from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Inventory model
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Ensure database is created
with app.app_context():
    db.create_all()

# Middleware for simulating a delay (set to 1 second for testing)
@app.before_request
def delay_response():
    time.sleep(1)

# Logging requests for debugging
@app.before_request
def log_request():
    print(f"\n Received {request.method} request at {request.path}")
    print(f"   Headers: {dict(request.headers)}")
    print(f"   Content-Type: {request.content_type}")
    print(f"   Raw Data: {request.data.decode('utf-8')}")
    
@app.route('/')
def home():
    return {"message": "Server is running"}

# Handle GET and POST requests for transformation data
@app.route('/transform', methods=['GET', 'POST'])
def receive_transform():
    if request.method == 'GET':
        return jsonify({'message': 'Send a POST request with JSON data'}), 200

    data = request.get_json(force=True, silent=True)
    if data is None:
        return jsonify({'error': 'Invalid JSON format or missing Content-Type: application/json'}), 415

    return jsonify({'message': 'Transform received', 'data': data}), 200

@app.route('/translation', methods=['GET', 'POST'])
def receive_translation():
    if request.method == 'GET':
        return jsonify({'message': 'Send a POST request with position data'}), 200

    data = request.get_json(force=True, silent=True)
    if data is None:
        return jsonify({'error': 'Invalid JSON format or missing Content-Type: application/json'}), 415

    return jsonify({'message': 'Translation received', 'data': data}), 200

@app.route('/rotation', methods=['GET', 'POST'])
def receive_rotation():
    if request.method == 'GET':
        return jsonify({'message': 'Send a POST request with rotation data'}), 200

    data = request.get_json(force=True, silent=True)
    if data is None:
        return jsonify({'error': 'Invalid JSON format or missing Content-Type: application/json'}), 415

    return jsonify({'message': 'Rotation received', 'data': data}), 200

@app.route('/scale', methods=['GET', 'POST'])
def receive_scale():
    if request.method == 'GET':
        return jsonify({'message': 'Send a POST request with scale data'}), 200

    data = request.get_json(force=True, silent=True)
    if data is None:
        return jsonify({'error': 'Invalid JSON format or missing Content-Type: application/json'}), 415

    return jsonify({'message': 'Scale received', 'data': data}), 200

@app.route('/file-path', methods=['GET'])
def file_path():
    project_path = request.args.get('projectpath', 'false').lower() == 'true'
    return jsonify({'path': '/path/to/dcc/file' if not project_path else '/path/to/project/folder'}), 200

# Inventory Management Endpoints
@app.route('/add-item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'GET':
        return jsonify({'message': 'Use POST with JSON { "name": "item_name", "quantity": 5 }'}), 200

    data = request.get_json(force=True, silent=True)
    if data is None or 'name' not in data or 'quantity' not in data:
        return jsonify({'error': 'Name and quantity are required'}), 400

    existing_item = Inventory.query.filter_by(name=data['name']).first()
    if existing_item:
        return jsonify({'error': 'Item already exists'}), 400

    new_item = Inventory(name=data['name'], quantity=data['quantity'])
    db.session.add(new_item)
    db.session.commit()

    return jsonify({'message': 'Item added successfully'}), 200

@app.route('/remove-item', methods=['GET', 'POST'])
def remove_item():
    if request.method == 'GET':
        return jsonify({'message': 'Use POST with JSON { "name": "item_name" }'}), 200

    data = request.get_json(force=True, silent=True)
    if data is None or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400

    item = Inventory.query.filter_by(name=data['name']).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({'message': 'Item removed successfully'}), 200

@app.route('/update-quantity', methods=['GET', 'POST'])
def update_quantity():
    if request.method == 'GET':
        return jsonify({'message': 'Use POST with JSON { "name": "item_name", "new_quantity": 10 }'}), 200

    data = request.get_json(force=True, silent=True)
    if data is None or 'name' not in data or 'new_quantity' not in data:
        return jsonify({'error': 'Name and new_quantity are required'}), 400

    item = Inventory.query.filter_by(name=data['name']).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    item.quantity = data['new_quantity']
    db.session.commit()

    return jsonify({'message': 'Quantity updated successfully'}), 200

@app.route('/get-inventory', methods=['GET'])
def get_inventory():
    items = Inventory.query.all()
    inventory_list = [{'name': item.name, 'quantity': item.quantity} for item in items]
    return jsonify({'inventory': inventory_list}), 200



@app.route('/purchase-item', methods=['POST'])
def purchase_item():
    data = request.get_json(force=True, silent=True)
    if not data or 'name' not in data:
        return jsonify({'error': 'Item name is required'}), 400

    item = Inventory.query.filter_by(name=data['name']).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    if item.quantity == 0:
        return jsonify({'error': 'Item is out of stock'}), 400

    item.quantity -= 1
    db.session.commit()
    return jsonify({'message': 'Item purchased successfully'}), 200

@app.route('/return-item', methods=['POST'])
def return_item():
    data = request.get_json(force=True, silent=True)
    if not data or 'name' not in data:
        return jsonify({'error': 'Item name is required'}), 400

    item = Inventory.query.filter_by(name=data['name']).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    item.quantity += 1
    db.session.commit()
    return jsonify({'message': 'Item returned successfully'}), 200

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "Server is running"}), 200



if __name__ == '__main__':

    app.run(debug=True)  # Run the server only in the actual execution
