from utils.logging_parser import log_query, logger
from pymongo import MongoClient
import time
import random

# MongoDB connection (replace with your actual MongoDB connection string)
client = MongoClient('mongodb://localhost:27017/')
db = client['sample_database']

@log_query
def find_users(age):
    return list(db.users.find({"age": {"$gte": age}}))

@log_query
def insert_user(user):
    return db.users.insert_one(user)

@log_query
def update_user_age(user_id, new_age):
    return db.users.update_one({"_id": user_id}, {"$set": {"age": new_age}})

@log_query
def delete_user(user_id):
    return db.users.delete_one({"_id": user_id})

@log_query
def complex_aggregation():
    pipeline = [
        {"$group": {"_id": "$age", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    return list(db.users.aggregate(pipeline))

def simulate_slow_query():
    time.sleep(6)  # Simulate a slow query by sleeping for 6 seconds
    return db.users.find_one()

@log_query
def potentially_slow_query():
    return simulate_slow_query()

def main():
    logger.info("Application started")

    # Find users
    users = find_users(25)
    logger.info(f"Found {len(users)} users aged 25 or older")

    # Insert a new user
    new_user = {"name": "John Doe", "age": 30, "email": "john@example.com"}
    insert_result = insert_user(new_user)
    logger.info(f"Inserted user with ID: {insert_result.inserted_id}")

    # Update user's age
    update_result = update_user_age(insert_result.inserted_id, 31)
    logger.info(f"Updated {update_result.modified_count} user's age")

    # Delete user
    delete_result = delete_user(insert_result.inserted_id)
    logger.info(f"Deleted {delete_result.deleted_count} user")

    # Run complex aggregation
    age_distribution = complex_aggregation()
    logger.info(f"Age distribution: {age_distribution}")

    # Simulate a slow query
    logger.info("Running a potentially slow query...")
    slow_result = potentially_slow_query()
    logger.info("Potentially slow query completed")

    logger.info("Application finished")

if __name__ == "__main__":
    main()