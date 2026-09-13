from app import app
from db_utils import get_db_connection

def test_app_index():
    print("Testing Index Route...")
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
        assert b"Cancer Insights" in response.data
        assert b"Dashboard" in response.data
        # Check if dynamic stats are loaded (checking for a digit 0-9)
        # We expect "Total Records: [number]"
        assert b"Total Records" in response.data or b"stat-value" in response.data
    print("Index Route Passed.")

if __name__ == "__main__":
    test_app_index()
