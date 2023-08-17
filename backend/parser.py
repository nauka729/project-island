import json
from pprint import pprint
import psycopg2


# Load the JSON file:

with open('../temp/import_items1.json', 'r', encoding="utf8") as f:
    data = json.load(f)


itemsDict = {}

# Get data from Auctions->Show->Offers, store item_id's as keys in dictionary  to loop over in the next step
for item in data['auctions']['show']['offers']:
    itemsDict[item['item_id']] = {"price": item['bo_g'], "auction_id": item['id'], "time_left": item['time'] }

# Loop over dictionary keys 
for item_id in itemsDict.keys():
    itemsDict[item_id].update({"hid": data['item'][str(item_id)]['hid'], "name": data['item'][str(item_id)]['name'], "owner": data['item'][str(item_id)]['own']})


# Database manipulation:
# Connect to the database
conn = psycopg2.connect(database="items",
                        user="postgres",
                        password="postgres",
                        host="host.docker.internal", port="5555")

cur = conn.cursor() 

# Insert the data into the table (one-by-one - think about improving it later)
# Test values:
for key, value in itemsDict.items():
    item_id = key
    auction_id = value['auction_id']
    hid = value['hid']
    name = value['name']
    owner = value['owner']
    price = value['price']
    time_left = value['time_left']

    cur.execute(
        '''INSERT INTO items \
        (item_id, auction_id, hid, name, owner, price, time) VALUES (%s,%s,%s,%s,%s,%s,%s)''',
        (item_id, auction_id, hid, name, owner, price, time_left))

# commit the changes
conn.commit()

# close the cursor and connection
cur.close()
conn.close()
