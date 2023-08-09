from flask import Flask, request, jsonify
import json
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
    return "Hello, World!"

@app.route('/get_items', methods=["GET"])
def get_items():
    print("Get items endpoint reached...")

    #Connect to the database
    conn = psycopg2.connect(database="items",
                            user="postgres",
                            password="postgres",
                            host="localhost", port="5432")
    # create a cursor
    cur = conn.cursor()
  
    # Select all products from the table
    cur.execute('''SELECT item_name, price FROM items''')
  
    # Fetch the data
    data = cur.fetchall()
  
    # close the cursor and connection
    cur.close()
    conn.close()
    print(data)
    print(json.dumps(data))
    return json.dumps(data)
        


@app.route('/send_items', methods=["POST"])
def send_items():
    print("Items reached endpoint...")

    #Connect to the database
    conn = psycopg2.connect(database="items",
                            user="postgres",
                            password="postgres",
                            host="localhost", port="5432")
  
    cur = conn.cursor()
  
    # Get the data from the form
    data = request.json
    
    item = data['item']
    price = data['price']

    #print(item)
    #print(price)
  
    # Insert the data into the table
    cur.execute(
        '''INSERT INTO items \
        (item_name, price) VALUES (%s, %s)''',
        (item, price))
  
    # commit the changes
    conn.commit()
  
    # close the cursor and connection
    cur.close()
    conn.close()
  
    return jsonify({"message": "Items added successfully!"}) 