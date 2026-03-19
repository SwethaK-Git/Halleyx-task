# Comprehensive Workflow Management System

## Overview

This is a **Universal Workflow Management System** that allows you to:
- ✅ **Design workflows** with multiple steps and decision points
- ✅ **Define dynamic rules** that evaluate input data
- ✅ **Execute processes** with complex conditional logic
- ✅ **Track every step** with complete audit trails
- ✅ **Send notifications** at each workflow step
- ✅ **Manage approvals** with multi-level workflows
- ✅ **Make dynamic decisions** based on input data

## Key Features

### 🎨 Workflow Components
1. **Approval Steps** - Evaluate rules and make approval/rejection decisions
2. **Notification Steps** - Send notifications to stakeholders
3. **Task Steps** - Execute business logic
4. **Condition Steps** - Branch workflow based on conditions
5. **Wait Steps** - Pause execution (future enhancement)

### ⚡ Rule Engine
- Support for multiple operators: `==`, `!=`, `>`, `<`, `>=`, `<=`, `in`, `contains`, `startswith`
- AND/OR logic for combining multiple rules
- Dynamic field evaluation against input data

### 📊 Complete Tracking
- Workflow execution history
- Step-by-step execution logs
- Rule evaluation details
- Approval decision records
- Notification delivery logs
- Full audit trail with timestamps

## Default Workflow: Expense Approval

The system comes with a pre-built **Expense Approval Workflow**:

```
Expense Request
     ↓
Manager Approval (Rule-based)
     ↓
Finance Notification (Send email)
     ↓
CEO Approval (Rule-based)
     ↓
Task Completion (Mark as approved)
```

### Approval Rules Example:
- **Manager**: Approve if amount > $100 AND department != HR
- **CEO**: Approve if amount > $5000

## Getting Started

### 1. Install Flask
```powershell
pip install Flask==2.3.0
```

### 2. Run the Application
```powershell
python workflow_app.py
```

### 3. Open in Browser
Navigate to: **http://localhost:5000**

## File Structure

```
Halleyx/
├── workflow_engine.py        # Core workflow & rule engine
├── workflow_db.py            # Database operations
├── workflow_app.py           # Flask web application
├── workflow_execution.db     # Database file (auto-created)
└── templates/
    ├── workflow_index.html   # Home page
    ├── workflow_designer.html # Execute workflows
    ├── workflow_executions.html # View all executions
    └── workflow_detail.html   # Detailed execution view
```

## How It Works

### 1. Define a Workflow
```python
workflow = Workflow("Expense Approval", "Approve expenses")

# Add steps
manager_step = WorkflowStep(
    id="manager_approval",
    name="Manager Approval",
    type=StepType.APPROVAL,
    config={'rules': [...], 'approver': 'Manager'}
)
workflow.add_step(manager_step)

# Connect steps
workflow.set_next_steps("manager_approval", "finance_notification", None)
```

### 2. Execute the Workflow
```python
executor = WorkflowExecutor()
execution = executor.execute(workflow, {
    'amount': 5000,
    'department': 'Finance'
})
```

### 3. Track Execution
- View all steps executed
- See all decisions made
- Check notifications sent
- Review approvals recorded

## API Endpoints

### Workflows
- `GET /api/workflows` - Get all workflow definitions
- `GET /api/workflow/<id>` - Get specific workflow
- `POST /api/workflow` - Create new workflow
- `GET /api/default-workflow` - Get expense approval workflow

### Executions
- `POST /api/workflow/execute` - Execute a workflow
- `GET /api/execution/<id>` - Get execution details
- `GET /api/executions` - Get all executions

### Database Queries
- Get step executions
- Get notifications
- Get approvals
- Full audit trail

## Example: Execute Expense Approval

**Request:**
```json
POST /api/workflow/execute

{
  "workflow_id": "workflow-id",
  "input_data": {
    "amount": 5000,
    "department": "Finance",
    "status": "New"
  }
}
```

**Response:**
```json
{
  "success": true,
  "execution_id": "exec-abc123",
  "status": "completed",
  "steps_executed": 4,
  "final_status": "APPROVED"
}
```

## Database Schema

### workflows
- `id` - Unique workflow ID
- `name` - Workflow name
- `description` - Workflow description
- `workflow_json` - Complete workflow definition

### workflow_executions
- `id` - Execution ID
- `workflow_id` - Reference to workflow
- `status` - completed, running, etc.
- `input_data` - Input parameters
- `started_at`, `completed_at` - Timestamps

### step_executions
- `id` - Step execution ID
- `step_id` - Step identifier
- `status` - pending, completed, approved, rejected
- `rules_evaluated` - All evaluated rules
- `decision` - Approval decision

### notifications
- `recipient` - Email/contact
- `message` - Notification message
- `status` - sent, failed

### approvals_log
- `approver` - Who approved
- `decision` - APPROVED/REJECTED
- `comments` - Decision comments

## Rule Evaluation Examples

### Example 1: Simple Rule
```python
rule = {'field': 'amount', 'operator': '>', 'value': 5000}
# Evaluates: amount > 5000
```

### Example 2: Multiple Rules (AND)
```python
rules = [
    {'field': 'amount', 'operator': '>', 'value': 1000},
    {'field': 'department', 'operator': '!=', 'value': 'HR'}
]
# Evaluates: (amount > 1000) AND (department != HR)
```

### Example 3: Multiple Rules (OR)
```python
rules = [
    {'field': 'priority', 'operator': '==', 'value': 'High'},
    {'field': 'status', 'operator': '==', 'value': 'Urgent'}
]
# Evaluates: (priority == High) OR (status == Urgent)
```

## Customization

### Add New Approval Rules
Edit `workflow_engine.py` → `_execute_approval()` method

### Add New Step Types
1. Add to `StepType` enum
2. Add `_execute_<type>()` method in `WorkflowExecutor`
3. Implement step logic

### Add Notifications
Modify `_execute_notification()` to integrate with email service

### Add Conditions
Create complex decision logic in `_execute_condition()`

## Testing

### Test with Default Workflow
1. Go to http://localhost:5000/designer
2. Fill in form:
   - Amount: 5000
   - Department: Finance
   - Status: New
3. Click "Execute Workflow"
4. View results

### Test Different Scenarios
- Small amount: $100 (Manager approval only)
- Large amount: $10000 (Full escalation)
- HR department: (Auto-rejection)

## Troubleshooting

### Database Errors
Delete `workflow_execution.db` and restart - database auto-initializes

### Port Already in Use
Change port in `workflow_app.py`:
```python
app.run(debug=True, port=5001)
```

### Template Not Found
Ensure `templates/` directory has all 4 HTML files

## Future Enhancements

- 🔐 User authentication & role-based access
- 📧 Email integration for notifications
- ⏲️ Scheduled workflows
- 🔄 Workflow versioning
- 📊 Analytics dashboard
- 🎯 Custom step types
- 💾 Workflow templates
- 🔌 API integrations

---

**Status**: Ready for Production ✅
**Last Updated**: March 2026
