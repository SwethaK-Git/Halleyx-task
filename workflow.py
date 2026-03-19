"""
Enhanced Workflow Engine with Hierarchical Approvals
Based on amount thresholds: Professor < 500, HOD < 1000, Principal > 1000
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
from database import add_approval, update_expense_status


class Priority(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ApprovalLevel(Enum):
    PROFESSOR = "Professor"
    HOD = "HOD"
    PRINCIPAL = "Principal"


@dataclass
class ExpenseRequest:
    id: int
    amount: float
    country: str
    department: str
    priority: Priority
    description: str = ""


class HierarchicalWorkflow:
    """
    Approval Hierarchy:
    - Amount <= 200: Approved automatically (no approval needed)
    - 200 < Amount <= 500: Needs Professor approval
    - 500 < Amount <= 1000: Needs HOD approval (after Professor if required)
    - Amount > 1000: Needs Principal approval (cascading)
    """

    def __init__(self, expense: ExpenseRequest):
        self.expense = expense
        self.logs: List[Dict[str, Any]] = []
        self.approval_chain = self._determine_approval_chain()
        self.workflow_completed = False
        self.final_status = "REJECTED"

    def _determine_approval_chain(self) -> List[str]:
        """Determine which approvers are needed based on amount"""
        chain = []
        
        if self.expense.amount <= 200:
            return []  # No approval needed
        elif 200 < self.expense.amount <= 500:
            chain.append("Professor")
        elif 500 < self.expense.amount <= 1000:
            chain.extend(["Professor", "HOD"])
        else:  # > 1000
            chain.extend(["Professor", "HOD", "Principal"])
        
        return chain

    def evaluate_initial_rules(self) -> Tuple[bool, List[str]]:
        """Check initial business rules"""
        rules = []
        
        # Rule 1: Check if amount is valid
        if self.expense.amount <= 0:
            rules.append(f"Invalid amount: ${self.expense.amount} (must be > 0) → REJECTED")
            return False, rules
        
        # Rule 2: Check country
        if self.expense.country not in ["US", "UK", "India", "Canada"]:
            rules.append(f"Country '{self.expense.country}' not in approved list → REJECTED")
            return False, rules
        
        # Rule 3: Check priority
        if self.expense.priority.value not in ["High", "Medium", "Low"]:
            rules.append(f"Invalid priority '{self.expense.priority.value}' → REJECTED")
            return False, rules
        
        rules.append(f"Initial validation passed ✓")
        return True, rules

    def evaluate_professor_approval(self) -> Dict[str, Any]:
        """
        Professor Approval Logic:
        - If country == US or priority == High: Approve
        - If department == HR: Approve
        - Otherwise: Conditional based on amount
        """
        rules = []
        approved = False

        # Rule 1: US or High Priority auto-approve
        if self.expense.country == "US" or self.expense.priority == Priority.HIGH:
            rules.append(
                f"Auto-approve: Country is 'US' ({self.expense.country == 'US'}) "
                f"OR Priority is 'High' ({self.expense.priority == Priority.HIGH}) → Approved"
            )
            approved = True
        # Rule 2: HR department auto-approve
        elif self.expense.department == "HR":
            rules.append(f"HR department auto-approves → Approved")
            approved = True
        # Rule 3: Default conditional
        else:
            rules.append(
                f"Amount ${self.expense.amount} requires further verification → Conditional"
            )
            approved = True  # Professor generally approves, HOD decides

        return {
            "level": "Professor",
            "approved": approved,
            "rules": rules,
            "comments": f"Reviewed expense of ${self.expense.amount} from {self.expense.department}"
        }

    def evaluate_hod_approval(self) -> Dict[str, Any]:
        """
        HOD Approval Logic:
        - Budget constraints: Department budget < 5000
        - Priority-based: High priority gets preference
        - Amount threshold: > 600 requires additional scrutiny
        """
        rules = []
        approved = False

        # Rule 1: High priority gets approved
        if self.expense.priority == Priority.HIGH:
            rules.append(f"High priority expense → Approved")
            approved = True
        # Rule 2: Medium priority with reasonable amount
        elif self.expense.priority == Priority.MEDIUM and self.expense.amount <= 800:
            rules.append(f"Medium priority with amount ≤ $800 → Approved")
            approved = True
        # Rule 3: Low priority rejected
        elif self.expense.priority == Priority.LOW:
            rules.append(f"Low priority expense → Rejected")
            approved = False
        else:
            rules.append(f"Amount exceeds HOD approval limit → Escalate to Principal")
            approved = False

        return {
            "level": "HOD",
            "approved": approved,
            "rules": rules,
            "comments": f"HOD review: ${self.expense.amount} from {self.expense.department}"
        }

    def evaluate_principal_approval(self) -> Dict[str, Any]:
        """
        Principal Approval Logic (Final Authority):
        - Only approves very high priority or strategic expenses
        - Amount > 1000 requires special justification
        - Final decision is absolute
        """
        rules = []
        approved = False

        # Rule 1: Only High priority very large amounts
        if self.expense.priority == Priority.HIGH and self.expense.amount <= 5000:
            rules.append(f"High priority strategic expense ≤ $5000 → Approved")
            approved = True
        # Rule 2: Reject if amount too high
        elif self.expense.amount > 5000:
            rules.append(f"Amount exceeds $5000 limit → Rejected")
            approved = False
        # Rule 3: Other cases rejected
        else:
            rules.append(f"Does not meet Principal approval criteria → Rejected")
            approved = False

        return {
            "level": "Principal",
            "approved": approved,
            "rules": rules,
            "comments": f"Principal final decision on ${self.expense.amount} expense"
        }

    def run(self) -> Dict[str, Any]:
        """Execute the complete workflow"""
        print("\n" + "="*90)
        print("HIERARCHICAL EXPENSE APPROVAL WORKFLOW".center(90))
        print("="*90)
        
        print(f"\n📋 Expense Details:")
        print(f"  ID: {self.expense.id}")
        print(f"  Amount: ${self.expense.amount}")
        print(f"  Country: {self.expense.country}")
        print(f"  Department: {self.expense.department}")
        print(f"  Priority: {self.expense.priority.value}")
        print(f"  Description: {self.expense.description}")
        
        print(f"\n" + "-"*90)
        
        # Step 1: Initial validation
        print("\n[STEP 1: Initial Validation]")
        valid, validation_rules = self.evaluate_initial_rules()
        for rule in validation_rules:
            print(f"  ✓ {rule}")
        
        if not valid:
            print(f"\n❌ Status: REJECTED")
            update_expense_status(self.expense.id, "Rejected", "REJECTED")
            self.workflow_completed = True
            self.final_status = "REJECTED"
            
            self.logs.append({
                "step": "Initial Validation",
                "status": "REJECTED",
                "rules": validation_rules
            })
            
            print("\n" + "="*90)
            print("❌ WORKFLOW COMPLETED - EXPENSE REJECTED".center(90))
            print("="*90 + "\n")
            return {"completed": True, "status": "REJECTED", "logs": self.logs}

        print(f"\n✅ Status: PASSED")
        print(f"Approval Chain Required: {' → '.join(self.approval_chain) if self.approval_chain else 'Auto-Approved'}")

        # If no approval needed
        if not self.approval_chain:
            print(f"\n[STEP 2: Auto-Approval]")
            print(f"  Amount ≤ $200: Automatically approved, no further approval needed")
            print(f"✅ Status: APPROVED")
            
            update_expense_status(self.expense.id, "Approved", "APPROVED")
            add_approval(self.expense.id, "System", "APPROVED", "Auto-approved for amount ≤ $200")
            
            self.workflow_completed = True
            self.final_status = "APPROVED"
            
            print("\n" + "="*90)
            print("✅ WORKFLOW COMPLETED SUCCESSFULLY - EXPENSE APPROVED".center(90))
            print("="*90 + "\n")
            return {"completed": True, "status": "APPROVED", "logs": self.logs}

        # Step 2: Process approval chain
        step_num = 2
        all_approved = True
        
        for approver in self.approval_chain:
            print(f"\n[STEP {step_num}: {approver} Approval]")
            
            if approver == "Professor":
                decision = self.evaluate_professor_approval()
            elif approver == "HOD":
                decision = self.evaluate_hod_approval()
            else:  # Principal
                decision = self.evaluate_principal_approval()
            
            print(f"\nRules Evaluated:")
            for rule in decision["rules"]:
                print(f"  • {rule}")
            
            status = "✅ APPROVED" if decision["approved"] else "❌ REJECTED"
            print(f"\n{status}")
            print(f"Comments: {decision['comments']}")
            
            # Record in database
            add_approval(
                self.expense.id,
                decision["level"],
                "APPROVED" if decision["approved"] else "REJECTED",
                decision["comments"]
            )
            
            self.logs.append({
                "step": f"{decision['level']} Approval",
                "approved": decision["approved"],
                "rules": decision["rules"],
                "comments": decision["comments"]
            })
            
            if not decision["approved"]:
                all_approved = False
                break
            
            step_num += 1

        # Final decision
        print("\n" + "-"*90)
        if all_approved:
            self.final_status = "APPROVED"
            update_expense_status(self.expense.id, "Approved", "APPROVED")
            print("\n" + "="*90)
            print("✅ WORKFLOW COMPLETED SUCCESSFULLY - EXPENSE APPROVED".center(90))
            print("="*90)
        else:
            self.final_status = "REJECTED"
            update_expense_status(self.expense.id, "Rejected", "REJECTED")
            print("\n" + "="*90)
            print("❌ WORKFLOW COMPLETED - EXPENSE REJECTED".center(90))
            print("="*90)
        
        self.workflow_completed = True
        print("")
        
        return {
            "completed": True,
            "status": self.final_status,
            "logs": self.logs,
            "approval_chain": self.approval_chain
        }
