# 🚀 Universal Workflow Management System

## 📋 Overview

A powerful, flexible **workflow management system** that allows you to create, execute, and track **ANY type of approval workflow** in minutes. Whether it's leave requests, travel approvals, expense management, permission requests, or custom workflows - this system automates it all.

**No coding required!** Design workflows with rules, set approvers, and let the system automatically route requests with complete audit trails.

---

## ✨ Key Features

### 🎨 **Three Designer Options**
- **Default Designer** - Pre-built expense approval workflow
- **Custom Designer** - Define thresholds and approvers (old way)
- **Universal Designer** - Create ANY workflow type with full customization (NEW!)

### ⚡ **Smart Rule Engine**
- Dynamic condition evaluation
- Support for: `>`, `<`, `>=`, `<=`, `==`, `!=`, `in`, `contains`, `startswith`
- AND/OR logic
- Automatic field validation

### 📧 **Automatic Routing**
- Rules automatically determine who should approve
- Send notifications to stakeholders
- Multi-level approvals
- Cascading decision workflows

### 📊 **Complete Audit Trail**
- Every request recorded
- Every decision tracked
- Timestamps for all actions
- Full approval history
- Notifications log
- Rule evaluation records

### 🔒 **Data Persistence**
- SQLite database
- Permanent records
- Query execution history
- Generate reports

---

## 🛠️ Installation & Setup

### **Prerequisites**
- Python 3.7+
- pip (Python package manager)

### **Step 1: Install Dependencies**
```bash
cd "c:\Users\sweth\OneDrive\Desktop\3RD Year Kcet\6th semester\Halleyx"
pip install -r requirements.txt
```

### **Step 2: Run the Application**

**Option A: Using PowerShell**
```powershell
.\RUN.ps1
```

**Option B: Using Command Prompt**
```cmd
RUN.bat
```

**Option C: Direct Python**
```bash
python workflow_app.py
```

### **Step 3: Access the Web Interface**
Open your browser and go to:
```
http://localhost:5000
```

---

## 🎯 How to Use

### **For Leave Requests**

1. **Go to**: `/universal-designer`
2. **Select Template**: "Leave Request"
3. **System Pre-fills**:
   - Fields: days_requested, leave_type, department
   - Rules: 
     - ≤3 days → Manager only
     - 3-7 days → Manager + Director
     - >7 days → Manager + Director + CEO

4. **Click**: "Create Workflow"
5. **Test with Sample Data**:
   - Days: 5
   - Leave Type: Medical
   - Department: IT
6. **Click**: "Execute Workflow"
7. **See Results**: All steps executed with decisions

---

### **For Travel Requests**

1. **Go to**: `/universal-designer`
2. **Select Template**: "Travel Request"
3. **System handles**:
   - Budget routing
   - Destination validation
   - Duration checks

---

### **For Custom Workflows**

1. **Go to**: `/universal-designer`
2. **Select**: "Custom Workflow"
3. **Define Request Fields**:
   ```
   Expense Amount (number)
   Category (text)
   Business Justification (text)
   ```

4. **Add Approval Rules**:
   ```
   Rule 1: If amount ≤ 500 → Manager approves
   Rule 2: If amount > 500 → Manager + Finance approves
   Rule 3: If amount > 5000 → Manager + Finance + CEO approves
   ```

5. **Assign Approvers**: Manager, Director, Finance, CEO, etc.

6. **Create & Test**

---

## 🗂️ Project Structure

```
Halleyx/
├── app.py                          # Old app (legacy)
├── workflow_app.py                 # Main Flask application ✅
├── workflow_engine.py              # Core workflow processing
├── workflow_db.py                  # Database operations
├── database.py                     # Legacy database (not used)
├── requirements.txt                # Python dependencies
├── RUN.bat                         # Windows batch startup
├── RUN.ps1                         # PowerShell startup
│
├── templates/
│   ├── workflow_index.html         # Home page
│   ├── workflow_designer.html      # Default designer
│   ├── custom_workflow_designer.html # Custom designer (old)
│   ├── universal_designer.html     # Universal designer ⭐ NEW
│   ├── workflow_executions.html    # View all executions
│   ├── workflow_detail.html        # Execution details
│   └── ...other templates
│
├── *.db                            # SQLite databases
├── README.md                       # This file
├── APPROVAL_LOGIC_GUIDE.md        # Approval/rejection guide
└── __pycache__/                   # Python cache
```

---

## 🔌 API Endpoints

### **Workflow Management**

#### Create Workflow
```
POST /api/universal-workflow/create
Content-Type: application/json

{
  "workflow_name": "Leave Approval",
  "workflow_description": "Approve leaves by days",
  "fields": [
    {"name": "days_requested", "label": "Days", "type": "number"},
    {"name": "reason", "label": "Reason", "type": "text"}
  ],
  "rules": [
    {
      "field": "days_requested",
      "operator": ">",
      "value": "3",
      "approvers": ["Manager", "Director"]
    }
  ]
}
```

#### Execute Workflow
```
POST /api/universal-workflow/execute
Content-Type: application/json

{
  "workflow_id": "uuid-here",
  "input_data": {
    "days_requested": 5,
    "reason": "Medical leave",
    "department": "IT"
  }
}
```

#### Get Executions
```
GET /api/executions
```

#### Get Execution Details
```
GET /api/execution/{execution_id}
```

---

## 📊 Database Schema

### **Workflows Table**
```sql
CREATE TABLE workflows (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  workflow_json TEXT NOT NULL,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

### **Workflow Executions Table**
```sql
CREATE TABLE workflow_executions (
  id TEXT PRIMARY KEY,
  workflow_id TEXT NOT NULL,
  workflow_name TEXT NOT NULL,
  status TEXT NOT NULL,
  input_data TEXT NOT NULL,
  current_step TEXT,
  started_at TIMESTAMP,
  completed_at TIMESTAMP
)
```

### **Step Executions Table** (Audit Trail)
```sql
CREATE TABLE step_executions (
  id TEXT PRIMARY KEY,
  workflow_execution_id TEXT NOT NULL,
  step_id TEXT NOT NULL,
  step_name TEXT NOT NULL,
  step_type TEXT NOT NULL,
  status TEXT NOT NULL,
  input_data TEXT,
  output_data TEXT,
  rules_evaluated TEXT,
  decision TEXT,
  started_at TIMESTAMP,
  completed_at TIMESTAMP
)
```

---

## 🎯 Available Templates

### **1. Leave Request**
```
Fields: days_requested, leave_type, department
Rules:
  ≤3 days → Manager
  3-7 days → Manager + Director
  >7 days → Manager + Director + CEO
```

### **2. Travel Request**
```
Fields: budget, duration_days, destination
Rules:
  ≤10000 → Manager
  >10000 → Manager + Finance
  International → Add HR
```

### **3. Expense Request**
```
Fields: amount, category, department
Rules:
  ≤500 → Manager
  >500 → Manager + Finance
  >5000 → Manager + Finance + CEO
```

### **4. Permission Request**
```
Fields: access_level, resource, reason
Rules:
  Low → Manager
  Medium → Manager + SecurityAdmin
  High → Manager + SecurityAdmin + CEO
```

### **5. Document Approval**
```
Fields: document_type, version, urgency
Rules:
  Low urgency → Manager
  Policy docs → Manager + Legal
  Version >2 → Manager + Legal + CEO
```

---

## 📈 Workflow Execution Example

### **Leave Request: 5 Days**

**Request:**
```
days_requested: 5
leave_type: Medical
department: IT
```

**Execution Timeline:**
```
2:00:00 PM - Request submitted
2:00:01 PM - Manager notification sent
2:00:02 PM - Director notification sent
2:15:30 PM - Manager approves
   Rules: days > 3? YES ✓
   Decision: APPROVED ✓
2:45:00 PM - Director approves
   Rules: days > 3? YES ✓
   Decision: APPROVED ✓
2:45:01 PM - Final: APPROVED ✓
```

---

## 🔧 Troubleshooting

### **❌ Everything Getting Rejected**

**Problem**: All requests are rejected even when conditions are true.

**Solution**:
1. Check if all required fields are provided
2. Use `/universal-designer` → Load a template
3. Follow the test fields that appear
4. All fields must be filled

---

### **❌ Not All Steps Are Executing**

**Problem**: Only some steps execute, others are skipped.

**Solution**:
1. Check workflow connections
2. Verify all rules are evaluating correctly
3. Go to `/executions` → View details
4. Check "rules_evaluated" field

---

### **❌ Missing Database**

**Problem**: "Database not found" error.

**Solution**:
```bash
python workflow_app.py
# It will auto-create database
```

---

### **❌ Port Already in Use**

**Problem**: "Address already in use" error.

**Solution**:
```bash
taskkill /F /IM python.exe
```

---

## 📚 Rule Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `>` | Greater than | `amount > 1000` |
| `<` | Less than | `days < 5` |
| `>=` | Greater or equal | `budget >= 5000` |
| `<=` | Less or equal | `cost <= 500` |
| `==` | Equals | `status == "Approved"` |
| `!=` | Not equals | `dept != "HR"` |
| `in` | Contains | `"Intl" in destination` |
| `contains` | String contains | `reason contains "urgent"` |
| `startswith` | Starts with | `code startswith "EXP"` |

---

## 🔐 Logic Operators

| Logic | Meaning |
|-------|---------|
| `AND` | ALL rules must be true |
| `OR` | ANY rule can be true |

---

## 🎓 Quick Start Examples

### **Example 1: Simple Expense Approval**

1. Go to `/universal-designer`
2. Click "Expense Request" template
3. Click "Create Workflow"
4. Enter: Amount = 2000
5. Click "Execute"
6. See: Manager approved → Finance → CEO → Complete

---

### **Example 2: Custom Leave Workflow**

1. Custom Workflow
2. Add Rule 1: `days_requested <= 3` → Manager
3. Add Rule 2: `days_requested > 3` → Manager + Director
4. Create
5. Test with: 5 days → Routed to Manager + Director

---

## 📖 Documentation Files

- **README.md** (this file) - System overview and setup
- **APPROVAL_LOGIC_GUIDE.md** - Detailed approval/rejection logic
- **QUICKSTART.md** - Quick start guide
- **WORKFLOW_GUIDE.md** - Workflow design patterns

---

## 🚀 Next Steps

1. **Run the app**: `python workflow_app.py`
2. **Visit**: `http://localhost:5000`
3. **Try a template**: For example, "Leave Request"
4. **Create workflow**: Define rules for your use case
5. **Test it**: Execute with sample data
6. **View results**: Check execution history

---

## ✅ Version Info

- **Version**: 2.0 (Universal)
- **Python**: 3.7+
- **Dependencies**: Flask, SQLite3
- **Database**: SQLite (workflow_execution.db)
- **Last Updated**: March 19, 2026

---

**Happy Workflow Building! 🎉**

For any workflow needs - Expenses, Leave, Travel, Permissions, Documents, or anything else - this system has you covered!
