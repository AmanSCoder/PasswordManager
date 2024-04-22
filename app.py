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

def anonymize(text):
    if text:
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        placeholder = 'user@example.com'
        anonymized_text = re.sub(email_regex, placeholder, text)
        return anonymized_text
    else:
        return None

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
    hipbStatus=check_hibp(text)
    print(hipbStatus)
    print(hipbStatus['message'])
    potential_issues.append(hipbStatus['message'])
    print(potential_issues)
    # Return the response
    response = {
        'checked_string': text,
        'breach_status': status,
        'potential_issues': potential_issues
    }

    return jsonify(response)

        

def check_hibp(text):
    # text=request.json['password']
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

    return response



@app.route('/adduser',methods=['POST'])
def addUser():
    data=request.json
    username=data['username']
    password=data['password']
    email=data['email']
    anonymize_email=anonymize(email)
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
        collection.insert_one({"username":username,"password":hash,'email':anonymize_email})
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

# @app.route('/face_auth',methods=['POST'])
# def face_auth():


#     if True:
#         return jsonify({"message": "Face Authenticated"})
#     else:
#         return jsonify({"message": "Face Not Authenticated"})











# import os
# import torch
# from torchvision import transforms
# import cv2 as cv
# from flask import Flask,jsonify
# import face_auth,dbstore,train_user
# @app.route("/capture/<user_name>",methods={'GET'})
# def capture(user_name):
#     face_auth.set_variables(r"C:\Users\Rohith\Downloads",user_name)
#     face_auth.cap()
#     return jsonify({'message':'capture successful'}),200

# @app.route("/capture/<user_name>/dbstore",methods={'GET'})
# def data_store(user_name):
#     dbstore.set_variables(r"C:\Users\Rohith\Downloads", user_name)
#     dbstore.database_storage()
#     dbstore.model_storage()
#     return jsonify({'message':'data and model stored in mongodb'})


# @app.route("/train_face_model/<user_name>",methods={'GET'})
# def train(user_name):
#     train_user.set_variables(r"C:\Users\Rohith\Downloads", user_name)
#     train_user.train_face_model()
#     return jsonify({'message':'model training successful for'+user_name}),200


# @app.route("/authenticate/<user_name>",methods={'GET'})
# def classify_face(user_name):
#     global check
#     check=False
#     def patimg(event, x, y, flags, param):
#         global check
#         if event == cv.EVENT_LBUTTONDOWN:
#             check = True
#         if event == cv.EVENT_RBUTTONDOWN:
#             check = False

#     transformer_classify = transforms.Compose([
#         transforms.ToTensor(),
#         transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
#     ])
#     path=r"C:\Users\Rohith\Downloads"
#     best_model_params_path=os.path.join(path+'\\data\\'+user_name,user_name+"_best_model_params.pt")

#     device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#     model= torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', weights=None)
#     num_ftrs =model.fc.in_features
#     model.fc = torch.nn.Linear(num_ftrs, 1)
#     model=model.to(device)
#     model.load_state_dict(torch.load(best_model_params_path))

#     vid = cv.VideoCapture(0)
#     winame = 'Face Authentication'
#     while True:
#         _, image= vid.read()
#         ima = image.copy()
#         cv.namedWindow(winame, cv.WINDOW_NORMAL)
#         cv.resizeWindow(winame, 800, 600)
#         cv.rectangle(image, (175, 400), (500, 75), color=(255, 255, 255), thickness=1)
#         ima = ima[75:400, 175:500]
#         cv.putText(image, text="Position your face inside the frame", lineType=cv.FILLED, color=(255, 200, 170),
#                    thickness=2, fontScale=1, org=(50, 30), fontFace=cv.FONT_HERSHEY_SIMPLEX)
#         cv.setMouseCallback(winame,patimg)
#         cv.imshow(winame,image)
#         if check == True:
#             break
#         if cv.waitKey(10) == (ord('E') | ord('e')):
#             break
#     check=False
#     vid.release()
#     cv.destroyAllWindows()

#     model.eval()
#     im = transformer_classify(ima).unsqueeze(0)
#     print(im.size())
#     with torch.no_grad():
#         output = model(im)

#     print(output)
#     #_,preds= torch.max(output,1)
#     #probabilities = torch.nn.functional.softmax(output[0], dim=0)
#     op = user_name if output[0] > 0.55 else None
#     if op==user_name:
#         return jsonify({'message':'true'}),200
#     else:
#         return jsonify({'message':'false'}),200



if __name__ == '__main__':
    app.run()