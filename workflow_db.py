"""
Workflow Execution Database
Stores all workflow definitions, executions, and audit trails
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

DB_NAME = "workflow_execution.db"


def init_workflow_database():
    """Initialize the workflow database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Workflow Definitions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workflows (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            workflow_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Workflow Executions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workflow_executions (
            id TEXT PRIMARY KEY,
            workflow_id TEXT NOT NULL,
            workflow_name TEXT NOT NULL,
            status TEXT NOT NULL,
            input_data TEXT NOT NULL,
            current_step TEXT,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (workflow_id) REFERENCES workflows(id)
        )
    """)
    
    # Step Executions table (audit trail)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS step_executions (
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
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (workflow_execution_id) REFERENCES workflow_executions(id)
        )
    """)
    
    # Notifications Log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            workflow_execution_id TEXT NOT NULL,
            step_id TEXT NOT NULL,
            recipient TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL,
            sent_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (workflow_execution_id) REFERENCES workflow_executions(id)
        )
    """)
    
    # Approvals Log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS approvals_log (
            id TEXT PRIMARY KEY,
            workflow_execution_id TEXT NOT NULL,
            step_id TEXT NOT NULL,
            approver TEXT NOT NULL,
            decision TEXT NOT NULL,
            comments TEXT,
            decided_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (workflow_execution_id) REFERENCES workflow_executions(id)
        )
    """)
    
    conn.commit()
    conn.close()


def save_workflow(workflow_id: str, name: str, description: str, workflow_dict: Dict):
    """Save workflow definition"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO workflows (id, name, description, workflow_json, updated_at)
        VALUES (?, ?, ?, ?, ?)
    """, (workflow_id, name, description, json.dumps(workflow_dict), datetime.now().isoformat()))
    
    conn.commit()
    conn.close()


def get_workflow(workflow_id: str) -> Optional[Dict]:
    """Get workflow definition"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'workflow_json': json.loads(row['workflow_json']),
            'created_at': row['created_at']
        }
    return None


def get_all_workflows() -> List[Dict]:
    """Get all workflow definitions"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, description, created_at FROM workflows ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def save_execution(execution_id: str, workflow_id: str, workflow_name: str, 
                   status: str, input_data: Dict, current_step: Optional[str],
                   started_at: str, completed_at: Optional[str] = None):
    """Save workflow execution"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Ensure input_data is JSON string
    input_data_json = json.dumps(input_data) if isinstance(input_data, dict) else input_data
    
    cursor.execute("""
        INSERT INTO workflow_executions 
        (id, workflow_id, workflow_name, status, input_data, current_step, started_at, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (execution_id, workflow_id, workflow_name, status, input_data_json,
          current_step, started_at, completed_at))
    
    conn.commit()
    conn.close()


def get_execution(execution_id: str) -> Optional[Dict]:
    """Get workflow execution details"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM workflow_executions WHERE id = ?", (execution_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row['id'],
            'workflow_id': row['workflow_id'],
            'workflow_name': row['workflow_name'],
            'status': row['status'],
            'input_data': json.loads(row['input_data']),
            'current_step': row['current_step'],
            'started_at': row['started_at'],
            'completed_at': row['completed_at']
        }
    return None


def get_all_executions() -> List[Dict]:
    """Get all workflow executions"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, workflow_name, status, started_at, completed_at 
        FROM workflow_executions 
        ORDER BY started_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def save_step_execution(step_id: str, workflow_execution_id: str, step_name: str,
                       step_type: str, status: str, input_data: Dict, output_data: Dict,
                       rules_evaluated: List[str], decision: Optional[str],
                       started_at: str, completed_at: str):
    """Save step execution"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    step_exec_id = f"{workflow_execution_id}_{step_id}"
    
    # Ensure all data is properly JSON serialized
    input_data_json = json.dumps(input_data) if isinstance(input_data, dict) else input_data
    output_data_json = json.dumps(output_data) if isinstance(output_data, dict) else output_data
    rules_evaluated_json = json.dumps(rules_evaluated) if isinstance(rules_evaluated, list) else rules_evaluated
    
    cursor.execute("""
        INSERT INTO step_executions
        (id, workflow_execution_id, step_id, step_name, step_type, status, input_data, 
         output_data, rules_evaluated, decision, started_at, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (step_exec_id, workflow_execution_id, step_id, step_name, step_type, status,
          input_data_json, output_data_json, rules_evaluated_json,
          decision, started_at, completed_at))
    
    conn.commit()
    conn.close()


def get_step_executions(workflow_execution_id: str) -> List[Dict]:
    """Get all step executions for a workflow"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM step_executions 
        WHERE workflow_execution_id = ? 
        ORDER BY created_at ASC
    """, (workflow_execution_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        'id': row['id'],
        'step_id': row['step_id'],
        'step_name': row['step_name'],
        'step_type': row['step_type'],
        'status': row['status'],
        'input_data': json.loads(row['input_data']) if row['input_data'] else {},
        'output_data': json.loads(row['output_data']) if row['output_data'] else {},
        'rules_evaluated': json.loads(row['rules_evaluated']) if row['rules_evaluated'] else [],
        'decision': row['decision'],
        'started_at': row['started_at'],
        'completed_at': row['completed_at']
    } for row in rows]


def save_notification(workflow_execution_id: str, step_id: str, recipient: str,
                     message: str, status: str, sent_at: Optional[str] = None):
    """Log a notification"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    notif_id = f"notif_{workflow_execution_id}_{step_id}_{recipient}"
    
    cursor.execute("""
        INSERT INTO notifications
        (id, workflow_execution_id, step_id, recipient, message, status, sent_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (notif_id, workflow_execution_id, step_id, recipient, message, status, sent_at))
    
    conn.commit()
    conn.close()


def save_approval_record(workflow_execution_id: str, step_id: str, approver: str,
                        decision: str, comments: Optional[str] = None):
    """Log an approval decision"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    approval_id = f"appr_{workflow_execution_id}_{step_id}"
    
    cursor.execute("""
        INSERT INTO approvals_log
        (id, workflow_execution_id, step_id, approver, decision, comments, decided_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (approval_id, workflow_execution_id, step_id, approver, decision, comments,
          datetime.now().isoformat()))
    
    conn.commit()
    conn.close()


def get_notifications(workflow_execution_id: str) -> List[Dict]:
    """Get all notifications for a workflow execution"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM notifications 
        WHERE workflow_execution_id = ? 
        ORDER BY created_at ASC
    """, (workflow_execution_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_approvals(workflow_execution_id: str) -> List[Dict]:
    """Get all approvals for a workflow execution"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM approvals_log 
        WHERE workflow_execution_id = ? 
        ORDER BY created_at ASC
    """, (workflow_execution_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def clear_all_data():
    """Clear all workflow data (for testing)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notifications")
    cursor.execute("DELETE FROM approvals_log")
    cursor.execute("DELETE FROM step_executions")
    cursor.execute("DELETE FROM workflow_executions")
    cursor.execute("DELETE FROM workflows")
    conn.commit()
    conn.close()
