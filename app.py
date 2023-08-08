from flask import Flask, request, jsonify
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
    return "Hello, World!"

@app.route('/get_items', methods=["GET"])
def get_items():
    print("Get items endpoint reached...")
    with open("database_placeholder.json", "r") as f:
        data = json.load(f)
    return jsonify(data)
        


@app.route('/send_items', methods=["POST"])
def send_items():
    print("Items reached endpoint...")
    data = request.json
    
    item = data['item']
    price = data['price']

    print(item)
    print(price)

    with open("database_placeholder.json", "r") as f:
        items = json.load(f)
    
    items.append({
        'item': item,
        'price': price
    })

    with open("database_placeholder.json", "w") as f:
        json.dump(items, f)



    return jsonify({"message": "Items added successfully!"})