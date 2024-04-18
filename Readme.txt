For checking strength of password 
/strength

Input format:
{
    "password":""
}

Response format:
 {
        'checked_string': text,
        'breach_status': status,
        'potential_issues': []
 }


For sign up-
/adduser
Input format:
{
    "username":"",
    "password":""
}

Response format:

{"message":"user already exists"}
{"message":"Account Successfully created"}


For login-
/login
Input format:
{
    "username":"",
    "password":""
}
Response format:
{"message": "Login successful"}
{"message": "Incorrect Password"}
{"message": "User does not exist"}


for saving password
/save
Input format:
{
    "username":"charn",
    "password":"9876",
    "reference":"twitter"
}
Response format:
{"message": f"Password for {reference} Updated Successfully"}
{"message": "Password Added Successfully"}



for view of saved password
Input format:
{
    "username":""
}
Response format:
{
    reference:password
}




