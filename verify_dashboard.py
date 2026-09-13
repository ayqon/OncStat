from app import app

def test_app_dashboard():
    print("Testing Dashboard Route...")
    with app.test_client() as client:
        response = client.get('/dashboard')
        if response.status_code != 200:
            print(f"Status Code: {response.status_code}")
            print(response.get_data(as_text=True))
        
        assert response.status_code == 200
        assert b"Data Insights Dashboard" in response.data
        # Check if images are generated (base64 start)
        assert b"data:image/png;base64" in response.data
        
    print("Dashboard Route Passed.")

if __name__ == "__main__":
    test_app_dashboard()
