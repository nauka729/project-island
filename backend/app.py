from flask import Flask, request, jsonify
import json
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from parse_and_insert import parse_and_insert
import datetime
from decouple import config
from psycopg2 import pool


# ENV. VARIABLES:
DATABSE=config('DATABSE')
USER=config('USER')
PASSWORD=config('PASSWORD')
HOST=config('HOST')
PORT=config('PORT')

# CREATING THE CONNECTION POOL
minconn = 1 # min. amount of concurrent connections to the database
maxconn = 10 # this will need to be increased it this is ever published

db_pool = pool.SimpleConnectionPool(
    minconn, maxconn,
    database=DATABSE,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT
)

if not db_pool:
    print("Error: Failed to create database connection pool.")

 
app = Flask(__name__)
CORS(app)


@app.route("/")
def hello():
    return "Hello, World!"


@app.route('/api/v1/get_items', methods=["GET"])
def get_items():
    with db_pool.getconn() as conn:
        with conn.cursor() as cur:
            # Select all products from the table
            cur.execute('''SELECT id, item_id, auction_id, hid, name, owner, price, time, created_at, updated_at FROM items''')
            data = cur.fetchall()
        db_pool.putconn(conn)
        # handling the datatime object and converting it to string
    return json.dumps(data, default=lambda o: o.strftime('%Y-%m-%d %H:%M:%S') if isinstance(o, datetime.datetime) else o)



@app.route('/api/v1/get_item_by_name', methods=["GET"])
def get_item_by_name():
    item_name = request.args.get('name')
    with db_pool.getconn() as conn:
        with conn.cursor() as cur:
            # Select all products from the table
            cur.execute("SELECT name, price, created_at, updated_at FROM items WHERE name = %s", (item_name,))
            data = cur.fetchall()
        db_pool.putconn(conn)
        # handling the datatime object and converting it to string
    return json.dumps(data, default=lambda o: o.strftime('%Y-%m-%d %H:%M:%S') if isinstance(o, datetime.datetime) else o)


@app.route('/api/v1/send_items_json', methods=["POST"])
def send_items_json():
    # get the textarea text:
    json_text = request.form['jsonInput']
    print("Received data:", json_text)
    message = parse_and_insert(json_text)

    return message

@app.teardown_appcontext
def close_db_pool(error):
    if hasattr(g, 'db_pool'):
        g.db_pool.closeall()
