import os
import json
import random
import subprocess
import uuid
from pymongo import MongoClient
from faker import Faker
from datetime import datetime, timedelta


DATABASE_NAME = "local_database"
COLLECTION_NAME = "submission"


LOCALES = [
    "en_US",
    "en_CA",
    "en_GB",
    "es",
    "en_AU",
]



def ensure_mongo_installed_and_running():
    try:
        # Check if MongoDB is installed
        subprocess.run(["mongod", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("MongoDB is already installed.")
    except FileNotFoundError:
        print("Error: MongoDB is not installed, or `mongod` is not in the system PATH.")
        exit(1)

    try:
        print("Starting MongoDB service...")
        subprocess.run(["brew", "services", "start", "mongodb-community"], check=True)  # macOS-specific command
        print("MongoDB service is running.")
    except Exception as e:
        print(f"Error starting MongoDB: {e}")
        print("Ensure MongoDB service is running manually.")
        exit(1)



def connect_to_mongo():
    ensure_mongo_installed_and_running()
    print("Connecting to MongoDB...")
    client = MongoClient("mongodb://localhost:27017/")
    return client


# Delete and recreate the database
def setup_database(client):
    if DATABASE_NAME in client.list_database_names():
        print(f"Deleting existing database: {DATABASE_NAME}")
        client.drop_database(DATABASE_NAME)
    print(f"Creating new database: {DATABASE_NAME}")
    db = client[DATABASE_NAME]
    return db


# Generate Faker instance
def get_faker_instance():
    """Generate a Faker instance for a random locale."""
    locale = random.choice(LOCALES)  # Randomly select one locale
    return Faker(locale)


# Generate random JSON data
def generate_random_json(num_entries=1000):
    data = []
    for _ in range(num_entries):
        faker = get_faker_instance()

        # Generate random record
        _id = str(uuid.uuid4()).replace("-", "")[:24]
        first_name = faker.first_name()
        last_name = faker.last_name()
        email = faker.email()
        phone_number = faker.phone_number()
        comments = faker.sentence(nb_words=random.randint(5, 15))
        accept_terms = random.choice([True, False])

        timezone = random.choice(["UTC", "EST", "CET", "PST", "IST", "CST"])
        ip = faker.ipv4()
        user_agent = faker.user_agent()

        created = faker.date_time_this_decade(before_now=True, after_now=False).isoformat()
        modified = (datetime.fromisoformat(created) + timedelta(minutes=random.randint(1, 60))).isoformat()

        state = random.choice(["submitted", "draft", "in_progress", "completed"])

        entry = {
            "_id": _id,
            "data": {
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "phoneNumber": phone_number,
                "comments": comments,
                "acceptTerms": accept_terms
            },
            "metadata": {
                "timezone": timezone,
                "ip": ip,
                "userAgent": user_agent
            },
            "state": state,
            "created": created,
            "modified": modified
        }

        data.append(entry)

    return data


# Insert data into MongoDB collection
def insert_data_into_collection(db, collection_name, data):
    print(f"Inserting data into collection: {collection_name}")
    collection = db[collection_name]
    collection.insert_many(data)
    print(f"Inserted {len(data)} records into the collection '{collection_name}'.")



if __name__ == "__main__":
    client = connect_to_mongo()

    db = setup_database(client)

    print("Generating random JSON data...")
    random_data = generate_random_json(num_entries=1000)

    insert_data_into_collection(db, COLLECTION_NAME, random_data)

    print("MongoDB setup and data insertion completed successfully!")
