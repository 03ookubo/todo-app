from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
CORS(app)
#データベースの接続
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            user='root',
            password='',
            host='localhost',
            database='todo_app'
        )
        return connection
    except Error as e:
        print(f"データベースの接続に失敗しました。: {e}")
        return None

#TODOの取得
@app.route('/todos', methods=['GET'])
def get_todos():
    connection = get_db_connection()
    if connection is None:
        abort(500, description="データベースの接続に失敗しました。")

    #クエリ結果を辞書型で取得
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM todos")
    todos = cursor.fetchall()
    cursor.close()
    connection.close()

    for todo in todos:
        if todo['due_date']:
            todo['dueDate'] = todo['due_date'].strftime('%Y-%m-%d')  # Format date to YYYY-MM-DD

    return jsonify(todos)

@app.route('/todos', methods=['POST'])
def add_todo():
    #JSON形式のデータをPythonの辞書形式で取得
    data = request.json
    connection = get_db_connection()
    if connection is None:
        abort(500, description="データベースの接続に失敗しました。")

    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO todos (title, due_date, details, completed) VALUES (%s, %s, %s, %s)",
        (data['title'], data['dueDate'], data['details'], data.get('completed', False))
    )
    connection.commit()
    #レコードのIDを取得
    new_id = cursor.lastrowid
    cursor.close()
    connection.close()
    return jsonify({'id': new_id, 'title': data['title'], 'dueDate': data['dueDate'], 'details': data['details'], 'completed': data.get('completed', False)}), 201

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo_status(todo_id):
    data = request.json
    completed = data.get('completed', False)

    connection = get_db_connection()
    if connection is None:
        abort(500, description="データベースの接続に失敗しました。")

    cursor = connection.cursor()
    cursor.execute("UPDATE todos SET completed = %s WHERE id = %s", (completed, todo_id))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'id': todo_id, 'completed': completed})

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    connection = get_db_connection()
    if connection is None:
        abort(500, description="データベースの接続に失敗しました。")

    cursor = connection.cursor()
    cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    connection.commit()
    cursor.close()
    connection.close()

    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
