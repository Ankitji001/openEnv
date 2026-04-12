import unittest
from fastapi.testclient import TestClient
from server.app import app

client = TestClient(app)

response = client.post("/reset")
print("Status Code:", response.status_code)
print("Response JSON:", response.text)
