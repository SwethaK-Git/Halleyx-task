"""
Universal Workflow Management Web Application
Allows creating, executing, and tracking any workflow
"""

from flask import Flask, render_template, request, jsonify, redirect
from workflow_engine import (
    Workflow, WorkflowStep, StepType, WorkflowExecutor, 
    create_expense_workflow
)
from workflow_db import (
    init_workflow_database, save_workflow, get_workflow, get_all_workflows,
    save_execution, get_execution, get_all_executions,
    save_step_execution, get_step_executions,
    save_notification, get_notifications,
    save_approval_record, get_approvals
)
from datetime import datetime
import json

app = Flask(__name__)
executor = WorkflowExecutor()

# Initialize database on startup
init_workflow_database()

# Create default expense workflow
default_workflow = create_expense_workflow()
save_workflow(default_workflow.id, default_workflow.name, default_workflow.description, 
              default_workflow.to_dict())


@app.route('/')
def index():
    """Home page"""
    return render_template('workflow_index.html')


@app.route('/designer')
def designer():
    """Workflow designer page"""
    return render_template('workflow_designer.html')


@app.route('/custom-designer')
def custom_designer():
    """Custom workflow designer page"""
    return render_template('custom_workflow_designer.html')


@app.route('/universal-designer')
def universal_designer():
    """Universal workflow designer - for ANY approval type"""
    return render_template('universal_designer.html')


@app.route('/executions')
def executions():
    """View all workflow executions"""
    executions_list = get_all_executions()
    return render_template('workflow_executions.html', executions=executions_list)


@app.route('/execution/<execution_id>')
def execution_detail(execution_id):
    """View detailed execution"""
    execution = get_execution(execution_id)
    if not execution:
        return redirect('/executions')
    
    steps = get_step_executions(execution_id)
    notifications = get_notifications(execution_id)
    approvals = get_approvals(execution_id)
    
    return render_template('workflow_detail.html', 
                          execution=execution,
                          steps=steps,
                          notifications=notifications,
                          approvals=approvals)


# API Routes

@app.route('/api/workflows', methods=['GET'])
def api_get_workflows():
    """Get all workflow definitions"""
    workflows = get_all_workflows()
    return jsonify(workflows), 200


@app.route('/api/workflow/<workflow_id>', methods=['GET'])
def api_get_workflow(workflow_id):
    """Get specific workflow"""
    workflow = get_workflow(workflow_id)
    if not workflow:
        return jsonify({"error": "Workflow not found"}), 404
    return jsonify(workflow), 200


@app.route('/api/workflow', methods=['POST'])
def api_create_workflow():
    """Create a new workflow"""
    try:
        data = request.json
        
        workflow = Workflow(data['name'], data.get('description', ''))
        
        # Add steps from request
        for step_data in data.get('steps', []):
            step = WorkflowStep(
                id=step_data['id'],
                name=step_data['name'],
                type=StepType[step_data['type'].upper()],
                description=step_data.get('description', ''),
                config=step_data.get('config', {})
            )
            workflow.add_step(step)
        
        # Set connections
        for connection in data.get('connections', []):
            workflow.set_next_steps(
                connection['from_step'],
                connection.get('on_success'),
                connection.get('on_failure')
            )
        
        # Save to database
        save_workflow(workflow.id, workflow.name, workflow.description, workflow.to_dict())
        
        return jsonify({
            "success": True,
            "workflow_id": workflow.id,
            "message": f"Workflow '{workflow.name}' created successfully"
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/workflow/execute', methods=['POST'])
def api_execute_workflow():
    """Execute a workflow"""
    try:
        data = request.json
        workflow_id = data.get('workflow_id')
        input_data = data.get('input_data', {})
        
        # Get workflow definition
        workflow_def = get_workflow(workflow_id)
        if not workflow_def:
            return jsonify({"error": "Workflow not found"}), 404
        
        # Reconstruct workflow object
        workflow = Workflow(workflow_def['name'], workflow_def['description'])
        
        # Rebuild steps
        for step_id, step_data in workflow_def['workflow_json']['steps'].items():
            step = WorkflowStep(
                id=step_data['id'],
                name=step_data['name'],
                type=StepType[step_data['type'].upper()],
                description=step_data['description'],
                config=step_data['config'],
                next_on_success=step_data.get('next_on_success'),
                next_on_failure=step_data.get('next_on_failure')
            )
            workflow.add_step(step)
        
        # Execute workflow
        execution = executor.execute(workflow, input_data)
        
        # Save execution and steps to database
        save_execution(
            execution.id,
            workflow_id,
            execution.workflow_name,
            execution.status,
            execution.input_data,
            execution.current_step,
            execution.started_at.isoformat(),
            execution.completed_at.isoformat() if execution.completed_at else None
        )
        
        # Save step executions
        step_execs = executor.get_step_executions(execution.id)
        for step_exec in step_execs:
            save_step_execution(
                step_exec.step_id,
                execution.id,
                step_exec.step_name,
                step_exec.step_type,
                step_exec.status,
                step_exec.input_data,
                step_exec.output_data,
                step_exec.rules_evaluated,
                step_exec.decision,
                step_exec.started_at.isoformat(),
                step_exec.completed_at.isoformat()
            )
            
            # Save notifications if it's a notification step
            if step_exec.step_type == 'notification':
                for recipient in step_exec.output_data.get('recipients', []):
                    save_notification(
                        execution.id,
                        step_exec.step_id,
                        recipient,
                        step_exec.output_data.get('message', ''),
                        'sent'
                    )
            
            # Save approvals if it's an approval step
            if step_exec.step_type == 'approval':
                save_approval_record(
                    execution.id,
                    step_exec.step_id,
                    step_exec.output_data.get('approver', 'System'),
                    step_exec.decision,
                    f"Rules evaluated: {len(step_exec.rules_evaluated)}"
                )
        
        return jsonify({
            "success": True,
            "execution_id": execution.id,
            "status": execution.status,
            "message": "Workflow executed successfully",
            "steps_executed": len(step_execs),
            "final_status": "COMPLETED"
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/execution/<execution_id>', methods=['GET'])
def api_get_execution(execution_id):
    """Get execution details"""
    execution = get_execution(execution_id)
    if not execution:
        return jsonify({"error": "Execution not found"}), 404
    
    steps = get_step_executions(execution_id)
    notifications = get_notifications(execution_id)
    approvals = get_approvals(execution_id)
    
    return jsonify({
        "execution": execution,
        "steps": steps,
        "notifications": notifications,
        "approvals": approvals
    }), 200


@app.route('/api/executions', methods=['GET'])
def api_get_all_executions():
    """Get all executions"""
    executions = get_all_executions()
    return jsonify(executions), 200


@app.route('/api/default-workflow', methods=['GET'])
def api_get_default_workflow():
    """Get the default expense approval workflow"""
    return jsonify(default_workflow.to_dict()), 200


@app.route('/api/custom-workflow/create', methods=['POST'])
def api_create_custom_workflow():
    """Create a custom workflow based on user-defined rules"""
    try:
        data = request.json
        
        # Extract thresholds from request
        # Format: [{amount: 600, approvers: ['manager']}, {amount: 5000, approvers: ['manager', 'ceo']}]
        thresholds = data.get('thresholds', [])
        workflow_name = data.get('workflow_name', 'Custom Approval Workflow')
        
        # Sort thresholds by amount ascending
        thresholds = sorted(thresholds, key=lambda x: x['amount'])
        
        # Create workflow
        workflow = Workflow(workflow_name, f"Custom workflow with {len(thresholds)} approval thresholds")
        
        # Add first approval step (always manager)
        manager_approval = WorkflowStep(
            id='manager-approval',
            name='Manager Approval',
            type=StepType.APPROVAL,
            description='Manager approval for expenses',
            config={
                'approver': 'Manager',
                'rules': [
                    {'field': 'amount', 'operator': '>', 'value': thresholds[0]['amount'] - 1}
                ]
            }
        )
        workflow.add_step(manager_approval)
        
        # Add notification step
        notification = WorkflowStep(
            id='notification',
            name='Notification',
            type=StepType.NOTIFICATION,
            description='Notify stakeholders about approval request',
            config={'message': f'Approval request for amount: {{amount}}'}
        )
        workflow.add_step(notification)
        workflow.set_next_steps('manager-approval', 'notification', None)
        
        # Add CEO/other approvers based on thresholds
        for i, threshold in enumerate(thresholds[1:]):
            for approver in threshold['approvers']:
                if approver.lower() != 'manager':  # Skip manager, already added
                    step_id = f'{approver.lower()}-approval'
                    if not any(s.id == step_id for s in workflow.steps.values()):
                        approval_step = WorkflowStep(
                            id=step_id,
                            name=f'{approver} Approval',
                            type=StepType.APPROVAL,
                            description=f'{approver} approval for high-value requests',
                            config={
                                'approver': approver,
                                'rules': [
                                    {'field': 'amount', 'operator': '>', 'value': threshold['amount']}
                                ]
                            }
                        )
                        workflow.add_step(approval_step)
                        workflow.set_next_steps('notification', step_id, None)
        
        # Add final task
        task = WorkflowStep(
            id='completion',
            name='Task Completion',
            type=StepType.TASK,
            description='Mark request as completed and process',
            config={'action': 'Mark as approved and process'}
        )
        workflow.add_step(task)
        
        # Connect last approval to task
        last_approver = thresholds[-1]['approvers'][-1].lower()
        workflow.set_next_steps(f'{last_approver}-approval', 'completion', None)
        
        # Save workflow to database
        save_workflow(workflow.id, workflow.name, workflow.description, workflow.to_dict())
        
        return jsonify({
            "success": True,
            "workflow_id": workflow.id,
            "workflow_name": workflow.name,
            "message": "Custom workflow created successfully!",
            "thresholds": thresholds,
            "steps": list(workflow.steps.keys())
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/custom-workflow/execute', methods=['POST'])
def api_execute_custom_workflow():
    """Execute a custom workflow with input data"""
    try:
        data = request.json
        workflow_id = data.get('workflow_id')
        input_data = data.get('input_data', {})
        
        # Get workflow definition
        workflow_def = get_workflow(workflow_id)
        if not workflow_def:
            return jsonify({"error": "Workflow not found"}), 404
        
        # Reconstruct workflow object
        workflow = Workflow(workflow_def['name'], workflow_def['description'])
        
        # Rebuild steps
        for step_id, step_data in workflow_def['workflow_json']['steps'].items():
            step = WorkflowStep(
                id=step_data['id'],
                name=step_data['name'],
                type=StepType[step_data['type'].upper()],
                description=step_data['description'],
                config=step_data['config'],
                next_on_success=step_data.get('next_on_success'),
                next_on_failure=step_data.get('next_on_failure')
            )
            workflow.add_step(step)
        
        # Execute workflow
        execution = executor.execute(workflow, input_data)
        
        # Save execution and steps to database
        save_execution(
            execution.id,
            workflow_id,
            execution.workflow_name,
            execution.status,
            execution.input_data,
            execution.current_step,
            execution.started_at.isoformat(),
            execution.completed_at.isoformat() if execution.completed_at else None
        )
        
        # Save step executions
        step_execs = executor.get_step_executions(execution.id)
        for step_exec in step_execs:
            save_step_execution(
                step_exec.step_id,
                execution.id,
                step_exec.step_name,
                step_exec.step_type,
                step_exec.status,
                step_exec.input_data,
                step_exec.output_data,
                step_exec.rules_evaluated,
                step_exec.decision,
                step_exec.started_at.isoformat(),
                step_exec.completed_at.isoformat()
            )
        
        return jsonify({
            "success": True,
            "execution_id": execution.id,
            "status": execution.status,
            "message": "Workflow executed successfully",
            "steps_executed": len(step_execs),
            "details": {
                "workflow_name": execution.workflow_name,
                "input_data": execution.input_data,
                "steps": [
                    {
                        "step_name": s.step_name,
                        "status": s.status,
                        "decision": s.decision,
                        "rules": s.rules_evaluated
                    }
                    for s in step_execs
                ]
            }
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Universal Workflow API Endpoints
@app.route('/api/universal-workflow/create', methods=['POST'])
def api_create_universal_workflow():
    """Create a universal workflow for ANY approval type"""
    try:
        data = request.json
        
        workflow_name = data.get('workflow_name', 'Universal Workflow')
        workflow_description = data.get('workflow_description', '')
        fields = data.get('fields', [])
        rules = data.get('rules', [])
        
        if not rules:
            return jsonify({"error": "Please add at least one approval rule"}), 400
        
        # Create workflow
        workflow = Workflow(workflow_name, workflow_description)
        
        # Add approval step for each rule
        for idx, rule in enumerate(rules):
            step_id = f'approval_{idx}'
            approvers = rule.get('approvers', ['Manager'])
            
            step = WorkflowStep(
                id=step_id,
                name=f"Rule {idx + 1}: {rule.get('field')} {rule.get('operator')} {rule.get('value')}",
                type=StepType.APPROVAL,
                description=f"Approval required when {rule.get('field')} {rule.get('operator')} {rule.get('value')}",
                config={
                    'approvers': approvers,
                    'rules': [{
                        'field': rule.get('field'),
                        'operator': rule.get('operator'),
                        'value': rule.get('value')
                    }]
                }
            )
            workflow.add_step(step)
            
            # Link rules sequentially
            if idx > 0:
                workflow.set_next_steps(f'approval_{idx-1}', step_id, None)
        
        # Add notification step
        notification = WorkflowStep(
            id='notification',
            name='Notify Stakeholders',
            type=StepType.NOTIFICATION,
            description='Send notification about approval decision',
            config={'message': 'Approval request has been processed'}
        )
        workflow.add_step(notification)
        
        # Link last approval to notification
        if rules:
            workflow.set_next_steps(f'approval_{len(rules)-1}', 'notification', None)
        
        # Add completion step
        completion = WorkflowStep(
            id='completion',
            name='Mark Complete',
            type=StepType.TASK,
            description='Mark approval request as complete',
            config={'action': 'Mark request as complete'}
        )
        workflow.add_step(completion)
        workflow.set_next_steps('notification', 'completion', None)
        
        # Save workflow to database
        save_workflow(workflow.id, workflow.name, workflow.description, workflow.to_dict())
        
        return jsonify({
            "success": True,
            "workflow_id": workflow.id,
            "workflow_name": workflow.name,
            "message": f"Universal workflow '{workflow_name}' created successfully!",
            "rules_count": len(rules),
            "approvers": list(set([app for rule in rules for app in rule.get('approvers', [])]))
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e), "details": str(type(e))}), 400


@app.route('/api/universal-workflow/execute', methods=['POST'])
def api_execute_universal_workflow():
    """Execute a universal workflow with test data"""
    try:
        data = request.json
        workflow_id = data.get('workflow_id')
        input_data = data.get('input_data', {})
        
        # Get workflow definition
        workflow_def = get_workflow(workflow_id)
        if not workflow_def:
            return jsonify({"error": "Workflow not found"}), 404
        
        # Validate input data has required fields
        required_fields = []
        for step_id, step_data in workflow_def['workflow_json']['steps'].items():
            if step_data.get('type') == 'approval':
                rules = step_data.get('config', {}).get('rules', [])
                for rule in rules:
                    field = rule.get('field')
                    if field:
                        required_fields.append(field)
        
        # Check for missing fields
        missing_fields = [f for f in set(required_fields) if f not in input_data]
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "required_fields": required_fields,
                "input_received": list(input_data.keys())
            }), 400
        
        # Reconstruct workflow object
        workflow = Workflow(workflow_def['name'], workflow_def['description'])
        workflow.id = workflow_def['id']
        
        # Rebuild steps
        for step_id, step_data in workflow_def['workflow_json']['steps'].items():
            step = WorkflowStep(
                id=step_data['id'],
                name=step_data['name'],
                type=StepType[step_data['type'].upper()],
                description=step_data['description'],
                config=step_data['config'],
                next_on_success=step_data.get('next_on_success'),
                next_on_failure=step_data.get('next_on_failure')
            )
            workflow.add_step(step)
        
        # Execute workflow
        execution = executor.execute(workflow, input_data)
        
        # Save execution and steps to database
        save_execution(
            execution.id,
            workflow_id,
            execution.workflow_name,
            execution.status,
            execution.input_data,
            execution.current_step,
            execution.started_at.isoformat(),
            execution.completed_at.isoformat() if execution.completed_at else None
        )
        
        # Save step executions
        step_execs = executor.get_step_executions(execution.id)
        for step_exec in step_execs:
            save_step_execution(
                step_exec.step_id,
                execution.id,
                step_exec.step_name,
                step_exec.step_type,
                step_exec.status,
                step_exec.input_data,
                step_exec.output_data,
                step_exec.rules_evaluated,
                step_exec.decision,
                step_exec.started_at.isoformat(),
                step_exec.completed_at.isoformat()
            )
        
        return jsonify({
            "success": True,
            "execution_id": execution.id,
            "status": execution.status,
            "message": "Workflow executed successfully",
            "steps_executed": len(step_execs),
            "details": {
                "workflow_name": execution.workflow_name,
                "input_data": execution.input_data,
                "steps": [
                    {
                        "step_name": s.step_name,
                        "status": s.status,
                        "decision": s.decision,
                        "rules": s.rules_evaluated
                    }
                    for s in step_execs
                ]
            }
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e), "details": str(type(e))}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
