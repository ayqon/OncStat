from app import app
from db_utils import get_db_connection

def test_crud_export():
    print("Testing CRUD & Export...")
    with app.test_client() as client:
        # 1. Test Export (Basic)
        print("- Testing Export...")
        response = client.get('/export')
        assert response.status_code == 200
        assert response.mimetype == 'text/csv'
        assert b"icd10_code,diagnosis_year" in response.data
        
        # 2. Test CRUD - Create
        print("- Testing Create...")
        # Get count before
        with app.app_context():
            conn = get_db_connection()
            start_count = conn.execute("SELECT COUNT(*) FROM incidence").fetchone()[0]
            
        data = {
            'action': 'create',
            'icd10': 'TEST_999',
            'year': '2025',
            'gender': 'Male',
            'age': '90+',
            'count': '1'
        }
        client.post('/crud', data=data, follow_redirects=True)
        
        with app.app_context():
            conn = get_db_connection()
            new_count = conn.execute("SELECT COUNT(*) FROM incidence").fetchone()[0]
            assert new_count == start_count + 1
            
            # Get ID of new record
            new_id = conn.execute("SELECT id FROM incidence WHERE icd10_code='TEST_999'").fetchone()[0]

        # 3. Test CRUD - Read (Check it appears on page)
        print("- Testing Read...")
        response = client.get('/crud')
        assert b"TEST_999" in response.data

        # 4. Test CRUD - Delete
        print("- Testing Delete...")
        client.post('/crud', data={'action': 'delete', 'id': new_id}, follow_redirects=True)
        
        with app.app_context():
            conn = get_db_connection()
            final_count = conn.execute("SELECT COUNT(*) FROM incidence").fetchone()[0]
            assert final_count == start_count
            
    print("CRUD & Export Passed.")

if __name__ == "__main__":
    test_crud_export()
