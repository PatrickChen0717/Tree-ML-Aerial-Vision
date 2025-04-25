import time
import json

import pymongo
from pymongo import MongoClient
import bcrypt

class UserDatabase:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['ServerDB']
        self.user_collection = self.db['userinfo']
        self.history_collection = self.db['history']

    def is_new_user(self, username):
        user = self.user_collection.find_one({"username": username})
        return not user

    def check_password(self, username, password):
        user = self.user_collection.find_one({"username": username})
        if user:
            return bcrypt.checkpw(password.encode(), user['password'].encode())
        return False

    def add_new_user(self, username, password):
        if self.is_new_user(username):
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
            self.user_collection.insert_one({"username": username, "password": hashed_password})
            return True
        return False
      
    def print(self):
        users = self.user_collection.find()
        print("Current users in the database:")
        for user in users:
            print({"username": user.get("username"), "password": user.get("password")})

    def add_history_item(self, username, type, result):
        result_str = json.dumps(result)
        timestamp = time.time()

        try:
            self.history_collection.insert_one({
                "username": username,
                "type": type,
                "result": result_str,
                "timestamp": timestamp
            })
        except Exception as e:
            print("INSERT FAILED:", e)
            raise

        #find number of classifications in history
        count = self.history_collection.count_documents({"username":username})

        #delete oldest entries if we have over 10
        while count > 10:
            self.history_collection.find_one_and_delete(
                filter={"username":username},
                sort=[('timestamp', pymongo.ASCENDING)]
            )

            count -= 1

    def get_history(self, username):
        cursor = list(self.history_collection.find({"username":username}, sort=[("timestamp", pymongo.ASCENDING)]))
        history = {}

        for i in range(len(cursor)):
            history[str(i)] = {
                "type":cursor[i]['type'], 
                "timestamp":cursor[i]['timestamp']
            }

        return history

    def get_old_classification(self, username, type, timestamp):
        classification = self.history_collection.find({"username":username, "type":type, "timestamp":timestamp})[0]

        if classification:
            return json.loads(classification["result"])
        
        return classification
    
    def delete_all_history(self, username):
        result = self.history_collection.delete_many({"username": username})
        return result.deleted_count

    def delete_history_item(self, username, type, timestamp):
        result = self.history_collection.delete_one({
            "username": username,
            "type": type,
            "timestamp": timestamp
        })
        return result.deleted_count
