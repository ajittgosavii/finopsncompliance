// api/mode/handler.js
// Production-grade backend API for Demo/Live mode management

const AWS = require('aws-sdk');
const crypto = require('crypto');

const dynamodb = new AWS.DynamoDB.DocumentClient();
const sns = new AWS.SNS();
const cloudwatch = new AWS.CloudWatch();

const MODE_CONFIG_TABLE = 'compliance_canvas_mode_config';
const AUDIT_LOG_TABLE = 'mode_switch_audit_log';

// Configuration
const APPROVAL_REQUIRED_ROLES = ['security_team', 'operations_team'];
const DEMO_TO_LIVE_REQUIRES_APPROVAL = true;
const LIVE_TO_DEMO_REQUIRES_APPROVAL = false;
const SESSION_TIMEOUT_MINUTES = 240; // 4 hours

/**
 * Get current mode for an organization
 */
async function getCurrentMode(req, res) {
  try {
    const { org_id } = req.query;

    if (!org_id) {
      return res.status(400).json({ 
        error: 'organization_id is required' 
      });
    }

    const result = await dynamodb.get({
      TableName: MODE_CONFIG_TABLE,
      Key: { organization_id: org_id }
    }).promise();

    if (!result.Item) {
      // Initialize with demo mode if not exists
      const defaultConfig = {
        organization_id: org_id,
        current_mode: 'demo',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        version: 1
      };

      await dynamodb.put({
        TableName: MODE_CONFIG_TABLE,
        Item: defaultConfig
      }).promise();

      return res.json({
        current_mode: 'demo',
        metadata: defaultConfig
      });
    }

    return res.json({
      current_mode: result.Item.current_mode,
      metadata: result.Item
    });
  } catch (error) {
    console.error('Error getting current mode:', error);
    return res.status(500).json({ 
      error: 'Failed to get current mode',
      message: error.message 
    });
  }
}

/**
 * Switch mode with approval workflow
 */
async function switchMode(req, res) {
  try {
    const {
      organization_id,
      target_mode,
      justification,
      mfa_code,
      user_id,
      user_email
    } = req.body;

    // Validation
    if (!organization_id || !target_mode || !user_id || !user_email) {
      return res.status(400).json({
        error: 'Missing required fields'
      });
    }

    if (!['demo', 'live'].includes(target_mode)) {
      return res.status(400).json({
        error: 'Invalid target_mode. Must be "demo" or "live"'
      });
    }

    // Get current mode
    const currentConfig = await dynamodb.get({
      TableName: MODE_CONFIG_TABLE,
      Key: { organization_id }
    }).promise();

    const currentMode = currentConfig.Item?.current_mode || 'demo';

    if (currentMode === target_mode) {
      return res.status(400).json({
        error: `Already in ${target_mode} mode`
      });
    }

    // Verify MFA
    const mfaValid = await verifyMFA(user_id, mfa_code);
    if (!mfaValid) {
      await logSecurityEvent({
        event: 'mfa_verification_failed',
        user_id,
        organization_id,
        severity: 'high'
      });
      return res.status(401).json({
        error: 'Invalid MFA code'
      });
    }

    // Check if approval is required
    const requiresApproval = 
      (currentMode === 'demo' && target_mode === 'live' && DEMO_TO_LIVE_REQUIRES_APPROVAL) ||
      (currentMode === 'live' && target_mode === 'demo' && LIVE_TO_DEMO_REQUIRES_APPROVAL);

    if (requiresApproval) {
      // Create approval request
      const requestId = crypto.randomUUID();
      const approvalRequest = {
        request_id: requestId,
        organization_id,
        from_mode: currentMode,
        to_mode: target_mode,
        requested_by: user_id,
        requested_by_email: user_email,
        justification,
        status: 'pending',
        created_at: new Date().toISOString(),
        required_approvers: APPROVAL_REQUIRED_ROLES,
        approvers: []
      };

      // Store approval request
      await dynamodb.put({
        TableName: 'mode_switch_approvals',
        Item: approvalRequest
      }).promise();

      // Send approval notifications
      await sendApprovalNotifications(approvalRequest);

      // Log audit event
      await logAuditEvent({
        event_type: 'mode_switch_requested',
        organization_id,
        from_mode: currentMode,
        to_mode: target_mode,
        user_id,
        user_email,
        request_id: requestId,
        status: 'pending_approval'
      });

      return res.json({
        status: 'pending_approval',
        request_id: requestId,
        approval_status: 'pending',
        message: 'Approval request sent to required teams'
      });
    } else {
      // Execute mode switch immediately
      await executeModeSwitch({
        organization_id,
        from_mode: currentMode,
        to_mode: target_mode,
        user_id,
        user_email,
        justification: justification || 'Switching to demo mode'
      });

      return res.json({
        status: 'completed',
        current_mode: target_mode,
        message: `Successfully switched to ${target_mode} mode`
      });
    }
  } catch (error) {
    console.error('Error switching mode:', error);
    return res.status(500).json({
      error: 'Failed to switch mode',
      message: error.message
    });
  }
}

/**
 * Execute the actual mode switch
 */
async function executeModeSwitch(params) {
  const {
    organization_id,
    from_mode,
    to_mode,
    user_id,
    user_email,
    justification,
    approvers = []
  } = params;

  // Calculate auto-revert time if switching to live
  const autoRevertAt = to_mode === 'live' 
    ? new Date(Date.now() + SESSION_TIMEOUT_MINUTES * 60000).toISOString()
    : null;

  // Update mode configuration
  const updatedConfig = {
    organization_id,
    current_mode: to_mode,
    last_switched_at: new Date().toISOString(),
    last_switched_by: user_id,
    last_switched_by_email: user_email,
    last_switched_from: from_mode,
    approval_status: approvers.length > 0 ? 'approved' : 'not_required',
    approvers,
    reason: justification,
    auto_revert_enabled: to_mode === 'live',
    auto_revert_at: autoRevertAt,
    updated_at: new Date().toISOString(),
    version: (await getCurrentVersion(organization_id)) + 1
  };

  await dynamodb.put({
    TableName: MODE_CONFIG_TABLE,
    Item: updatedConfig
  }).promise();

  // Schedule auto-revert if needed
  if (autoRevertAt) {
    await scheduleAutoRevert(organization_id, autoRevertAt);
  }

  // Log audit event
  await logAuditEvent({
    event_type: 'mode_switch_completed',
    organization_id,
    from_mode,
    to_mode,
    user_id,
    user_email,
    justification,
    approvers
  });

  // Publish CloudWatch metrics
  await publishModeSwitchMetrics(organization_id, from_mode, to_mode);

  // Send notifications
  await sendModeChangeNotifications({
    organization_id,
    from_mode,
    to_mode,
    user_email,
    auto_revert_at: autoRevertAt
  });

  return updatedConfig;
}

/**
 * Get approval status for a mode switch request
 */
async function getApprovalStatus(req, res) {
  try {
    const { request_id } = req.query;

    if (!request_id) {
      return res.status(400).json({ 
        error: 'request_id is required' 
      });
    }

    const result = await dynamodb.get({
      TableName: 'mode_switch_approvals',
      Key: { request_id }
    }).promise();

    if (!result.Item) {
      return res.status(404).json({ 
        error: 'Approval request not found' 
      });
    }

    return res.json({
      status: result.Item.status,
      approvers: result.Item.approvers,
      required_approvers: result.Item.required_approvers
    });
  } catch (error) {
    console.error('Error getting approval status:', error);
    return res.status(500).json({ 
      error: 'Failed to get approval status',
      message: error.message 
    });
  }
}

/**
 * Approve or reject a mode switch request
 */
async function handleApproval(req, res) {
  try {
    const {
      request_id,
      decision, // 'approved' or 'rejected'
      approver_id,
      approver_email,
      comments
    } = req.body;

    // Get approval request
    const result = await dynamodb.get({
      TableName: 'mode_switch_approvals',
      Key: { request_id }
    }).promise();

    if (!result.Item) {
      return res.status(404).json({ 
        error: 'Approval request not found' 
      });
    }

    const approvalRequest = result.Item;

    // Check if already approved/rejected
    if (approvalRequest.status !== 'pending') {
      return res.status(400).json({ 
        error: `Request already ${approvalRequest.status}` 
      });
    }

    // Add approver
    const approvers = approvalRequest.approvers || [];
    approvers.push({
      user_id: approver_id,
      email: approver_email,
      decision,
      decided_at: new Date().toISOString(),
      comments
    });

    // Check if all required approvals received
    const approvedCount = approvers.filter(a => a.decision === 'approved').length;
    const rejectedCount = approvers.filter(a => a.decision === 'rejected').length;

    let finalStatus = 'pending';
    if (rejectedCount > 0) {
      finalStatus = 'rejected';
    } else if (approvedCount >= approvalRequest.required_approvers.length) {
      finalStatus = 'approved';
    }

    // Update approval request
    await dynamodb.update({
      TableName: 'mode_switch_approvals',
      Key: { request_id },
      UpdateExpression: 'SET #status = :status, approvers = :approvers, updated_at = :updated_at',
      ExpressionAttributeNames: {
        '#status': 'status'
      },
      ExpressionAttributeValues: {
        ':status': finalStatus,
        ':approvers': approvers,
        ':updated_at': new Date().toISOString()
      }
    }).promise();

    // If approved, execute mode switch
    if (finalStatus === 'approved') {
      await executeModeSwitch({
        organization_id: approvalRequest.organization_id,
        from_mode: approvalRequest.from_mode,
        to_mode: approvalRequest.to_mode,
        user_id: approvalRequest.requested_by,
        user_email: approvalRequest.requested_by_email,
        justification: approvalRequest.justification,
        approvers
      });

      // Notify requester
      await sendNotification({
        to: approvalRequest.requested_by_email,
        subject: 'Mode Switch Request Approved',
        message: `Your request to switch to ${approvalRequest.to_mode} mode has been approved and executed.`
      });
    } else if (finalStatus === 'rejected') {
      // Notify requester
      await sendNotification({
        to: approvalRequest.requested_by_email,
        subject: 'Mode Switch Request Rejected',
        message: `Your request to switch to ${approvalRequest.to_mode} mode has been rejected.`
      });
    }

    return res.json({
      status: finalStatus,
      approvers
    });
  } catch (error) {
    console.error('Error handling approval:', error);
    return res.status(500).json({ 
      error: 'Failed to process approval',
      message: error.message 
    });
  }
}

/**
 * Emergency rollback to previous mode
 */
async function emergencyRollback(req, res) {
  try {
    const {
      organization_id,
      reason,
      user_id,
      user_email
    } = req.body;

    // Get current config
    const currentConfig = await dynamodb.get({
      TableName: MODE_CONFIG_TABLE,
      Key: { organization_id }
    }).promise();

    if (!currentConfig.Item) {
      return res.status(404).json({ 
        error: 'Organization config not found' 
      });
    }

    const previousMode = currentConfig.Item.last_switched_from || 'demo';
    const currentMode = currentConfig.Item.current_mode;

    // Execute rollback
    await executeModeSwitch({
      organization_id,
      from_mode: currentMode,
      to_mode: previousMode,
      user_id,
      user_email,
      justification: `EMERGENCY ROLLBACK: ${reason}`,
      approvers: [] // Emergency rollback bypasses approvals
    });

    // Send critical alert
    await sendEmergencyAlert({
      type: 'emergency_rollback',
      organization_id,
      from_mode: currentMode,
      to_mode: previousMode,
      reason,
      user_email
    });

    return res.json({
      status: 'completed',
      rolled_back_to: previousMode,
      message: 'Emergency rollback completed successfully'
    });
  } catch (error) {
    console.error('Error during emergency rollback:', error);
    return res.status(500).json({ 
      error: 'Failed to execute emergency rollback',
      message: error.message 
    });
  }
}

/**
 * Helper Functions
 */

async function verifyMFA(userId, mfaCode) {
  // Implement actual MFA verification logic
  // This is a placeholder
  return mfaCode && mfaCode.length === 6;
}

async function getCurrentVersion(organizationId) {
  const result = await dynamodb.get({
    TableName: MODE_CONFIG_TABLE,
    Key: { organization_id: organizationId }
  }).promise();
  
  return result.Item?.version || 0;
}

async function logAuditEvent(event) {
  const logItem = {
    log_id: `log-${Date.now()}-${crypto.randomBytes(6).toString('hex')}`,
    timestamp: new Date().toISOString(),
    ...event,
    request_metadata: {
      ip_address: event.ip_address || 'unknown',
      user_agent: event.user_agent || 'unknown'
    },
    ttl: Math.floor(Date.now() / 1000) + (365 * 24 * 60 * 60 * 7) // 7 years
  };

  await dynamodb.put({
    TableName: AUDIT_LOG_TABLE,
    Item: logItem
  }).promise();

  // Also log to CloudWatch
  console.log('AUDIT_EVENT:', JSON.stringify(logItem));
}

async function logSecurityEvent(event) {
  console.error('SECURITY_EVENT:', JSON.stringify(event));
  
  // Send to security monitoring system
  await sns.publish({
    TopicArn: process.env.SECURITY_ALERTS_TOPIC_ARN,
    Subject: `Security Event: ${event.event}`,
    Message: JSON.stringify(event, null, 2)
  }).promise();
}

async function publishModeSwitchMetrics(organizationId, fromMode, toMode) {
  await cloudwatch.putMetricData({
    Namespace: 'CloudComplianceCanvas/ModeManagement',
    MetricData: [
      {
        MetricName: 'ModeSwitches',
        Dimensions: [
          { Name: 'OrganizationId', Value: organizationId },
          { Name: 'FromMode', Value: fromMode },
          { Name: 'ToMode', Value: toMode }
        ],
        Value: 1,
        Unit: 'Count',
        Timestamp: new Date()
      },
      {
        MetricName: 'CurrentMode',
        Dimensions: [
          { Name: 'OrganizationId', Value: organizationId }
        ],
        Value: toMode === 'live' ? 1 : 0,
        Unit: 'None',
        Timestamp: new Date()
      }
    ]
  }).promise();
}

async function sendApprovalNotifications(approvalRequest) {
  const message = `
Mode Switch Approval Required

Organization: ${approvalRequest.organization_id}
Requested by: ${approvalRequest.requested_by_email}
From: ${approvalRequest.from_mode}
To: ${approvalRequest.to_mode}
Justification: ${approvalRequest.justification}
Request ID: ${approvalRequest.request_id}

Please review and approve/reject this request in the Cloud Compliance Canvas portal.
  `;

  for (const role of approvalRequest.required_approvers) {
    await sendNotification({
      to: `${role}@company.com`,
      subject: 'Mode Switch Approval Required',
      message
    });
  }
}

async function sendModeChangeNotifications(params) {
  const { organization_id, from_mode, to_mode, user_email, auto_revert_at } = params;
  
  const message = `
Mode switch completed for organization ${organization_id}

From: ${from_mode}
To: ${to_mode}
Switched by: ${user_email}
Time: ${new Date().toISOString()}
${auto_revert_at ? `Auto-revert scheduled for: ${auto_revert_at}` : ''}
  `;

  await sendNotification({
    to: 'compliance-team@company.com',
    subject: `Mode Switch: ${from_mode} → ${to_mode}`,
    message
  });
}

async function sendEmergencyAlert(params) {
  const message = `
🚨 EMERGENCY ROLLBACK EXECUTED 🚨

Organization: ${params.organization_id}
From: ${params.from_mode}
To: ${params.to_mode}
Reason: ${params.reason}
Executed by: ${params.user_email}
Time: ${new Date().toISOString()}

Immediate investigation required.
  `;

  await sns.publish({
    TopicArn: process.env.EMERGENCY_ALERTS_TOPIC_ARN,
    Subject: '🚨 EMERGENCY MODE ROLLBACK',
    Message: message
  }).promise();
}

async function sendNotification(params) {
  // Implement actual notification logic (email, Slack, etc.)
  console.log('NOTIFICATION:', params);
}

async function scheduleAutoRevert(organizationId, revertTime) {
  // Implement scheduling logic using EventBridge or similar
  console.log(`Scheduled auto-revert for ${organizationId} at ${revertTime}`);
}

module.exports = {
  getCurrentMode,
  switchMode,
  getApprovalStatus,
  handleApproval,
  emergencyRollback
};
