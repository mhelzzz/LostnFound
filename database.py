import sqlite3
from models import User, LostItem, FoundItem, Claim


class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.conn = sqlite3.connect('lost_and_found.db')
            cls._instance._create_tables()
        return cls._instance

    def _create_tables(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS users
                             (
                                 id
                                 INTEGER
                                 PRIMARY
                                 KEY,
                                 username
                                 TEXT
                                 UNIQUE,
                                 password
                                 TEXT
                             )''')
        self.conn.execute('''CREATE TABLE IF NOT EXISTS items
                             (
                                 id
                                 INTEGER
                                 PRIMARY
                                 KEY,
                                 type
                                 TEXT,
                                 name
                                 TEXT,
                                 description
                                 TEXT,
                                 category
                                 TEXT,
                                 date
                                 TEXT,
                                 location
                                 TEXT,
                                 status
                                 TEXT,
                                 image_path
                                 TEXT,
                                 user_id
                                 INTEGER
                             )''')

        self.conn.execute('''CREATE TABLE IF NOT EXISTS claims
                             (
                                 id
                                 INTEGER
                                 PRIMARY
                                 KEY,
                                 item_id
                                 INTEGER,
                                 claimant_id
                                 INTEGER,
                                 status
                                 TEXT,
                                 claim_date
                                 TEXT
                             )''')
        self.conn.commit()

    def add_user(self, user):
        self.conn.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                          (user.username, user._password_hash))
        self.conn.commit()

    def get_user(self, username):
        cursor = self.conn.execute("SELECT * FROM users WHERE username=?", (username,))
        return cursor.fetchone()

    def add_item(self, item):
        item_type = "lost" if isinstance(item, LostItem) else "found"
        self.conn.execute(
            "INSERT INTO items (type, name, description, category, date, location, status,image_path, user_id ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (item_type, item._name, item._description, item._category, item._date.strftime("%Y-%m-%d"), item._location,
             item._status,item._image_path, item._user_id))
        self.conn.commit()

    def get_items(self, filters=None):
        query = "SELECT * FROM items"
        params = []
        if filters:
            conditions = []
            if 'name' in filters: conditions.append("name LIKE ?"); params.append(f"%{filters['name']}%")
            if 'category' in filters: conditions.append("category=?"); params.append(filters['category'])
            if 'location' in filters: conditions.append("location LIKE ?"); params.append(f"%{filters['location']}%")
            if 'type' in filters: conditions.append("type=?"); params.append(filters['type'])
            if conditions: query += " WHERE " + " AND ".join(conditions)
        cursor = self.conn.execute(query, params)
        return cursor.fetchall()

    def get_item_by_id(self, item_id):
        return self.conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()

    def add_claim(self, claim):
        self.conn.execute(
            "INSERT INTO claims (item_id, claimant_id, status, claim_date) VALUES (?, ?, ?, ?)",
            (claim._item_id, claim._claimant_id, claim._status, claim._claim_date)
        )
        self.conn.commit()

    def get_claims(self):
        cursor = self.conn.execute(
            "SELECT id, item_id, claimant_id, status, claim_date FROM claims"
        )
        return cursor.fetchall()

    def update_item_status(self, item_id, status):
        self.conn.execute("UPDATE items SET status=? WHERE id=?", (status, item_id))
        self.conn.commit()

    def update_claim_status(self, claim_id, status):
        self.conn.execute("UPDATE claims SET status=? WHERE id=?", (status, claim_id))
        self.conn.commit()