from flask import Flask, jsonify,request
import hashlib
import re
import requests
from pymongo import MongoClient
from flask_cors import CORS
app = Flask(__name__)


CORS(app)
CORS(app, origins='http://localhost:5173', methods=['POST'], headers=['Content-Type'])


# Endpoint to return SHA-1 hash of the received string
def hash_string(text):
    hashed_string = hashlib.sha1(text.encode()).hexdigest()

    response = {
        'original_string': text,
        'hashed_string': hashed_string
    }
    return response

# Endpoint to salt the received string and return it
@app.route('/salt/<string:text>', methods=['GET'])
def salt_string(text):
    salted_string = '@()HB12$_' + text + '_$@L73D'
    
    # TODO: Task 2
    # Write an algorithm that even salts between the text

    response = {
        'original_string': text,
        'salted_string': salted_string
    }
    
    return jsonify(response)

@app.route('/strength', methods=['POST'])
def check_breaches():
    text=request.json['password']

    with open('rockyou.txt', 'r', encoding='utf-8', errors='ignore') as file:
        passwords = file.read().splitlines()

    potential_issues = []

    # Check if the text is found in the "rockyou.txt" file
    if text in passwords:
        potential_issues.append("Found in common passwords list")

    # Check for at least one uppercase letter
    if not any(char.isupper() for char in text):
        potential_issues.append("No uppercase letter")

    # Check for at least one lowercase letter
    if not any(char.islower() for char in text):
        potential_issues.append("No lowercase letter")

    # Check for at least one digit
    if not any(char.isdigit() for char in text):
        potential_issues.append("No digit")

    # Check for at least one special character (except space)
    if not re.search(r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]', text):
        potential_issues.append("No special character")

    # Check for minimum length of 8
    if len(text) < 8:
        potential_issues.append("Length less than 8 characters")

    # Determine the overall status
    if potential_issues:
        status = 'unsafe'
    else:
        status = 'safe'

    response = {
        'checked_string': text,
        'breach_status': status,
        'potential_issues': potential_issues
    }

    return jsonify(response)

        

@app.route('/check_hibp', methods=['POST'])
def check_hibp():
    text=request.json['password']
    # Salt the password using SHA-1
    hashed_text = hashlib.sha1(text.encode()).hexdigest()

    # Query the HIBP API using the first 5 characters of the hash
    api_url = f'https://api.pwnedpasswords.com/range/{hashed_text[:5]}'
    response = requests.get(api_url)

    if response.status_code == 200:
        # Check if the exact hash match is found in the API responses
        hash_suffix = hashed_text[5:].upper()
        breached_count = 0

        for line in response.text.splitlines():
            if line.startswith(hash_suffix):
                # If the exact hash match is found, extract the number of times it has been breached
                breached_count = int(line.split(':')[1])
                break

        if breached_count > 0:
            status = 'unsafe'
            response_message = f'The password has been breached {breached_count} times.'
        else:
            status = 'safe'
            response_message = 'The password is not found in breaches.'

    else:
        # Handle API request failure
        status = 'error'
        response_message = 'Error connecting to HIBP API.'

    response = {
        'checked_string': text,
        'hibp_status': status,
        'message': response_message
    }

    return jsonify(response)



@app.route('/adduser',methods=['POST'])
def addUser():
    data=request.json
    username=data['username']
    password=data['password']
    client = MongoClient("mongodb+srv://aman:aman@cluster0.fundjn6.mongodb.net/")
    db = client.PasswordManager
    collection = db.UserDetails
    savedUser=[]
    for i in collection.find():
        savedUser.append(i['username'])

    if username in savedUser:
        return jsonify({"message":"user already exists"})
    else:
        hash_response=hash_string(password)
        hash=hash_response['hashed_string']
        collection.insert_one({"username":username,"password":hash})
        return jsonify({"message":"Account Successfully created"})


@app.route('/login',methods=['POST'])
def login():
    data=request.json
    username=data['username']
    password=data['password']
    password=hash_string(password)['hashed_string']
    client = MongoClient("mongodb+srv://aman:aman@cluster0.fundjn6.mongodb.net/")
    db = client.PasswordManager
    collection = db.UserDetails
    user_document = collection.find_one({"username": username})
    if user_document:
        # If the username exists, check if the provided password matches the stored password
        if user_document["password"] == password:
            return jsonify({"message": "Login successful"})
        else:
            return jsonify({"message": "Incorrect Password"})
    else:
        return jsonify({"message": "User does not exist"})

@app.route('/save',methods=['POST'])
def savePassword():
    data=request.json
    username=data['username']
    reference=data['reference']
    password=data['password']
    client = MongoClient("mongodb+srv://aman:aman@cluster0.fundjn6.mongodb.net/")
    db = client.PasswordManager
    collection = db.SavedPassword
    usernames = [doc["username"] for doc in collection.find({}, {"username": 1, "_id": 0})]
    if username in usernames:
        document=collection.find_one({"username":username})
        newpassword=document['password']
        newpassword[reference]=password
        collection.update_one({"username":username},{"$set":{"password":newpassword}})  
        return jsonify({"message": f"Password for {reference} Updated Successfully"})

    else:
        collection.insert_one({"username":username,"password":{reference:password}})
        return jsonify({"message": "Password Added Successfully"})


@app.route('/savedpassword',methods=['POST'])
def savedPassword():
    data=request.json
    username=data['username']
    client = MongoClient("mongodb+srv://aman:aman@cluster0.fundjn6.mongodb.net/")
    db = client.PasswordManager
    collection = db.SavedPassword
    if check_user_exists(username,collection):
        password=collection.find_one({"username": username})['password']
        print(password)
        return jsonify({"password": password})
    else:
        return jsonify({"message":"User doesn't exist"})


def check_user_exists(username,collection):
    user_document = collection.find_one({"username": username})
    if user_document:
        return True
    else:
        return False



if __name__ == '__main__':
    app.run()