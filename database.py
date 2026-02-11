import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict

class Database:
    def __init__(self, db_path: str = "giveaway.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS giveaways (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                button_text TEXT NOT NULL,
                channels TEXT,
                winners_count INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                publish_time TEXT,
                end_type TEXT NOT NULL,
                end_value TEXT NOT NULL,
                status TEXT DEFAULT 'draft',
                created_at TEXT NOT NULL,
                message_id INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                giveaway_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT,
                joined_at TEXT NOT NULL,
                FOREIGN KEY (giveaway_id) REFERENCES giveaways (id),
                UNIQUE(giveaway_id, user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                channel_username TEXT,
                added_at TEXT NOT NULL,
                UNIQUE(admin_id, channel_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_giveaway(self, admin_id: int, text: str, button_text: str, 
                       channels: List[str], winners_count: int, channel_id: int,
                       publish_time: Optional[str], end_type: str, end_value: str) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO giveaways 
            (admin_id, text, button_text, channels, winners_count, channel_id, 
             publish_time, end_type, end_value, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (admin_id, text, button_text, json.dumps(channels), winners_count,
              channel_id, publish_time, end_type, end_value, datetime.now().isoformat()))
        
        giveaway_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return giveaway_id
    
    def get_giveaway(self, giveaway_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM giveaways WHERE id = ?', (giveaway_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'admin_id': row[1],
                'text': row[2],
                'button_text': row[3],
                'channels': json.loads(row[4]) if row[4] else [],
                'winners_count': row[5],
                'channel_id': row[6],
                'publish_time': row[7],
                'end_type': row[8],
                'end_value': row[9],
                'status': row[10],
                'created_at': row[11],
                'message_id': row[12]
            }
        return None
    
    def update_giveaway_status(self, giveaway_id: int, status: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE giveaways SET status = ? WHERE id = ?', (status, giveaway_id))
        conn.commit()
        conn.close()
    
    def update_giveaway_message_id(self, giveaway_id: int, message_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE giveaways SET message_id = ? WHERE id = ?', (message_id, giveaway_id))
        conn.commit()
        conn.close()
    
    def add_participant(self, giveaway_id: int, user_id: int, username: Optional[str] = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO participants (giveaway_id, user_id, username, joined_at)
                VALUES (?, ?, ?, ?)
            ''', (giveaway_id, user_id, username, datetime.now().isoformat()))
            conn.commit()
            success = True
        except sqlite3.IntegrityError:
            success = False
        
        conn.close()
        return success
    
    def get_participants(self, giveaway_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, joined_at 
            FROM participants 
            WHERE giveaway_id = ?
        ''', (giveaway_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{'user_id': row[0], 'username': row[1], 'joined_at': row[2]} for row in rows]
    
    def get_participants_count(self, giveaway_id: int) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM participants WHERE giveaway_id = ?', (giveaway_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_admin_giveaways(self, admin_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, text, status, created_at, winners_count
            FROM giveaways 
            WHERE admin_id = ?
            ORDER BY created_at DESC
        ''', (admin_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'text': row[1][:50],
                'status': row[2],
                'created_at': row[3],
                'winners_count': row[4]
            } 
            for row in rows
        ]
    
    def add_admin_channel(self, admin_id: int, channel_id: int, channel_username: Optional[str] = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO admin_channels (admin_id, channel_id, channel_username, added_at)
                VALUES (?, ?, ?, ?)
            ''', (admin_id, channel_id, channel_username, datetime.now().isoformat()))
            conn.commit()
            success = True
        except sqlite3.IntegrityError:
            success = False
        
        conn.close()
        return success
    
    def get_admin_channels(self, admin_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT channel_id, channel_username, added_at
            FROM admin_channels
            WHERE admin_id = ?
        ''', (admin_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'channel_id': row[0],
                'channel_username': row[1],
                'added_at': row[2]
            }
            for row in rows
        ]

db = Database()
