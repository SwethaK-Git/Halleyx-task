"""
Universal Workflow Management System
Allows creating, executing, and tracking any workflow with dynamic rules
"""

import json
from enum import Enum
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, asdict
import uuid


class StepType(Enum):
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    TASK = "task"
    CONDITION = "condition"
    WAIT = "wait"


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"


@dataclass
class WorkflowStep:
    """Represents a single step in the workflow"""
    id: str
    name: str
    type: StepType
    description: str
    config: Dict[str, Any]  # Step-specific configuration
    next_on_success: Optional[str] = None
    next_on_failure: Optional[str] = None
    order: int = 0


@dataclass
class WorkflowExecution:
    """Tracks workflow execution"""
    id: str
    workflow_name: str
    status: str
    input_data: Dict[str, Any]
    current_step: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    steps_executed: List[str] = None
    
    def __post_init__(self):
        if self.steps_executed is None:
            self.steps_executed = []


@dataclass
class StepExecution:
    """Tracks individual step execution"""
    step_id: str
    workflow_execution_id: str
    step_name: str
    step_type: str
    status: str  # pending, running, completed, failed, approved, rejected
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    rules_evaluated: List[str]
    decision: Optional[str] = None
    started_at: datetime = None
    completed_at: datetime = None
    
    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.now()
        if self.rules_evaluated is None:
            self.rules_evaluated = []


class RuleEngine:
    """Evaluates conditions and rules for workflow steps"""
    
    def __init__(self):
        self.operators = {
            '==': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            'in': lambda a, b: a in b,
            'contains': lambda a, b: b in a,
            'startswith': lambda a, b: a.startswith(b) if isinstance(a, str) else False,
        }
    
    def evaluate(self, rule: Dict[str, Any], data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Evaluate a rule against data
        Rule format: {
            "field": "amount",
            "operator": ">",
            "value": 1000
        }
        """
        field = rule.get('field')
        operator = rule.get('operator')
        value = rule.get('value')
        
        field_value = data.get(field)
        
        # Check if required field is missing
        if field_value is None:
            return False, f"❌ {field} is missing from input data"
        
        if operator not in self.operators:
            return False, f"Unknown operator: {operator}"
        
        try:
            result = self.operators[operator](field_value, value)
            rule_str = f"{field} {operator} {value} = {result} ✓"
            return result, rule_str
        except Exception as e:
            return False, f"Error evaluating {field} {operator} {value}: {str(e)}"
    
    def evaluate_all(self, rules: List[Dict[str, Any]], data: Dict[str, Any], 
                     logic: str = "AND") -> tuple[bool, List[str]]:
        """
        Evaluate multiple rules with AND or OR logic
        """
        results = []
        rule_strings = []
        
        for rule in rules:
            passed, rule_str = self.evaluate(rule, data)
            results.append(passed)
            rule_strings.append(rule_str)
        
        if logic == "AND":
            final_result = all(results)
        else:  # OR
            final_result = any(results)
        
        return final_result, rule_strings


class Workflow:
    """Represents a complete workflow"""
    
    def __init__(self, name: str, description: str = ""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.steps: Dict[str, WorkflowStep] = {}
        self.step_order = []
        self.rule_engine = RuleEngine()
        self.created_at = datetime.now()
    
    def add_step(self, step: WorkflowStep) -> 'Workflow':
        """Add a step to the workflow"""
        self.steps[step.id] = step
        self.step_order.append(step.id)
        return self
    
    def set_next_steps(self, step_id: str, on_success: Optional[str] = None, 
                       on_failure: Optional[str] = None) -> 'Workflow':
        """Set the next step based on success/failure"""
        if step_id in self.steps:
            self.steps[step_id].next_on_success = on_success
            self.steps[step_id].next_on_failure = on_failure
        return self
    
    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get a step by ID"""
        return self.steps.get(step_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'steps': {k: {
                'id': v.id,
                'name': v.name,
                'type': v.type.value,
                'description': v.description,
                'config': v.config,
                'next_on_success': v.next_on_success,
                'next_on_failure': v.next_on_failure
            } for k, v in self.steps.items()},
            'step_order': self.step_order,
            'created_at': self.created_at.isoformat()
        }


class WorkflowExecutor:
    """Executes workflows step by step"""
    
    def __init__(self):
        self.executions: Dict[str, WorkflowExecution] = {}
        self.step_executions: Dict[str, List[StepExecution]] = {}
        self.rule_engine = RuleEngine()
    
    def execute(self, workflow: Workflow, input_data: Dict[str, Any]) -> WorkflowExecution:
        """Execute a workflow with given input data"""
        execution = WorkflowExecution(
            id=str(uuid.uuid4()),
            workflow_name=workflow.name,
            status="running",
            input_data=input_data,
            current_step=workflow.step_order[0] if workflow.step_order else None,
            started_at=datetime.now(),
            steps_executed=[]
        )
        
        self.executions[execution.id] = execution
        self.step_executions[execution.id] = []
        
        # Execute workflow step by step
        current_step_id = workflow.step_order[0] if workflow.step_order else None
        
        while current_step_id:
            step = workflow.get_step(current_step_id)
            if not step:
                break
            
            step_exec = self._execute_step(step, input_data, execution.id)
            self.step_executions[execution.id].append(step_exec)
            execution.steps_executed.append(current_step_id)
            
            # Determine next step based on result
            if step_exec.status == "approved" or step_exec.status == "completed":
                current_step_id = step.next_on_success
            else:
                current_step_id = step.next_on_failure
        
        execution.completed_at = datetime.now()
        execution.status = "completed"
        execution.current_step = current_step_id
        
        return execution
    
    def _execute_step(self, step: WorkflowStep, data: Dict[str, Any], execution_id: str = "") -> StepExecution:
        """Execute a single workflow step"""
        step_exec = StepExecution(
            step_id=step.id,
            workflow_execution_id=execution_id,
            step_name=step.name,
            step_type=step.type.value,
            status="running",
            input_data=data,
            output_data={},
            rules_evaluated=[]
        )
        
        if step.type == StepType.APPROVAL:
            step_exec = self._execute_approval(step, data, step_exec)
        elif step.type == StepType.NOTIFICATION:
            step_exec = self._execute_notification(step, data, step_exec)
        elif step.type == StepType.TASK:
            step_exec = self._execute_task(step, data, step_exec)
        elif step.type == StepType.CONDITION:
            step_exec = self._execute_condition(step, data, step_exec)
        
        step_exec.completed_at = datetime.now()
        return step_exec
    
    def _execute_approval(self, step: WorkflowStep, data: Dict[str, Any], 
                         exec_obj: StepExecution) -> StepExecution:
        """Execute approval step"""
        rules = step.config.get('rules', [])
        approver = step.config.get('approver', 'System')
        
        if rules:
            passed, rule_strings = self.rule_engine.evaluate_all(
                rules, 
                data, 
                step.config.get('logic', 'AND')
            )
            exec_obj.rules_evaluated = rule_strings
        else:
            passed = True
        
        exec_obj.status = "approved" if passed else "rejected"
        exec_obj.decision = "APPROVED" if passed else "REJECTED"
        exec_obj.output_data = {
            'approver': approver,
            'decision': exec_obj.decision,
            'rules_evaluated': exec_obj.rules_evaluated
        }
        
        return exec_obj
    
    def _execute_notification(self, step: WorkflowStep, data: Dict[str, Any],
                             exec_obj: StepExecution) -> StepExecution:
        """Execute notification step"""
        recipients = step.config.get('recipients', [])
        message_template = step.config.get('message', '')
        
        # Simulate notification
        message = message_template.format(**data)
        
        exec_obj.status = "completed"
        exec_obj.output_data = {
            'recipients': recipients,
            'message': message,
            'sent': True
        }
        
        return exec_obj
    
    def _execute_task(self, step: WorkflowStep, data: Dict[str, Any],
                     exec_obj: StepExecution) -> StepExecution:
        """Execute task step"""
        task_type = step.config.get('task_type', 'generic')
        task_action = step.config.get('action', '')
        
        exec_obj.status = "completed"
        exec_obj.output_data = {
            'task_type': task_type,
            'action': task_action,
            'completed_at': datetime.now().isoformat()
        }
        
        return exec_obj
    
    def _execute_condition(self, step: WorkflowStep, data: Dict[str, Any],
                          exec_obj: StepExecution) -> StepExecution:
        """Execute condition/decision step"""
        rules = step.config.get('rules', [])
        
        if rules:
            passed, rule_strings = self.rule_engine.evaluate_all(
                rules,
                data,
                step.config.get('logic', 'AND')
            )
            exec_obj.rules_evaluated = rule_strings
        else:
            passed = True
        
        exec_obj.status = "completed"
        exec_obj.decision = "YES" if passed else "NO"
        exec_obj.output_data = {
            'condition_result': passed,
            'rules_evaluated': exec_obj.rules_evaluated
        }
        
        return exec_obj
    
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution details"""
        return self.executions.get(execution_id)
    
    def get_step_executions(self, execution_id: str) -> List[StepExecution]:
        """Get all step executions for a workflow"""
        return self.step_executions.get(execution_id, [])


# Example: Build Expense Approval Workflow
def create_expense_workflow() -> Workflow:
    """Create the default expense approval workflow"""
    workflow = Workflow("Expense Approval", "Standard expense approval process")
    
    # Step 1: Manager Approval
    manager_step = WorkflowStep(
        id="manager_approval",
        name="Manager Approval",
        type=StepType.APPROVAL,
        description="Manager reviews and approves expense",
        config={
            'approver': 'Manager',
            'rules': [
                {'field': 'amount', 'operator': '>', 'value': 0}
            ]
        }
    )
    workflow.add_step(manager_step)
    
    # Step 2: Finance Notification
    finance_step = WorkflowStep(
        id="finance_notification",
        name="Finance Notification",
        type=StepType.NOTIFICATION,
        description="Notify Finance team",
        config={
            'recipients': ['finance@company.com'],
            'message': 'Expense of ${amount} from {department} approved for processing'
        }
    )
    workflow.add_step(finance_step)
    
    # Step 3: CEO Approval
    ceo_step = WorkflowStep(
        id="ceo_approval",
        name="CEO Approval",
        type=StepType.APPROVAL,
        description="CEO approves large expenses",
        config={
            'approver': 'CEO',
            'rules': [
                {'field': 'amount', 'operator': '>', 'value': 5000}
            ]
        }
    )
    workflow.add_step(ceo_step)
    
    # Step 4: Task Completion
    task_step = WorkflowStep(
        id="task_completion",
        name="Task Completion",
        type=StepType.TASK,
        description="Mark expense as approved",
        config={
            'task_type': 'mark_approved',
            'action': 'Update expense status to APPROVED'
        }
    )
    workflow.add_step(task_step)
    
    # Set workflow flow
    workflow.set_next_steps("manager_approval", "finance_notification", None)
    workflow.set_next_steps("finance_notification", "ceo_approval", None)
    workflow.set_next_steps("ceo_approval", "task_completion", None)
    
    return workflow
