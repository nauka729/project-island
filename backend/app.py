# Standard library imports
import datetime
import json

# Third-party imports
from decouple import config
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import psycopg2
from psycopg2 import pool
from psycopg2.errors import UniqueViolation
from psycopg2.extras import RealDictCursor

# Application-specific imports
# Uncomment if you plan to use it in the future
# from parse_and_insert import parse_and_insert


# ENV. VARIABLES:
DATABASE=config('DATABASE')
USER=config('USER')
PASSWORD=config('PASSWORD')
HOST=config('HOST')
PORT=config('PORT')

#TEST

# CREATING THE CONNECTION POOL
minconn = 1 # min. amount of concurrent connections to the database
maxconn = 10 # this will need to be increased it this is ever published

db_pool = pool.SimpleConnectionPool(
    minconn, maxconn,
    database=DATABASE,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT
)

API_KEY = "AKIAIOSFODNN7EXAMPLE"
SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
GOOGLE_CLIENT_ID = "123456789012-abcdefg12345hijklmnop.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "xXxX_YoUr_SeCrEt_xXxX"

if not db_pool:
    print("Error: Failed to create database connection pool.")

# FUNCTIONS:
def process_json_data(json_file_as_text):
    data = json.loads(json_file_as_text)
    items_dict = {}

    # Extract offers from JSON data
    for item in data['auctions']['show']['offers']:
        items_dict[item['item_id']] = {"price": item['bo_g'], "auction_id": item['id'], "time_left": item['time']}

    # Extract additional item details from JSON data
    for item_id in items_dict.keys():
        items_dict[item_id].update({
            "hid": data['item'][str(item_id)]['hid'],
            "name": data['item'][str(item_id)]['name'],
            "owner": data['item'][str(item_id)]['own']
        })

    return items_dict


def insert_or_update_record(cur, item_id, details):
    unique_id_str = str(item_id) + str(details['auction_id'])[-3:]
    unique_id = int(unique_id_str)

    cur.execute("SAVEPOINT sp_insert")

    try:
        cur.execute("""
        INSERT INTO items (id, item_id, auction_id, hid, name, owner, price, time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (unique_id, item_id, details['auction_id'], details['hid'], details['name'], details['owner'], details['price'], details['time_left']))
        return "inserted"

    except UniqueViolation:
        cur.execute("ROLLBACK TO SAVEPOINT sp_insert")
        cur.execute("""
        UPDATE items
        SET 
            time = %s,
            updated_at = now()
        WHERE id = %s
        """, (details['time_left'], unique_id))
        return "updated"
    

def parse_and_insert(json_file_as_text):
    items_dict = process_json_data(json_file_as_text)

    inserted_count, updated_count = 0, 0

    with db_pool.getconn() as conn:  # Automatically releases the connection back to the pool when done
        with conn.cursor() as cur:  # Automatically closes the cursor when done
            for item_id, details in items_dict.items():
                action = insert_or_update_record(cur, item_id, details)
                if action == "inserted":
                    inserted_count += 1
                else:
                    updated_count += 1
            conn.commit()
            db_pool.putconn(conn)
    print(f"Inserted {inserted_count} records.")
    print(f"Updated {updated_count} records.")

    return f"Inserted {inserted_count} and updated {updated_count}"



# SERVER CODE:

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
    try:
        if hasattr(g, 'db_pool'):
            g.db_pool.closeall()
    except psycopg2.pool.PoolError:
        pass
