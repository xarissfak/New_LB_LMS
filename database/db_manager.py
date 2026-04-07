"""
db_manager.py
Διαχείριση της SQLite βάσης δεδομένων.
"""

import sqlite3
import os
from datetime import datetime

CURRENT_SCHEMA_VERSION = 1

def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_new_database(db_path: str):
    """Δημιουργεί νέα βάση δεδομένων με όλους τους πίνακες."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS clients (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            code        TEXT UNIQUE,
            contact     TEXT,
            email       TEXT,
            phone       TEXT,
            notes       TEXT,
            created_at  TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS analysts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            email       TEXT,
            phone       TEXT,
            notes       TEXT,
            active      INTEGER NOT NULL DEFAULT 1,
            created_at  TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS analysis_types (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            name                TEXT NOT NULL UNIQUE,
            description         TEXT,
            incubation_hours    REAL,
            temperature_c       REAL,
            stages              TEXT,
            unit                TEXT,
            expected_days       INTEGER,
            notes               TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS batches (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_code      TEXT NOT NULL UNIQUE,
            client_id       INTEGER NOT NULL REFERENCES clients(id),
            received_date   TEXT NOT NULL DEFAULT (date('now','localtime')),
            notes           TEXT,
            created_at      TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS samples (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_code     TEXT NOT NULL UNIQUE,
            batch_id        INTEGER NOT NULL REFERENCES batches(id),
            analysis_type_id INTEGER NOT NULL REFERENCES analysis_types(id),
            status          TEXT NOT NULL DEFAULT 'RECEIVED',
            assigned_analyst_id INTEGER REFERENCES analysts(id),
            result_value    TEXT,
            result_notes    TEXT,
            result_at       TEXT,
            notes           TEXT,
            created_at      TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            updated_at      TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS sample_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id   INTEGER NOT NULL REFERENCES samples(id),
            status      TEXT NOT NULL,
            analyst_id  INTEGER REFERENCES analysts(id),
            notes       TEXT,
            timestamp   TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );
    """)

    cursor.execute("DELETE FROM schema_version")
    cursor.execute("INSERT INTO schema_version VALUES (?)", (CURRENT_SCHEMA_VERSION,))
    conn.commit()
    conn.close()


def validate_and_migrate(db_path: str) -> tuple[bool, str]:
    """
    Ελέγχει αν η βάση είναι συμβατή.
    Επιστρέφει (True, '') αν είναι OK, ή (False, μήνυμα_σφάλματος).
    """
    try:
        conn = get_connection(db_path)
        cursor = conn.cursor()

        # Έλεγχος αν υπάρχει πίνακας schema_version
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'")
        if not cursor.fetchone():
            # Παλιά βάση χωρίς version — προσπαθούμε migration
            _run_migration(cursor)
            cursor.execute("INSERT INTO schema_version VALUES (?)", (CURRENT_SCHEMA_VERSION,))
            conn.commit()

        cursor.execute("SELECT version FROM schema_version")
        row = cursor.fetchone()
        version = row[0] if row else 0

        conn.close()

        if version < CURRENT_SCHEMA_VERSION:
            return False, f"Η βάση είναι έκδοση {version}. Απαιτείται αναβάθμιση."

        return True, ""

    except Exception as e:
        return False, str(e)


def _run_migration(cursor):
    """Προσθέτει πίνακες που λείπουν σε παλιές βάσεις."""
    tables = [
        """CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)""",
        """CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            code TEXT UNIQUE, contact TEXT, email TEXT, phone TEXT,
            notes TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')))""",
        """CREATE TABLE IF NOT EXISTS analysts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            email TEXT, phone TEXT, notes TEXT, active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')))""",
        """CREATE TABLE IF NOT EXISTS analysis_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE,
            description TEXT, incubation_hours REAL, temperature_c REAL,
            stages TEXT, unit TEXT, expected_days INTEGER, notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')))""",
        """CREATE TABLE IF NOT EXISTS batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT, batch_code TEXT NOT NULL UNIQUE,
            client_id INTEGER NOT NULL REFERENCES clients(id),
            received_date TEXT NOT NULL DEFAULT (date('now','localtime')),
            notes TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')))""",
        """CREATE TABLE IF NOT EXISTS samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT, sample_code TEXT NOT NULL UNIQUE,
            batch_id INTEGER NOT NULL REFERENCES batches(id),
            analysis_type_id INTEGER NOT NULL REFERENCES analysis_types(id),
            status TEXT NOT NULL DEFAULT 'RECEIVED',
            assigned_analyst_id INTEGER REFERENCES analysts(id),
            result_value TEXT, result_notes TEXT, result_at TEXT, notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime')))""",
        """CREATE TABLE IF NOT EXISTS sample_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id INTEGER NOT NULL REFERENCES samples(id),
            status TEXT NOT NULL, analyst_id INTEGER REFERENCES analysts(id),
            notes TEXT, timestamp TEXT NOT NULL DEFAULT (datetime('now','localtime')))""",
    ]
    for sql in tables:
        cursor.execute(sql)


# ─── SAMPLE STATUS ────────────────────────────────────────────────────────────

STATUSES = [
    ("RECEIVED",   "Παραλαβή"),
    ("IN_ANALYSIS","Προς Ανάλυση"),
    ("ANALYZED",   "Αναλύθηκε"),
    ("PENDING",    "Αναμονή"),
    ("COMPLETED",  "Ολοκλήρωση"),
    ("SHIPPED",    "Αποστολή"),
]

STATUS_COLORS = {
    "RECEIVED":    "#3498db",
    "IN_ANALYSIS": "#e67e22",
    "ANALYZED":    "#9b59b6",
    "PENDING":     "#e74c3c",
    "COMPLETED":   "#27ae60",
    "SHIPPED":     "#95a5a6",
}

def status_label(code: str) -> str:
    for c, label in STATUSES:
        if c == code:
            return label
    return code


def is_configured(db_path: str) -> bool:
    """Ελέγχει αν η βάση έχει τουλάχιστον έναν αναλυτή ή πελάτη."""
    try:
        conn = get_connection(db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM analysts")
        a = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM clients")
        cl = c.fetchone()[0]
        conn.close()
        return a > 0 or cl > 0
    except:
        return False
