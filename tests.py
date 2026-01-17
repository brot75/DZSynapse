import unittest
import os
import sqlite3
import database

class TestDZSynapseDB(unittest.TestCase):

    def setUp(self):
        # Use a temporary DB for testing
        database.DB_NAME = "test_dzsynapse.db"
        database.init_db()

    def tearDown(self):
        if os.path.exists("test_dzsynapse.db"):
            os.remove("test_dzsynapse.db")

    def test_auth_security(self):
        # Test default admin account
        user = database.verify_login("doctor", "admin123")
        self.assertIsNotNone(user)
        self.assertEqual(user['role'], "doctor")

        # Test hashing security (password in DB should not be plain text)
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username='doctor'")
        row = cursor.fetchone()
        conn.close()
        self.assertNotEqual(row['password_hash'], "admin123")
        self.assertEqual(len(row['password_hash']), 64) # SHA-256 length

        # Test wrong password
        user = database.verify_login("doctor", "wrongpass")
        self.assertIsNone(user)

    def test_patient_crud(self):
        patient_data = {
            'nom': 'Doe', 'prenom': 'John', 'date_naissance': '01/01/1980',
            'sexe': 'M', 'parents': 'Mr/Mme Doe', 'wilaya': 'Alger',
            'sang': 'A+', 'allergies': 'None', 'antecedents': 'None'
        }
        database.add_patient(patient_data)
        
        patients = database.get_all_patients()
        self.assertEqual(len(patients), 1)
        self.assertEqual(patients[0]['nom'], 'Doe')

        # Test intervention
        pid = patients[0]['id']
        interv_data = {
            'patient_id': pid, 'date': '2023-01-01', 'diagnostic': 'Hernie',
            'type_chirurgie': 'Réparation', 'geste': 'Filet',
            'lateralite': 'Droite', 'urgence': 'Non', 'notes': 'RAS'
        }
        database.add_intervention(interv_data)
        intervs = database.get_interventions(pid)
        self.assertEqual(len(intervs), 1)
        self.assertEqual(intervs[0]['diagnostic'], 'Hernie')

if __name__ == '__main__':
    unittest.main()
