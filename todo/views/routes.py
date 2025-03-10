from flask import Blueprint, jsonify
from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta
api = Blueprint('api', __name__, url_prefix='/api/v1') 
VALID_FIELDS = {"id", "title", "description", "completed", "deadline_at"}

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})

# This will query the database for all the todos and return them as JSON.
@api.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    result = []
    # completed is string
    completed =request.args.get('completed')
    window =request.args.get('window')
    # check 'completed' and 'window'
    if completed == 'true':
        for todo in todos:
            if todo.completed == False:
                continue
            result.append(todo.to_dict())
        return result    
      
    if window is not None:
        for todo in todos:
            if todo.deadline_at > (datetime.now() + timedelta(days=int(window))):
                continue
            result.append(todo.to_dict())  
        return result
    
    for todo in todos:
        result.append(todo.to_dict())

    return result

@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())


@api.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
  
    # check valid keys
    if request.is_json:      
        # get keys in table and turn it into a set
        if data:
            keys_set = set(data.keys())
            extra_keys = keys_set - VALID_FIELDS
            if extra_keys:
                return jsonify({'error': 'invalid extra keys'}), 400         
    # if 'deadline_at' in request.json:
    #     data.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
    # Adds a new record to the database or will update an existing record.
    title=data.get('title')
    if not title or not title.strip():
        return jsonify({'error': 'title must not null'}), 400 
    todo = Todo(
        title=data.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed'),
    )   
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
    db.session.add(todo)
    # Commits the changes to the database.
    # This must be called for the changes to be saved.
    db.session.commit()
    return jsonify(todo.to_dict()), 201  



@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    data = request.get_json()
    # print("打印data中的请求")
    # print(data)

    if request.is_json:      
    # get keys in table and turn it into a set
        keys_set = set(data.keys())
        # print("打印set(data.keys()")
        # print(keys_set)
        if not keys_set.issubset(VALID_FIELDS):
            return jsonify({'error': 'invalid extra keys'}), 400   
             
    if data is not None:
        if data.get("id") is not None:
            if data.get("id") is not todo:
                return jsonify({'error': 'id is changed'}), 400
            
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    db.session.commit()
    return jsonify(todo.to_dict())


@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({}), 200
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200
 
