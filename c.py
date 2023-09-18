import requests


# while True:
#     msg = input("Please enter message>> ")
data = {"message": "hello"}
response = requests.post("http://localhost:8888/", json=data)
print(response.status_code)
print(response.json())