"""
action_logger.py
Σύστημα καταγραφής δράσεων (Action Logging) για debugging και audit trail.
"""

import json
import sqlite3
from datetime import datetime
from typing import Any, List, Dict, Optional
from database.db_manager import get_connection


class ActionLogger:
    """Καταγράφει όλες τις ενέργειες στο σύστημα."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_table()
    
    def _ensure_table(self):
        """Δημιουργεί τον πίνακα action_logs αν δεν υπάρχει."""
        try:
            conn = get_connection(self.db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS action_logs (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp   TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                    action      TEXT NOT NULL,
                    category    TEXT NOT NULL,
                    user        TEXT,
                    entity_type TEXT,
                    entity_id   INTEGER,
                    status      TEXT NOT NULL DEFAULT 'SUCCESS',
                    old_data    TEXT,
                    new_data    TEXT,
                    error_msg   TEXT,
                    details     TEXT
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error creating action_logs table: {e}")
    
    def log_action(
        self,
        action: str,
        category: str,
        status: str = "SUCCESS",
        entity_type: str = None,
        entity_id: int = None,
        user: str = None,
        old_data: Dict = None,
        new_data: Dict = None,
        error_msg: str = None,
        details: str = None
    ) -> int:
        """
        Καταγράφει μια ενέργεια.
        
        Args:
            action: Περιγραφή ενέργειας (π.χ. "CREATE", "UPDATE", "DELETE")
            category: Κατηγορία (π.χ. "BATCH", "SAMPLE", "ANALYSIS")
            status: "SUCCESS", "ERROR", "PENDING"
            entity_type: Τύπος οντότητας
            entity_id: ID της οντότητας
            user: Χρήστης που πραγματοποίησε την ενέργεια
            old_data: Παλιά δεδομένα (για update)
            new_data: Νέα δεδομένα
            error_msg: Μήνυμα σφάλματος αν υπάρχει
            details: Επιπλέον λεπτομέρειες
        
        Returns:
            Log ID
        """
        try:
            conn = get_connection(self.db_path)
            
            old_data_json = json.dumps(old_data) if old_data else None
            new_data_json = json.dumps(new_data) if new_data else None
            
            conn.execute(
                """INSERT INTO action_logs
                   (action, category, status, entity_type, entity_id, user,
                    old_data, new_data, error_msg, details)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (action, category, status, entity_type, entity_id, user,
                 old_data_json, new_data_json, error_msg, details)
            )
            conn.commit()
            log_id = conn.lastrowid
            conn.close()
            return log_id
        except Exception as e:
            print(f"Error logging action: {e}")
            return -1
    
    def get_logs(
        self,
        limit: int = 100,
        category: str = None,
        entity_type: str = None,
        status: str = None
    ) -> List[Dict]:
        """Ανακτά καταγεγραμμένες ενέργειες."""
        try:
            conn = get_connection(self.db_path)
            
            sql = "SELECT * FROM action_logs WHERE 1=1"
            params = []
            
            if category:
                sql += " AND category = ?"
                params.append(category)
            if entity_type:
                sql += " AND entity_type = ?"
                params.append(entity_type)
            if status:
                sql += " AND status = ?"
                params.append(status)
            
            sql += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            rows = conn.execute(sql, params).fetchall()
            conn.close()
            
            logs = []
            for row in rows:
                log_dict = dict(row)
                # Parsing JSON fields
                if log_dict['old_data']:
                    log_dict['old_data'] = json.loads(log_dict['old_data'])
                if log_dict['new_data']:
                    log_dict['new_data'] = json.loads(log_dict['new_data'])
                logs.append(log_dict)
            
            return logs
        except Exception as e:
            print(f"Error fetching logs: {e}")
            return []
    
    def get_entity_logs(self, entity_type: str, entity_id: int) -> List[Dict]:
        """Ανακτά όλα τα logs για συγκεκριμένη οντότητα."""
        return self.get_logs(limit=1000, entity_type=entity_type, status=None)
    
    def get_recent_errors(self, limit: int = 20) -> List[Dict]:
        """Ανακτά τα πιο πρόσφατα σφάλματα."""
        return self.get_logs(limit=limit, status="ERROR")
    
    def clear_old_logs(self, days: int = 30):
        """Διαγράφει logs παλιότερα από τις συγκεκριμένες ημέρες."""
        try:
            conn = get_connection(self.db_path)
            conn.execute(
                """DELETE FROM action_logs
                   WHERE datetime(timestamp) < datetime('now', '-' || ? || ' days')""",
                (days,)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error clearing old logs: {e}")


# Singleton instance
_logger_instance = None


def get_logger(db_path: str) -> ActionLogger:
    """Λαμβάνει το singleton instance του logger."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ActionLogger(db_path)
    return _logger_instance
