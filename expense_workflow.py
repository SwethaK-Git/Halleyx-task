"""
Expense Approval Workflow Simulation
A step-by-step simulation of a multi-step approval workflow
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple


class Priority(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class StepStatus(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    NOTIFIED = "notified"


@dataclass
class ExpenseRequest:
    amount: float
    country: str
    department: str
    priority: Priority


@dataclass
class StepLog:
    step_name: str
    rules_evaluated: List[str]
    status: str
    next_step: str
    details: str = ""


class WorkflowEngine:
    def __init__(self, expense: ExpenseRequest):
        self.expense = expense
        self.logs: List[StepLog] = []
        self.current_step = "Manager Approval"
        self.workflow_completed = False
        self.final_status = None

    def evaluate_manager_approval(self) -> Tuple[bool, List[str]]:
        """
        Manager Approval Rules:
        a) amount > 100 && country == 'US' && priority == 'High' → approve
        b) amount <= 100 || department == 'HR' → reject
        """
        rules_evaluated = []
        
        # Rule a: High value US expenses with High priority
        rule_a = (
            self.expense.amount > 100 and
            self.expense.country == "US" and
            self.expense.priority == Priority.HIGH
        )
        rules_evaluated.append(
            f"Rule a (Auto-approve): amount > 100 ({self.expense.amount > 100}) "
            f"AND country == 'US' ({self.expense.country == 'US'}) "
            f"AND priority == 'High' ({self.expense.priority.value == 'High'}) "
            f"→ {rule_a}"
        )
        
        if rule_a:
            return True, rules_evaluated
        
        # Rule b: Low value or HR department → reject
        rule_b = (
            self.expense.amount <= 100 or
            self.expense.department == "HR"
        )
        rules_evaluated.append(
            f"Rule b (Auto-reject): amount <= 100 ({self.expense.amount <= 100}) "
            f"OR department == 'HR' ({self.expense.department == 'HR'}) "
            f"→ {rule_b}"
        )
        
        if rule_b:
            return False, rules_evaluated
        
        # Default: reject if no rules match
        rules_evaluated.append("No matching rule → Default rejection")
        return False, rules_evaluated

    def execute_finance_notification(self) -> bool:
        """
        Finance Notification Step:
        - Notify Finance team
        - Proceed to CEO Approval
        """
        notification_msg = (
            f"✉ Finance team notified: "
            f"Expense of ${self.expense.amount} from {self.expense.department} "
            f"({self.expense.country}) - Priority: {self.expense.priority.value}"
        )
        return True, [notification_msg]

    def evaluate_ceo_approval(self) -> Tuple[bool, List[str]]:
        """
        CEO Approval Rule:
        - amount > 200 && priority == 'High' → approve (else reject)
        """
        rules_evaluated = []
        
        rule = (
            self.expense.amount > 200 and
            self.expense.priority == Priority.HIGH
        )
        rules_evaluated.append(
            f"CEO Rule: amount > 200 ({self.expense.amount > 200}) "
            f"AND priority == 'High' ({self.expense.priority.value == 'High'}) "
            f"→ {rule}"
        )
        
        return rule, rules_evaluated

    def execute_task_rejection(self) -> Tuple[bool, List[str]]:
        """
        Task Rejection Step:
        - Mark the expense as rejected
        """
        rejection_msg = (
            f"❌ Expense rejected: ${self.expense.amount} from {self.expense.department}"
        )
        return True, [rejection_msg]

    def run(self) -> Dict[str, Any]:
        """Execute the entire workflow"""
        print("\n" + "="*80)
        print("EXPENSE APPROVAL WORKFLOW EXECUTION")
        print("="*80)
        print(f"\nInput Expense Request:")
        print(f"  Amount: ${self.expense.amount}")
        print(f"  Country: {self.expense.country}")
        print(f"  Department: {self.expense.department}")
        print(f"  Priority: {self.expense.priority.value}")
        print("\n" + "-"*80)

        # Step 1: Manager Approval
        print("\n[STEP 1: Manager Approval]")
        approved, rules = self.evaluate_manager_approval()
        print(f"\nRule Evaluation:")
        for rule in rules:
            print(f"  • {rule}")
        
        next_step = "Finance Notification" if approved else "Task Rejection"
        status = StepStatus.APPROVED.value if approved else StepStatus.REJECTED.value
        
        log = StepLog(
            step_name="Manager Approval",
            rules_evaluated=rules,
            status=status,
            next_step=next_step,
            details=f"Decision: {'APPROVED' if approved else 'REJECTED'}"
        )
        self.logs.append(log)
        print(f"Status: {status.upper()}")
        print(f"Next Step: {next_step}")

        if not approved:
            # Rejected path
            print("\n" + "-"*80)
            print("\n[STEP 4: Task Rejection]")
            completed, rejection_msg = self.execute_task_rejection()
            for msg in rejection_msg:
                print(f"  {msg}")
            
            log = StepLog(
                step_name="Task Rejection",
                rules_evaluated=rejection_msg,
                status=StepStatus.COMPLETED.value,
                next_step="WORKFLOW_END",
                details="Expense marked as rejected"
            )
            self.logs.append(log)
            print(f"Status: {StepStatus.COMPLETED.value.upper()}")
            print(f"Next Step: WORKFLOW_END")
            
            self.workflow_completed = True
            self.final_status = "REJECTED"
        else:
            # Approved path
            # Step 2: Finance Notification
            print("\n" + "-"*80)
            print("\n[STEP 2: Finance Notification]")
            notified, notification_msgs = self.execute_finance_notification()
            for msg in notification_msgs:
                print(f"  {msg}")
            
            log = StepLog(
                step_name="Finance Notification",
                rules_evaluated=notification_msgs,
                status=StepStatus.NOTIFIED.value,
                next_step="CEO Approval",
                details="Finance team notified"
            )
            self.logs.append(log)
            print(f"Status: {StepStatus.NOTIFIED.value.upper()}")
            print(f"Next Step: CEO Approval")

            # Step 3: CEO Approval
            print("\n" + "-"*80)
            print("\n[STEP 3: CEO Approval]")
            ceo_approved, ceo_rules = self.evaluate_ceo_approval()
            print(f"\nRule Evaluation:")
            for rule in ceo_rules:
                print(f"  {rule}")
            
            ceo_status = StepStatus.APPROVED.value if ceo_approved else StepStatus.REJECTED.value
            next_step_final = "WORKFLOW_END" if ceo_approved else "Task Rejection"
            
            log = StepLog(
                step_name="CEO Approval",
                rules_evaluated=ceo_rules,
                status=ceo_status,
                next_step=next_step_final,
                details=f"Decision: {'APPROVED' if ceo_approved else 'REJECTED'}"
            )
            self.logs.append(log)
            print(f"Status: {ceo_status.upper()}")
            print(f"Next Step: {next_step_final}")

            if not ceo_approved:
                # Rejection after CEO
                print("\n" + "-"*80)
                print("\n[STEP 4: Task Rejection]")
                completed, rejection_msg = self.execute_task_rejection()
                for msg in rejection_msg:
                    print(f"  {msg}")
                
                log = StepLog(
                    step_name="Task Rejection",
                    rules_evaluated=rejection_msg,
                    status=StepStatus.COMPLETED.value,
                    next_step="WORKFLOW_END",
                    details="Expense marked as rejected by CEO"
                )
                self.logs.append(log)
                print(f"Status: {StepStatus.COMPLETED.value.upper()}")
                print(f"Next Step: WORKFLOW_END")
                
                self.workflow_completed = True
                self.final_status = "REJECTED"
            else:
                # Successfully approved
                self.workflow_completed = True
                self.final_status = "APPROVED"

        # Summary
        print("\n" + "="*80)
        print("WORKFLOW EXECUTION SUMMARY")
        print("="*80)
        print(f"\nWorkflow Status: {self.final_status}")
        print(f"Completed: {self.workflow_completed}")
        print(f"\nExecution Steps:")
        for i, log in enumerate(self.logs, 1):
            print(f"\n  {i}. {log.step_name}")
            print(f"     Status: {log.status.upper()}")
            print(f"     Next Step: {log.next_step}")

        print("\n" + "="*80)
        if self.final_status == "APPROVED":
            print("✅ WORKFLOW COMPLETED SUCCESSFULLY - EXPENSE APPROVED")
        else:
            print("❌ WORKFLOW COMPLETED - EXPENSE REJECTED")
        print("="*80 + "\n")

        return {
            "workflow_completed": self.workflow_completed,
            "final_status": self.final_status,
            "logs": self.logs
        }


def main():
    # Create the expense request
    expense = ExpenseRequest(
        amount=250,
        country="US",
        department="Finance",
        priority=Priority.HIGH
    )

    # Run the workflow
    workflow = WorkflowEngine(expense)
    result = workflow.run()

    # Print detailed execution logs
    print("\nDETAILED EXECUTION LOGS:")
    print("-"*80)
    for log in result["logs"]:
        print(f"\nStep: {log.step_name}")
        print(f"Rules Evaluated:")
        for rule in log.rules_evaluated:
            print(f"  → {rule}")
        print(f"Status: {log.status}")
        print(f"Next Step: {log.next_step}")
        if log.details:
            print(f"Details: {log.details}")


if __name__ == "__main__":
    main()
