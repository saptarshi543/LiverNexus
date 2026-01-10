import requests

print("Testing Backend API...")
try:
    # 1. Health check
    r = requests.get("http://localhost:8000/health")
    print(f"Health Check: {r.status_code} - {r.json()}")

    # 2. Tabular Prediction
    data = {"ALT": 45, "AST": 30, "Albumin": 3.8}
    r = requests.post("http://localhost:8000/analyze/tabular", json=data)
    print(f"Tabular Analysis: {r.status_code} - {r.json()}")

    print("\nBackend Logic Verified if outputs are 200.")
except Exception as e:
    print(f"Failed to connect: {e}")
    print("Ensure the backend server is running (uvicorn main:app).")
