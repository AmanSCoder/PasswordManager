# For checking strength of password 
Endpoint- `/strength`
```bash
Input format:
{
    "password":password
}

Response format:
 {
        'checked_string': text,
        'breach_status': status,
        'potential_issues': []
 }
```


# For sign up-
Endpoint- `/adduser`
```bash
Input format:
{
    "username":username,
    "password":password
}
Response format:
{"message":"user already exists"}
{"message":"Account Successfully created"}
```


# For login-
Endpoint- `/login`
```bash
Input format:
{
    "username":username,
    "password":password
}
Response format:
{"message": "Login successful"}
{"message": "Incorrect Password"}
{"message": "User does not exist"}
```


# For face authentication:
Endpoint- `/faceauth`
```bash
Input format:
{
"image":[]
}
Responseformat:
{"message": "Face Authenticated"}
{"message": "Face Not Authenticated"}
```

# For saving password
Endpoint- `/save`
```bash
Input format:
{
    "username":username,
    "password":password,
    "reference":reference
}
Response format:
{"message": f"Password for {reference} Updated Successfully"}
{"message": "Password Added Successfully"}
```


# For view of saved password
Endpoint- `/savedpassword`
```bash
Input format:
{
    "username":""
}
Response format:
{
    reference:password
}
```



