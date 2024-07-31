from pymongo import MongoClient
import pandas as pd

def get_db():
    # Set up the MongoDB client and specify the database and collection
    print("Database created")
    client = MongoClient('mongodb://localhost:27017/')  # Adjust the URI as necessary
    db = client['stock_prices']
    return db

def save_to_mongo(db, collection_name, data):
    collection = db[collection_name]
    if isinstance(data, pd.DataFrame):
        # Convert the dataframe to a dictionary and insert it into the collection
        data_dict = data.to_dict("records")
        collection.insert_many(data_dict)
    elif isinstance(data, dict):
        # If data is a single dictionary, insert it directly
        collection.insert_one(data)
    else:
        print("Unsupported data type for MongoDB insertion.")
        
def fetch_and_store_stock_data(ticker, start, end):
    db = get_db()
    data = fetch_stock_data(ticker, start, end)
    if data is not None:
        data = preprocess_data(data)
        save_to_mongo(db, "stock_prices", data)
        return data
    return None