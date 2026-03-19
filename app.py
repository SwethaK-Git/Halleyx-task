"""
Flask Web Application for Expense Approval Workflow
"""

from flask import Flask, render_template, request, jsonify, redirect
from database import init_database, add_expense, get_all_expenses, get_expense, get_expense_approvals
from workflow import HierarchicalWorkflow, Priority, ExpenseRequest
import os

app = Flask(__name__)

# Initialize database on startup
init_database()


@app.route('/')
def index():
    """Home page with expense submission form"""
    return render_template('index.html')


@app.route('/api/submit-expense', methods=['POST'])
def submit_expense():
    """Handle expense submission"""
    try:
        data = request.json
        
        # Validate input
        amount = float(data.get('amount', 0))
        country = data.get('country', '').strip()
        department = data.get('department', '').strip()
        priority = data.get('priority', '').strip()
        description = data.get('description', '').strip()
        submitted_by = data.get('submitted_by', 'User').strip()
        
        if not all([amount, country, department, priority]):
            return jsonify({"error": "Missing required fields"}), 400
        
        if amount <= 0:
            return jsonify({"error": "Amount must be greater than 0"}), 400
        
        if priority not in ["High", "Medium", "Low"]:
            return jsonify({"error": "Invalid priority level"}), 400
        
        # Add to database
        expense_id = add_expense(amount, country, department, priority, description, submitted_by)
        
        # Create expense request for workflow
        expense = ExpenseRequest(
            id=expense_id,
            amount=amount,
            country=country,
            department=department,
            priority=Priority[priority.upper()],
            description=description
        )
        
        # Run workflow
        workflow = HierarchicalWorkflow(expense)
        result = workflow.run()
        
        return jsonify({
            "success": True,
            "expense_id": expense_id,
            "status": result["status"],
            "approval_chain": result["approval_chain"],
            "message": f"Expense submitted successfully. Status: {result['status']}"
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/expenses')
def get_expenses():
    """Get all submitted expenses"""
    try:
        expenses = get_all_expenses()
        return jsonify(expenses), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/expense/<int:expense_id>')
def get_expense_detail(expense_id):
    """Get detailed information about a specific expense"""
    try:
        expense = get_expense(expense_id)
        if not expense:
            return jsonify({"error": "Expense not found"}), 404
        
        approvals = get_expense_approvals(expense_id)
        
        return jsonify({
            "expense": expense,
            "approvals": approvals
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/history')
def history():
    """View submission history"""
    expenses = get_all_expenses()
    return render_template('history.html', expenses=expenses)


@app.route('/expense/<int:expense_id>')
def expense_detail(expense_id):
    """View detailed expense and approval status"""
    expense = get_expense(expense_id)
    if not expense:
        return redirect('/')
    
    approvals = get_expense_approvals(expense_id)
    return render_template('detail.html', expense=expense, approvals=approvals)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
