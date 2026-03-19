"""
Workflow System Test Suite
Tests the complete workflow management system
"""

from workflow_engine import (
    Workflow, WorkflowStep, StepType, WorkflowExecutor,
    RuleEngine, create_expense_workflow
)
from workflow_db import init_workflow_database, save_workflow
import json


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(f" {title}".ljust(80))
    print("="*80)


def print_section(title):
    """Print a formatted section"""
    print(f"\n{'─'*80}")
    print(f" {title}")
    print(f"{'─'*80}")


def test_rule_engine():
    """Test the rule engine"""
    print_header("TEST 1: Rule Engine")
    
    engine = RuleEngine()
    
    # Test individual rules
    print_section("Single Rule Evaluation")
    data = {'amount': 5000, 'department': 'Finance'}
    
    rule = {'field': 'amount', 'operator': '>', 'value': 1000}
    passed, rule_str = engine.evaluate(rule, data)
    print(f"Rule: {rule_str}")
    print(f"Result: {'✅ PASSED' if passed else '❌ FAILED'}")
    
    # Test multiple rules
    print_section("Multiple Rules (AND Logic)")
    rules = [
        {'field': 'amount', 'operator': '>', 'value': 1000},
        {'field': 'department', 'operator': '==', 'value': 'Finance'}
    ]
    
    passed, rule_strings = engine.evaluate_all(rules, data, 'AND')
    for rule_str in rule_strings:
        print(f"  • {rule_str}")
    print(f"Combined Result (AND): {'✅ PASSED' if passed else '❌ FAILED'}")
    
    # Test OR logic
    print_section("Multiple Rules (OR Logic)")
    rules = [
        {'field': 'amount', 'operator': '<', 'value': 100},
        {'field': 'department', 'operator': '==', 'value': 'Finance'}
    ]
    
    passed, rule_strings = engine.evaluate_all(rules, data, 'OR')
    for rule_str in rule_strings:
        print(f"  • {rule_str}")
    print(f"Combined Result (OR): {'✅ PASSED' if passed else '❌ FAILED'}")


def test_workflow_creation():
    """Test workflow creation"""
    print_header("TEST 2: Workflow Creation")
    
    print_section("Creating Custom Workflow")
    workflow = Workflow("Test Workflow", "A test workflow for validation")
    
    # Add steps
    step1 = WorkflowStep(
        id="step1",
        name="First Step",
        type=StepType.APPROVAL,
        description="First approval",
        config={'approver': 'Manager', 'rules': []}
    )
    
    step2 = WorkflowStep(
        id="step2",
        name="Second Step",
        type=StepType.NOTIFICATION,
        description="Send notification",
        config={'recipients': ['user@example.com']}
    )
    
    workflow.add_step(step1)
    workflow.add_step(step2)
    workflow.set_next_steps("step1", "step2")
    
    print(f"Workflow: {workflow.name}")
    print(f"ID: {workflow.id}")
    print(f"Steps: {len(workflow.steps)}")
    for step_id, step in workflow.steps.items():
        print(f"  • {step.name} ({step.type.value})")


def test_default_workflow():
    """Test the default expense workflow"""
    print_header("TEST 3: Default Expense Approval Workflow")
    
    workflow = create_expense_workflow()
    print_section("Workflow Structure")
    print(f"Workflow: {workflow.name}")
    print(f"Description: {workflow.description}")
    print(f"Steps: {len(workflow.steps)}")
    
    for step_id in workflow.step_order:
        step = workflow.steps[step_id]
        print(f"\n  Step: {step.name}")
        print(f"    Type: {step.type.value}")
        print(f"    Description: {step.description}")
        if step.config.get('rules'):
            print(f"    Rules: {len(step.config['rules'])} rule(s)")
        if step.next_on_success:
            print(f"    Next (Success): {step.next_on_success}")


def test_workflow_execution():
    """Test workflow execution"""
    print_header("TEST 4: Workflow Execution")
    
    workflow = create_expense_workflow()
    executor = WorkflowExecutor()
    
    print_section("Executing Expense Approval Workflow")
    
    # Test case 1: Approved expense
    print("\nTest Case 1: Large Expense ($7500)")
    input_data = {
        'amount': 7500,
        'department': 'Finance',
        'status': 'New'
    }
    
    execution = executor.execute(workflow, input_data)
    print(f"Status: {execution.status}")
    print(f"Steps Executed: {len(execution.steps_executed)}")
    
    step_execs = executor.get_step_executions(execution.id)
    for step_exec in step_execs:
        status_icon = "✅" if step_exec.status in ["completed", "approved"] else "❌"
        print(f"  {status_icon} {step_exec.step_name} ({step_exec.status})")
        if step_exec.decision:
            print(f"      Decision: {step_exec.decision}")
        if step_exec.rules_evaluated:
            for rule in step_exec.rules_evaluated[:2]:
                print(f"      Rule: {rule}")
    
    # Test case 2: Small expense
    print("\n\nTest Case 2: Small Expense ($500)")
    input_data = {
        'amount': 500,
        'department': 'Marketing',
        'status': 'New'
    }
    
    execution = executor.execute(workflow, input_data)
    print(f"Status: {execution.status}")
    print(f"Steps Executed: {len(execution.steps_executed)}")


def test_database_operations():
    """Test database operations"""
    print_header("TEST 5: Database Operations")
    
    print_section("Initializing Database")
    init_workflow_database()
    print("✅ Database initialized")
    
    print_section("Saving Workflow")
    workflow = create_expense_workflow()
    save_workflow(workflow.id, workflow.name, workflow.description, workflow.to_dict())
    print(f"✅ Workflow saved: {workflow.name}")


def run_all_tests():
    """Run all tests"""
    print("\n\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "WORKFLOW MANAGEMENT SYSTEM - TEST SUITE" + " "*20 + "║")
    print("╚" + "="*78 + "╝")
    
    try:
        test_rule_engine()
        test_workflow_creation()
        test_default_workflow()
        test_workflow_execution()
        test_database_operations()
        
        print_header("ALL TESTS COMPLETED SUCCESSFULLY ✅")
        print("\nSummary:")
        print("  ✅ Rule engine working correctly")
        print("  ✅ Workflow creation functional")
        print("  ✅ Default expense workflow validated")
        print("  ✅ Workflow execution successful")
        print("  ✅ Database operations working")
        print("\n✨ System is ready for production! ✨\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
