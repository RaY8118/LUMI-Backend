from flask import Flask
from flask_pymongo import PyMongo

# Create and configure the Flask app
app = Flask(__name__)
# Ensure this points to your config
app.config.from_object('app.config.Config')

# Initialize PyMongo
mongo = PyMongo(app)

# Access the 'users' collection
users_collection = mongo.db.users
print(users_collection)
# Example usage


def print_users_collection_info():
    # Print the name of the collection
    print("Collection Name:", users_collection.name)

    # Print a sample document if any
    sample_document = users_collection.find_one()
    print("Sample Document:", sample_document)


if __name__ == '__main__':
    print_users_collection_info()
