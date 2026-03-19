"""
Database models for College Leave Approval Workflow
"""

import sqlite3
from datetime import datetime
from typing import List, Dict

DB_NAME = "leave_workflow.db"


def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create Leave Requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            student_id TEXT NOT NULL,
            roll_number TEXT NOT NULL,
            semester INTEGER NOT NULL,
            leave_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            num_days INTEGER NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'Pending',
            final_decision TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create Approvals table to track approval chain
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            leave_id INTEGER NOT NULL,
            approver_level TEXT NOT NULL,
            decision TEXT NOT NULL,
            comments TEXT,
            decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (leave_id) REFERENCES leave_requests(id)
        )
    """)

    conn.commit()
    conn.close()


def add_leave_request(student_name: str, student_id: str, roll_number: str,
                     semester: int, leave_type: str, start_date: str,
                     end_date: str, num_days: int, reason: str = "") -> int:
    """Add a new leave request to the database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO leave_requests 
        (student_name, student_id, roll_number, semester, leave_type, start_date, end_date, num_days, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (student_name, student_id, roll_number, semester, leave_type, start_date, end_date, num_days, reason))
    
    conn.commit()
    leave_id = cursor.lastrowid
    conn.close()
    
    return leave_id


def add_approval(leave_id: int, approver_level: str, decision: str, comments: str = ""):
    """Record an approval decision"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO approvals (leave_id, approver_level, decision, comments)
        VALUES (?, ?, ?, ?)
    """, (leave_id, approver_level, decision, comments))
    
    conn.commit()
    conn.close()


def update_leave_status(leave_id: int, status: str, final_decision: str = None):
    """Update the status of a leave request"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if final_decision:
        cursor.execute("""
            UPDATE leave_requests 
            SET status = ?, final_decision = ?
            WHERE id = ?
        """, (status, final_decision, leave_id))
    else:
        cursor.execute("""
            UPDATE leave_requests 
            SET status = ?
            WHERE id = ?
        """, (status, leave_id))
    
    conn.commit()
    conn.close()


def get_leave_request(leave_id: int) -> Dict:
    """Retrieve a specific leave request"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM leave_requests WHERE id = ?", (leave_id,))
    leave = cursor.fetchone()
    conn.close()
    
    return dict(leave) if leave else None


def get_all_leave_requests() -> List[Dict]:
    """Retrieve all leave requests"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM leave_requests ORDER BY created_at DESC")
    leaves = cursor.fetchall()
    conn.close()
    
    return [dict(leave) for leave in leaves]


def get_leave_approvals(leave_id: int) -> List[Dict]:
    """Get all approvals for a leave request"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM approvals 
        WHERE leave_id = ? 
        ORDER BY decided_at ASC
    """, (leave_id,))
    approvals = cursor.fetchall()
    conn.close()
    
    return [dict(app) for app in approvals]


def clear_database():
    """Clear all data from database (for testing)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM approvals")
    cursor.execute("DELETE FROM leave_requests")
    conn.commit()
    conn.close()
