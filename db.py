import sqlite3

DB_PATH = 'payme.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_virtual_account_by_reference(reference):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM virtual_accounts WHERE reference = ?', (reference,))
    result = cur.fetchone()
    conn.close()
    return dict(result) if result else None

def store_virtual_account_in_db(customer_id, data, va_data):
	# from db import get_db_connection
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute('''CREATE TABLE IF NOT EXISTS virtual_accounts (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		reference TEXT UNIQUE,
		customer_id TEXT,
		first_name TEXT,
		last_name TEXT,
		email TEXT,
		account_number TEXT,
		account_bank_name TEXT,
		account_type TEXT,
		status TEXT,
		amount REAL,
		currency TEXT,
		account_expiration_datetime TEXT,
		created_datetime TEXT
	)''')
	cur.execute('''INSERT INTO virtual_accounts (
		reference, customer_id, first_name, last_name, email, account_number, account_bank_name, account_type, status, amount, currency, account_expiration_datetime, created_datetime
	) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
		va_data.get('reference'),
		customer_id,
		data['first_name'],
		data.get('last_name', ''),
		data['email'],
		va_data.get('account_number'),
		va_data.get('account_bank_name'),
		va_data.get('account_type'),
		va_data.get('status'),
		va_data.get('amount'),
		va_data.get('currency'),
		va_data.get('account_expiration_datetime'),
		va_data.get('created_datetime')
	))
	conn.commit()
	conn.close()



