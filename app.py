import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, render_template, request, jsonify
from shared.database import store

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'user-secret-key')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shopper/<shopper_id>')
def shopper_page(shopper_id):
    shoppers = store.get_shoppers()
    if shopper_id not in shoppers:
        return "Shopper not found", 404
    return render_template('shopper.html', 
                         shopper_id=shopper_id, 
                         shopper_name=shoppers[shopper_id]['name'])

@app.route('/api/register_shopper', methods=['POST'])
def register_shopper():
    data = request.json
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    success, message, shopper_id = store.register_shopper(name)
    
    if success:
        return jsonify({'shopper_id': shopper_id, 'name': name})
    else:
        return jsonify({'error': message}), 400

@app.route('/api/inventory')
def get_inventory():
    inventory = store.get_inventory()
    return jsonify({
        'inventory': inventory,
        'count': len(inventory),
        'max': store.max_inventory
    })

@app.route('/api/shopper/<shopper_id>/cart')
def get_cart(shopper_id):
    shoppers = store.get_shoppers()
    if shopper_id not in shoppers:
        return jsonify({'error': 'Shopper not found'}), 404
    
    return jsonify({
        'cart': shoppers[shopper_id]['cart'],
        'shopper_name': shoppers[shopper_id]['name']
    })

@app.route('/api/shopper/<shopper_id>/get_item', methods=['POST'])
def get_item(shopper_id):
    data = request.json
    items_input = data.get('item', '').strip()
    
    if not items_input:
        return jsonify({'error': 'Item name(s) required'}), 400
    
    items = [item.strip() for item in items_input.split(',') if item.strip()]
    if not items:
        return jsonify({'error': 'No valid items provided'}), 400
    
    success, message = store.get_items(shopper_id, items)
    
    return jsonify({
        'success': success,
        'message': message,
        'cart': store.get_shoppers().get(shopper_id, {}).get('cart', []),
        'inventory': store.get_inventory()
    })

@app.route('/api/shopper/<shopper_id>/return_item', methods=['POST'])
def return_item(shopper_id):
    data = request.json
    items_input = data.get('item', '').strip()
    
    if not items_input:
        return jsonify({'error': 'Item name(s) required'}), 400
    
    items = [item.strip() for item in items_input.split(',') if item.strip()]
    if not items:
        return jsonify({'error': 'No valid items provided'}), 400
    
    success, message = store.return_items(shopper_id, items)
    
    return jsonify({
        'success': success,
        'message': message,
        'cart': store.get_shoppers().get(shopper_id, {}).get('cart', []),
        'inventory': store.get_inventory()
    })

@app.route('/api/shoppers')
def get_shoppers():
    return jsonify({'shoppers': store.get_shoppers()})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=False)
