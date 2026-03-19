# 🎨 Custom Workflow Designer - User Guide

## What is the Custom Workflow Designer?

The **Custom Workflow Designer** lets you define your own approval workflows with **YOUR OWN RULES** - without writing any code!

You define:
- What approval thresholds matter (e.g., "$600" or "$5000")
- Who approves at each threshold (Manager, CEO, Finance Director, etc.)
- The system automatically builds and executes the workflow

---

## 📋 How It Works

### Step 1: Define Your Rules

You tell the system your business rules:

```
IF expense > 600
THEN need: Manager approval

IF expense > 5000  
THEN need: Manager + CEO approvals

IF expense > 50000
THEN need: Manager + Finance Director + CEO approvals
```

### Step 2: System Builds Your Workflow

The system automatically creates a workflow structure:

```
Request → Manager Approval → Notification → CEO Approval → Task Done
```

### Step 3: Test It

Submit a test request (e.g., $5000) and see:
- Which approvals it needs
- Whether it's approved or rejected
- Complete step-by-step execution

---

## 🎯 Step-by-Step Usage

### Start the System

```powershell
python workflow_app.py
```

Go to: **http://localhost:5000/custom-designer**

---

### Part 1: Create Your Workflow

**Left Panel: Configure Your Workflow**

1. **Enter Workflow Name** (optional)
   - Example: "Expense Approval", "Purchase Request", "Leave Approval"
   - Default: "Custom Approval Workflow"

2. **Add Thresholds** (repeat for each threshold you want)

   **Example 1:**
   ```
   Amount Threshold: 600
   Select Approvers: Manager
   Click: + Add This Threshold
   ```

   **Example 2:**
   ```
   Amount Threshold: 5000
   Select Approvers: Manager, CEO
   Click: + Add This Threshold
   ```

   **Example 3:**
   ```
   Amount Threshold: 50000
   Select Approvers: Manager, Finance Director, CEO
   Click: + Add This Threshold
   ```

3. **Review Your Thresholds**
   - See all thresholds listed
   - Can remove any by clicking 🗑️

4. **Click: ✅ Create Workflow**
   - System validates and creates workflow
   - You'll see success message

---

### Part 2: Test Your Workflow

**Right Panel: Preview & Execute**

1. **See Workflow Structure**
   - Visual preview of your workflow steps
   - Shows what each approver checks

2. **Fill Test Data**
   ```
   Test Amount: (e.g., 5000)
   Department: (e.g., Finance)
   Status: (e.g., New)
   ```

3. **Click: ▶️ Execute Workflow**
   - System runs your workflow with test data
   - Shows results immediately

---

## 📊 Real-World Example

Let's say you're setting up for **Expense Approval**:

### Your Business Rules:
- Expenses under $600: Manager approves
- Expenses $600-$5000: Manager + Finance Director
- Expenses over $5000: Manager + Finance Director + CEO

### Setup in Custom Designer:

```
THRESHOLD 1:
  Amount: 600
  Approvers: Manager

THRESHOLD 2:
  Amount: 5000
  Approvers: Manager, Finance Director

THRESHOLD 3:
  Amount: 50000
  Approvers: Manager, Finance Director, CEO
```

### Testing:

**Test 1: $500 Expense**
```
Input: Amount=500, Department=Finance
Expected: Manager approval → APPROVED (no CEO needed)
Actual: ✅ Manager Approval → Notification → Task Complete
```

**Test 2: $5000 Expense**
```
Input: Amount=5000, Department=Finance
Expected: Manager + Finance Director approval → APPROVED
Actual: ✅ Manager Approval → Notification → Finance Director → Task Complete
```

**Test 3: $50000 Expense**
```
Input: Amount=50000, Department=Finance
Expected: All three approvals → APPROVED
Actual: ✅ Manager → Notification → Finance Director → CEO → Task Complete
```

---

## 🔄 How Approvals Work

### Manager Approval
- **Checks**: amount > 0 (always required)
- **Decision**: Approve or Reject

### Finance Director Approval (if threshold met)
- **Checks**: amount > $5000
- **Decision**: Approve or Reject

### CEO Approval (if threshold met)
- **Checks**: amount > $50000
- **Decision**: Approve or Reject

---

## 💡 Common Scenarios

### Scenario 1: College Leave Approval

```
THRESHOLD 1:
  Amount: 3 (days)
  Approvers: HOD

THRESHOLD 2:
  Amount: 5 (days)
  Approvers: HOD, Director

THRESHOLD 3:
  Amount: 10 (days)
  Approvers: HOD, Director, Principal
```

**Test**: Requesting 7-day leave → Needs HOD + Director approval

---

### Scenario 2: Purchase Order Approval

```
THRESHOLD 1:
  Amount: 10000 (rupees)
  Approvers: Manager

THRESHOLD 2:
  Amount: 50000
  Approvers: Manager, Finance

THRESHOLD 3:
  Amount: 100000
  Approvers: Manager, Finance, CEO
```

**Test**: Ordering equipment for ₹75,000 → Needs Manager + Finance approval

---

### Scenario 3: Incident Resolution

```
THRESHOLD 1:
  Severity: Low
  Approvers: Support Team

THRESHOLD 2:
  Severity: Medium
  Approvers: Support Team, Manager

THRESHOLD 3:
  Severity: High
  Approvers: Support Team, Manager, Director
```

---

## 🎨 Available Approvers

Choose from:
- **Manager** - Direct supervisor
- **Finance Director** - Finance approval
- **CEO** - Executive decision
- **Director** - Department director
- **HOD** - Head of Department (for educational institutions)

---

## ✅ What Happens When You Execute

1. **System receives your request** (amount, department, status)
2. **Checks thresholds** - Which approval levels are needed?
3. **Executes Manager Approval** - Always happens first
4. **Sends Notification** - Alerts relevant people
5. **Checks higher-level approvals** - Based on amount
6. **Marks as Complete** - If approved

---

## 📈 Viewing Results

After execution, you see:

1. **Execution ID** - Unique identifier for this run
2. **Status** - "completed", "approved", "rejected"
3. **Steps Executed** - How many approval steps ran
4. **Detail for each step** - What happened at each approval

---

## 🔗 Detailed Audit Trail

Click **"View detailed audit trail"** to see:

- Complete timeline of every step
- Exact decision made at each approval
- Timestamp for each action
- Rules that were evaluated
- Who approved/rejected

---

## 🐛 Troubleshooting

### Problem: "Please create a workflow first"
**Solution**: Click the ✅ Create Workflow button on the left panel first

### Problem: Workflow doesn't exclude people I don't want
**Solution**: Only select the approvers you need. The system only creates steps for selected people.

### Problem: Amount threshold not working
**Solution**: Make sure you enter exact numbers. E.g., "5000" not "5000+"

### Problem: Can't select multiple approvers
**Solution**: Hold Ctrl (Cmd on Mac) and click each approver you want

---

## 💾 What Gets Saved

Everything is saved automatically:
- Your workflow definition
- Every execution/test you run
- Complete audit trail
- All decisions made

You can view history anytime: **http://localhost:5000/executions**

---

## 🚀 Next Steps

1. **Start system**: `python workflow_app.py`
2. **Go to**: http://localhost:5000/custom-designer
3. **Create your first workflow**: Add thresholds and click Create
4. **Test it**: Fill in test amount and execute
5. **View results**: See complete execution details
6. **Iterate**: Modify rules and test again

---

## 📝 Key Differences: Default vs. Custom Designer

| Feature | Default Designer | Custom Designer |
|---------|------------------|-----------------|
| **Workflow Type** | Fixed Expense Approval | Your own workflow |
| **Customization** | Can't change | Define your own rules |
| **Thresholds** | Hardcoded (Manager, CEO) | You set amounts and approvers |
| **Best For** | Quick testing | Building your actual system |

---

## 💪 Power Features

### Multiple Approvers at One Level
```
THRESHOLD: $10,000
APPROVERS: Manager, Finance Director, Director
```
All three must approve!

### Complex Escalations
```
THRESHOLD: $1,000 → Manager only
THRESHOLD: $5,000 → + Finance Director
THRESHOLD: $50,000 → + CEO
```
Automatic escalation!

### Industry-Specific Rules
- **Education**: Days of leave → HOD/Director/Principal
- **Finance**: Amount → Manager/Finance/CFO
- **IT**: Priority → Support/Manager/Director
- **HR**: Request type → Manager/HR Director

---

## ❓ FAQs

**Q: Can I change rules after creating workflow?**
A: No, but you can create a new workflow with different rules. Don't worry, old execution data is kept.

**Q: What if an expense amount falls between thresholds?**
A: It uses the highest threshold below the amount. Example: $450 uses $0-$600 threshold.

**Q: Can I add custom approver names?**
A: Currently limited to predefined approvers (Manager, Finance, CEO, etc.), but this can be extended.

**Q: How many thresholds can I create?**
A: Unlimited! Create as many as you need.

**Q: Do rejected expenses get notification?**
A: Yes! All decisions are logged and can be viewed in the audit trail.

---

## 🎓 Learning Resources

1. **Quick Start**: Test with the examples above
2. **Real Data**: Replace test amounts with your actual business amounts
3. **Audit Trail**: Click on any execution to see detailed decision history
4. **Documentation**: Read SYSTEM_SUMMARY.md for architecture details

---

## 📞 Support

If something doesn't work:
1. Check the error message (usually helpful!)
2. Verify all required fields are filled
3. Try with simpler test data first
4. Review the complete audit trail for execution details

---

**Ready to create your first custom workflow?**

→ Go to: **http://localhost:5000/custom-designer**

→ Define your thresholds

→ Click Create

→ Test it!

---

Built for flexible workflow automation | March 2026
