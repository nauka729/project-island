from flask import Flask, request, jsonify
import json
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from parse_and_insert import parse_and_insert
import datetime

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
                            #host="localhost", port="5432")
                            #host="host.docker.internal", port="5555") # if you need to connect from container to host's localhost
                            host="postgres-test-service", port="5432")    # TEST SERVICE NEEDS TO BE CHANGED LATER!
    # create a cursor
    cur = conn.cursor()
  
    # Select all products from the table
    cur.execute('''SELECT id, item_id, auction_id, hid, name, owner, price, time, created_at, updated_at FROM items''')
  
    # Fetch the data
    data = cur.fetchall()
  
    # close the cursor and connection
    cur.close()
    conn.close()
    #print(data)
    #print(json.dumps(data))
    # handling the datatime object and converting it to string
    return json.dumps(data, default=lambda o: o.strftime('%Y-%m-%d %H:%M:%S') if isinstance(o, datetime.datetime) else o)
        
@app.route('/get_item_by_name', methods=["GET"])
def get_item_by_name():
    print("Get single item by name endpoint reached...")
    item_name = request.args.get('name')
    print(item_name)
    #Connect to the database
    conn = psycopg2.connect(database="items",
                            user="postgres",
                            password="postgres",
                            #host="localhost", port="5432")
                            #host="host.docker.internal", port="5555") # if you need to connect from container to host's localhost
                            host="postgres-test-service", port="5432")    # TEST SERVICE NEEDS TO BE CHANGED LATER!
    
    # create a cursor
    cur = conn.cursor()
  
    # Select all products from the table
    # You need the comma at the end as this makes it a tuple!
    cur.execute("SELECT name, price, created_at, updated_at FROM items WHERE name = %s", (item_name,))
  
    # Fetch the data
    data = cur.fetchall()
  
    # close the cursor and connection
    cur.close()
    conn.close()
    #print(data)
    #print(json.dumps(data))
    # handling the datatime object and converting it to string
    return json.dumps(data, default=lambda o: o.strftime('%Y-%m-%d %H:%M:%S') if isinstance(o, datetime.datetime) else o)

@app.route('/send_items', methods=["POST"])
def send_items():
    print("Items reached endpoint...")

    #Connect to the database
    conn = psycopg2.connect(database="items",
                            user="postgres",
                            password="postgres",
                            #host="localhost", port="5432")
                            #host="host.docker.internal", port="5555") # if you need to connect from container to host's localhost
                            host="postgres-test-service", port="5432")    # TEST SERVICE NEEDS TO BE CHANGED LATER!
  
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


@app.route('/send_items_json', methods=["POST"])
def send_items_json():
    # get the textarea text:
    json_text = request.form['jsonInput']
    message = parse_and_insert(json_text)

    return message
