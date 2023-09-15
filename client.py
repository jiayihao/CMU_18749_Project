import requests

data = {"message": "hello"}
response = requests.post("http://localhost:8000/message", json=data)
print(response.status_code)
print(response.json())
