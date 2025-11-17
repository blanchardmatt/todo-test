from flask import Flask, render_template, request, jsonify
import os
import json

app = Flask(__name__)

# In-memory storage for todos
todos = []
todo_id_counter = 1

@app.route('/')
def index():
    """Render the main todo application page"""
    return render_template('index.html')

@app.route('/api/todos', methods=['GET'])
def get_todos():
    """Get all todos"""
    return jsonify(todos)

@app.route('/api/todos', methods=['POST'])
def add_todo():
    """Add a new todo"""
    global todo_id_counter
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({'error': 'Todo text is required'}), 400

    todo = {
        'id': todo_id_counter,
        'text': data['text'],
        'completed': False
    }

    todos.append(todo)
    todo_id_counter += 1

    return jsonify(todo), 201

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a todo's completed status"""
    data = request.get_json()

    for todo in todos:
        if todo['id'] == todo_id:
            if 'completed' in data:
                todo['completed'] = data['completed']
            if 'text' in data:
                todo['text'] = data['text']
            return jsonify(todo)

    return jsonify({'error': 'Todo not found'}), 404

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo"""
    global todos

    for i, todo in enumerate(todos):
        if todo['id'] == todo_id:
            deleted_todo = todos.pop(i)
            return jsonify(deleted_todo)

    return jsonify({'error': 'Todo not found'}), 404

@app.route('/health')
def health():
    """Health check endpoint for OpenShift"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
