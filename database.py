import sqlite3
import hashlib
import os
import uuid
from datetime import datetime

DB_NAME = "dzsynapse.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    
    # Create Patients table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        date_naissance TEXT NOT NULL,
        sexe TEXT NOT NULL,
        parents TEXT,
        wilaya TEXT,
        sang TEXT,
        allergies TEXT,
        antecedents TEXT
    )
    ''')

    # Create Documents table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        file_path TEXT NOT NULL,
        FOREIGN KEY (patient_id) REFERENCES patients (id)
    )
    ''')

    # Create Interventions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interventions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        diagnostic TEXT,
        type_chirurgie TEXT,
        geste TEXT,
        lateralite TEXT,
        urgence TEXT,
        notes TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients (id)
    )
    ''')

    conn.commit()
    conn.close()
    seed_users()
    check_and_update_schema()

def check_and_update_schema():
    """Checks for missing columns and adds them if necessary (Migration)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # helper to check if col exists
    def column_exists(table, col):
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [info[1] for info in cursor.fetchall()]
        return col in columns

    # Patients Table Extensions
    new_patient_cols = {
        'telephone': 'TEXT',
        'commune': 'TEXT',
        'vaccins': 'TEXT',
        'tuteur_nom': 'TEXT',
        'tuteur_lien': 'TEXT',
        'groupe_sanguin': 'TEXT',
        # Medical & Vitals
        'nss': 'TEXT',
        'poids': 'TEXT',
        'taille': 'TEXT',
        'traitements_actuels': 'TEXT',
        'motif_consultation': 'TEXT',
        'ant_medicaux': 'TEXT',
        'ant_chirurgicaux': 'TEXT',
        'ant_familiaux': 'TEXT',
        # Pediatric
        'terme_grossesse': 'TEXT',
        'poids_naissance': 'TEXT',
        'apgar': 'TEXT',
        'mode_accouchement': 'TEXT'
    }
    
    for col, dtype in new_patient_cols.items():
        if not column_exists('patients', col):
            print(f"Migrating: Adding '{col}' to 'patients' table...")
            try:
                cursor.execute(f"ALTER TABLE patients ADD COLUMN {col} {dtype}")
            except Exception as e:
                print(f"Error adding {col}: {e}")

    # Users Table Extensions (Auto-Login)
    if not column_exists('users', 'session_token'):
        print("Migrating: Adding 'session_token' to 'users' table...")
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN session_token TEXT")
        except Exception as e:
             print(f"Error adding session_token: {e}")

    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()
    
    # Simple SHA-256 hashing with salt
    salted_password = salt + password
    hashed = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
    return hashed, salt

def seed_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if admin exists
    cursor.execute('SELECT * FROM users WHERE username = ?', ('doctor',))
    if not cursor.fetchone():
        pwd_hash, salt = hash_password('admin123')
        cursor.execute('INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)',
                       ('doctor', pwd_hash, salt, 'doctor'))
        print("Admin user 'doctor' created.")
        
    # Check if operator exists
    cursor.execute('SELECT * FROM users WHERE username = ?', ('operator',))
    if not cursor.fetchone():
        pwd_hash, salt = hash_password('user123')
        cursor.execute('INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)',
                       ('operator', pwd_hash, salt, 'operator'))
        print("Operator user 'operator' created.")

    conn.commit()
    conn.close()

def verify_login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        stored_hash = user['password_hash']
        salt = user['salt']
        check_hash, _ = hash_password(password, salt)
        if check_hash == stored_hash:
            return {'username': user['username'], 'role': user['role']}
    return None

def create_session(username):
    """Generates a session token, saves it to DB, and returns it."""
    token = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET session_token = ? WHERE username = ?", (token, username))
    conn.commit()
    conn.close()
    return token

def validate_session(token):
    """Checks if a token is valid and returns the user info."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE session_token = ?", (token,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {'username': user['username'], 'role': user['role']}
    return None

def clear_session(username):
    """Clears the session token for a user (Logout)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET session_token = NULL WHERE username = ?", (username,))
    conn.commit()
    conn.close()

# Patient CRUD
def add_patient(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO patients (
            nom, prenom, date_naissance, sexe, parents, wilaya, sang, allergies, antecedents, 
            telephone, commune, vaccins, tuteur_nom, tuteur_lien, groupe_sanguin,
            nss, poids, taille, traitements_actuels, motif_consultation,
            ant_medicaux, ant_chirurgicaux, ant_familiaux,
            terme_grossesse, poids_naissance, apgar, mode_accouchement
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['nom'], data['prenom'], data['date_naissance'], data['sexe'], 
        data.get('parents', ''), data['wilaya'], data.get('sang', ''), data['allergies'], data['antecedents'],
        data.get('telephone', ''), data.get('commune', ''), data.get('vaccins', ''), 
        data.get('tuteur_nom', ''), data.get('tuteur_lien', ''), data.get('groupe_sanguin', ''),
        data.get('nss', ''), data.get('poids', ''), data.get('taille', ''), data.get('traitements_actuels', ''), data.get('motif_consultation', ''),
        data.get('ant_medicaux', ''), data.get('ant_chirurgicaux', ''), data.get('ant_familiaux', ''),
        data.get('terme_grossesse', ''), data.get('poids_naissance', ''), data.get('apgar', ''), data.get('mode_accouchement', '')
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_all_patients(search_query=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    if search_query:
        query = f"%{search_query}%"
        # Expanded search: Nom, Prenom, NSS, Telephone
        cursor.execute("""
            SELECT * FROM patients 
            WHERE nom LIKE ? 
            OR prenom LIKE ? 
            OR nss LIKE ? 
            OR telephone LIKE ?
        """, (query, query, query, query))
    else:
        cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()
    conn.close()
    return patients

def get_patient(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id = ?", (id,))
    patient = cursor.fetchone()
    conn.close()
    return patient

def update_patient(id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE patients SET 
            nom=?, prenom=?, date_naissance=?, sexe=?, parents=?, wilaya=?, sang=?, allergies=?, antecedents=?,
            telephone=?, commune=?, vaccins=?, tuteur_nom=?, tuteur_lien=?, groupe_sanguin=?,
            nss=?, poids=?, taille=?, traitements_actuels=?, motif_consultation=?,
            ant_medicaux=?, ant_chirurgicaux=?, ant_familiaux=?,
            terme_grossesse=?, poids_naissance=?, apgar=?, mode_accouchement=?
        WHERE id=?
    ''', (
        data['nom'], data['prenom'], data['date_naissance'], data['sexe'], 
        data.get('parents', ''), data['wilaya'], data.get('sang', ''), data['allergies'], data['antecedents'],
        data.get('telephone', ''), data.get('commune', ''), data.get('vaccins', ''), 
        data.get('tuteur_nom', ''), data.get('tuteur_lien', ''), data.get('groupe_sanguin', ''),
        data.get('nss', ''), data.get('poids', ''), data.get('taille', ''), data.get('traitements_actuels', ''), data.get('motif_consultation', ''),
        data.get('ant_medicaux', ''), data.get('ant_chirurgicaux', ''), data.get('ant_familiaux', ''),
        data.get('terme_grossesse', ''), data.get('poids_naissance', ''), data.get('apgar', ''), data.get('mode_accouchement', ''),
        id
    ))
    conn.commit()
    conn.close()

def delete_patient(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id=?", (id,))
    conn.commit()
    conn.close()

# Interventions CRUD
def add_intervention(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO interventions (patient_id, date, diagnostic, type_chirurgie, geste, lateralite, urgence, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['patient_id'], data['date'], data['diagnostic'], data['type_chirurgie'], 
          data['geste'], data['lateralite'], data['urgence'], data['notes']))
    conn.commit()
    conn.close()

def get_interventions(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interventions WHERE patient_id = ?", (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Documents CRUD
def add_document(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO documents (patient_id, type, file_path)
        VALUES (?, ?, ?)
    ''', (data['patient_id'], data['type'], data['file_path']))
    conn.commit()
    conn.close()

def get_documents(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE patient_id = ?", (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows
