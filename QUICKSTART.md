# 🚀 Quick Start Guide - Expense Approval Workflow

## What You've Created

A complete **web-based expense approval system** with:
- 🎨 Modern, responsive frontend
- 💾 Database to store all expenses and approvals
- 🔄 Automatic hierarchical approval workflow
- 📊 Complete approval tracking and history

---

## Approval Hierarchy Explained

The system automatically routes expenses to the right approver based on **amount**:

### Level 1️⃣: Self-Approved (Amount ≤ $200)
- **Who**: System Auto-approves
- **Time**: Instant
- **Rules**: Just validate country & amount
- **Example**: $150 office supplies → ✅ Approved immediately

### Level 2️⃣: Professor (Amount $200-$500)
- **Who**: Professor/Manager approval
- **Rules**:
  - ✅ Auto-approve: US expenses OR High priority
  - ✅ Auto-approve: HR department expenses
  - ✓ Review needed: Other cases
- **Example**: $350 from Marketing → Professor reviews

### Level 3️⃣: HOD (Amount $500-$1000)
- **Who**: Head of Department
- **Rules**:
  - ✅ High priority → Approve
  - ✅ Medium priority + amount ≤ $800 → Approve
  - ❌ Low priority → Reject
- **Example**: $750 marketing campaign → Professor → HOD

### Level 4️⃣: Principal (Amount > $1000)
- **Who**: Principal/CEO (Final Authority)
- **Rules**:
  - ✅ High priority + amount ≤ $5000 → Approve
  - ❌ Amount > $5000 → Reject
  - ❌ Other cases → Reject
- **Example**: $1500 infrastructure → Professor → HOD → Principal

---

## How to Run

### Option 1: Simple (Double-Click)
1. Go to folder: `C:\Users\sweth\OneDrive\Desktop\3RD Year Kcet\6th semester\Halleyx`
2. Double-click **`RUN.bat`** file
3. Wait for "Running on http://127.0.0.1:5000"
4. Open browser → http://localhost:5000

### Option 2: PowerShell
```powershell
cd "c:\Users\sweth\OneDrive\Desktop\3RD Year Kcet\6th semester\Halleyx"
.\RUN.ps1
```

### Option 3: Manual
```powershell
cd "c:\Users\sweth\OneDrive\Desktop\3RD Year Kcet\6th semester\Halleyx"
python app.py
```

---

## Using the System

### 1. Submit an Expense

Fill in the form:
```
Amount:      250
Country:     US
Department:  Finance
Priority:    High
Description: Office supplies purchase
```

Click **"Submit Expense"** → System instantly shows:
- ✅ Status: APPROVED
- 📊 Approval chain required
- 🔢 Expense ID assigned

### 2. Check Status

Click **"View History"** to see:
- 📋 All submitted expenses
- 📊 Current status of each
- ⏱️ Submission timestamp

Click **"View Details"** for any expense:
- 📄 Full expense details
- 🔄 Complete approval timeline
- 💬 Approval comments
- 📅 When each step occurred

---

## Test Cases to Try

### ✅ Test 1: Auto-Approved
```
Amount:     100
Country:    US
Department: Finance
Priority:   Low
```
**Result**: Instantly approved (≤$200)

### Test 2: Professor Approval
```
Amount:     350
Country:    UK
Department: Marketing
Priority:   Medium
```
**Result**: Sent to Professor for review

### Test 3: HOD Approval
```
Amount:     750
Country:    India
Department: Operations
Priority:   High
```
**Result**: Goes through Professor → HOD chain

### Test 4: Full Escalation
```
Amount:     1500
Country:    Canada
Department: IT
Priority:   High
```
**Result**: Goes through Professor → HOD → Principal

### ❌ Test 5: Rejection
```
Amount:     2000
Country:    US
Department: Finance
Priority:   Low
```
**Result**: Rejected at Principal level (Low priority)

---

## Database

All data is saved in **`expense_workflow.db`** (SQLite file):
- 📝 Every submitted expense
- ✅ All approval decisions
- 💬 Comments from each approver
- ⏱️ Timestamps for audit trail

To reset (delete all data):
```python
from database import clear_database
clear_database()
```

---

## Files Reference

| File | Purpose |
|------|---------|
| **app.py** | Web server & routes |
| **workflow.py** | Approval logic |
| **database.py** | Database operations |
| **RUN.bat** | Windows batch launcher |
| **RUN.ps1** | PowerShell launcher |
| **templates/index.html** | Submission form |
| **templates/history.html** | View all expenses |
| **templates/detail.html** | Approval timeline |
| **expense_workflow.db** | SQLite database (created on first run) |

---

## Common Issues & Solutions

### ❌ "Cannot find port 5000"
Port is already in use. Change in `app.py`:
```python
app.run(debug=True, port=5001)  # Change 5000 to 5001
```

### ❌ "Flask not found"
```powershell
pip install Flask==2.3.0 Werkzeug==2.3.0
```

### ❌ "Database errors"
Delete `expense_workflow.db` and restart - it creates a new one.

### ❌ "Templates not found"
Make sure `templates/` folder exists with 3 HTML files inside.

---

## Key Features Explained

### 🔄 Automatic Workflow
- You submit → System auto-evaluates all rules → Shows decision
- No manual approval needed (we simulate it in console logs)

### 💾 Full History Tracking
- Every expense logged
- Every approval decision recorded
- Can see who approved and when

### 📊 Smart Rules
- Country validation
- Amount-based routing
- Priority-based decisions
- Department-specific rules (HR auto-approves)

### 🎨 Beautiful Frontend
- Clean, modern design
- Mobile-responsive
- Shows real-time approval chain
- Visual timeline of approvals

---

## Backend Logic (Technical)

### Request Flow
```
User submits form
    ↓
Web server receives data
    ↓
Saves to database
    ↓
Workflow engine evaluates rules
    ↓
Records approval decisions
    ↓
Returns status to user
    ↓
User sees results
```

### Approval Chain Decision
```python
if amount <= 200:
    return []  # Auto-approved
elif amount <= 500:
    return ["Professor"]
elif amount <= 1000:
    return ["Professor", "HOD"]
else:
    return ["Professor", "HOD", "Principal"]
```

---

## Next Steps

1. **Run the application**: Double-click `RUN.bat` or use PowerShell
2. **Test with examples**: Try the test cases above
3. **Check history**: View all submissions and approval chains
4. **Explore the code**: Read comments in Python files
5. **Customize rules**: Modify approval logic in `workflow.py`

---

## Questions?

- **How do I stop the server?** → Press `CTRL+C` in terminal
- **How do I change thresholds?** → Edit `workflow.py` in your editor
- **What if I want to add more countries?** → Edit the validation in `workflow.py`
- **Can I modify approver names?** → Yes, edit `ApprovalLevel` enum
- **Where is my data stored?** → In `expense_workflow.db` file

---

**Happy Testing! 🎉**

For full documentation, see **README.md**
