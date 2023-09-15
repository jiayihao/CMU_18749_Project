import requests

response = requests.get("http://localhost:8000/hello")
print(response.status_code, response.reason)
print(response.text)