from app import app
from db_utils import get_db_connection

def test_app_filter():
    print("Testing Filter Route...")
    with app.test_client() as client:
        # GET
        response = client.get('/filter')
        if response.status_code != 200:
            print(f"Status Code: {response.status_code}")
            print(response.get_data(as_text=True))
        assert response.status_code == 200
        assert b"Filter Data" in response.data
        
        # POST - Filter by Sarcoma only
        print("Testing POST filter (Sarcoma)...")
        response = client.post('/filter', data={
            'sarcoma_only': '1'
        })
        assert response.status_code == 200
        assert b"Sarcoma" in response.data
        
        # Check text exists indicating table rows (simple check)
        # Should have results if ETL worked
        if b"No results found" in response.data:
            print("WARNING: No sarcoma results found. ETL might have failed to flag them.")
        else:
            print("Sarcoma results found.")
            
    print("Filter Route Passed.")

if __name__ == "__main__":
    test_app_filter()
