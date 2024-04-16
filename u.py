# from pymongo import MongoClient
# client = MongoClient("mongodb+srv://aman:aman@cluster0.fundjn6.mongodb.net/")
# db = client.PasswordManager
# collection = db.SavedPassword
# def add_or_update_password(username, reference, password):
    
#     document=collection.find_one({"username":username})
#     print(document)
#     # if document['password'][reference] is not None:
#     newpassword=document['password']
#     newpassword[reference]=password
#     collection.update_one({"username":username},{"$set":{"password":newpassword}})
# add_or_update_password("rohit","insta","1234")




# # usernames = [doc["username"] for doc in collection.find({}, {"username": 1, "_id": 0})]
# # print()
# # user_document = collection.find_one({"username": "aan"})
# # if user_document:
# #     # If the username exists, check if the provided password matches the stored password
# #     if user_document["password"] == "123":
# #         print("logged in")
# #     else:
# #         print("not")
# # else:
# #     print("user not exist")


from pymongo import MongoClient
from gridfs import GridFS
client = MongoClient("mongodb+srv://aman:aman@cluster0.fundjn6.mongodb.net/")
db = client["PasswordManager"]
with open('1.jpeg', 'rb') as file:
    data = file.read()

fs = GridFS(db)
file_id=fs.put(data,filename='1.jpeg')
print("Image stored with id:", file_id)


stored_image = fs.get(file_id)

# Write the retrieved image to a new file
with open('retrieved_image.jpg', 'wb') as file:
    file.write(stored_image.read())

print("Image retrieved and saved.")