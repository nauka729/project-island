import json
from pprint import pprint
import psycopg2
from psycopg2.errors import UniqueViolation


def parse_and_insert(json_file_as_text):
    data = json.loads(json_file_as_text)
    # Initialize an empty dictionary
    itemsDict = {}

    # Get data from Auctions->Show->Offers, store item_id's as keys in dictionary  to loop over in the next step
    for item in data['auctions']['show']['offers']:
        itemsDict[item['item_id']] = {"price": item['bo_g'], "auction_id": item['id'], "time_left": item['time'] }

    # Loop over dictionary keys 
    for item_id in itemsDict.keys():
        itemsDict[item_id].update({"hid": data['item'][str(item_id)]['hid'], "name": data['item'][str(item_id)]['name'], "owner": data['item'][str(item_id)]['own']})


    # Database manipulation:
    # Connect to the database (when in docker)
    #conn = psycopg2.connect(database="items",
    #                        user="postgres",
    #                        password="postgres",
    #                        host="host.docker.internal", port="5555")
    # Connect to the database (when in k8s, using service)
    conn = psycopg2.connect(database="items",
                            user="postgres",
                            password="postgres",
                            #host="postgres-test-service", port="5432")    # TEST SERVICE NEEDS TO BE CHANGED LATER!
                            host="postgres-service", port="5432")
    
    # Create a cursor
    cur = conn.cursor() 

    # Initialize counters
    inserted_count = 0
    updated_count = 0

    # Insert the data into the table (one-by-one - think about improving it later)
    for key, value in itemsDict.items():
        # 1. Set the Variables:
        # 1.1 Prepare unique ID:
        item_id_as_string = str(key)
        # take only last 3 digits! see 18/08/2023 for the justification
        auction_id_as_string = str(value['auction_id'])[-3:]
        id_as_string = item_id_as_string + auction_id_as_string
        id = int(id_as_string)
        #print(id)
        # 1.1 Prepare rest of variables:
        item_id = key
        auction_id = value['auction_id']
        hid = value['hid']
        name = value['name']
        owner = value['owner']
        price = value['price']
        time_left = value['time_left']

        cur.execute("SAVEPOINT sp_insert")  # Set a savepoint

        # Insert the data, update if there's an error:
        try:
            cur.execute("""
            INSERT INTO items (id, item_id, auction_id, hid, name, owner, price, time)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (id, item_id, auction_id, hid, name, owner, price, time_left))

            inserted_count += 1

        except UniqueViolation:
            # Necessary to continue the transaction after a conflict error
            cur.execute("ROLLBACK TO SAVEPOINT sp_insert")
            cur.execute("""
            UPDATE items
            SET 
                time = %s,
                updated_at = now()
            WHERE id = %s
            """, (time_left, id))
        
            updated_count += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"Inserted {inserted_count} records.")
    print(f"Updated {updated_count} records.")

    return f"Inserted {inserted_count} and updated {updated_count}" 


if __name__ == '__main__':
    # Load the JSON file (initial approach):

    with open('../temp/import_items1.json', 'r', encoding="utf8") as f:
        data = f.read()
        
    parse_and_insert(data)