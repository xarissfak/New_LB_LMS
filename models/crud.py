"""
models.py
Όλες οι CRUD λειτουργίες για Clients, Analysts, AnalysisTypes, Batches, Samples.
"""

from database.db_manager import get_connection
from datetime import datetime


# ─── CLIENTS ──────────────────────────────────────────────────────────────────

def get_all_clients(db_path):
    conn = get_connection(db_path)
    rows = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_client(db_path, name, code="", contact="", email="", phone="", notes=""):
    conn = get_connection(db_path)
    conn.execute(
        "INSERT INTO clients (name, code, contact, email, phone, notes) VALUES (?,?,?,?,?,?)",
        (name, code or None, contact, email, phone, notes)
    )
    conn.commit()
    conn.close()

def update_client(db_path, client_id, name, code="", contact="", email="", phone="", notes=""):
    conn = get_connection(db_path)
    conn.execute(
        "UPDATE clients SET name=?, code=?, contact=?, email=?, phone=?, notes=? WHERE id=?",
        (name, code or None, contact, email, phone, notes, client_id)
    )
    conn.commit()
    conn.close()

def delete_client(db_path, client_id):
    conn = get_connection(db_path)
    conn.execute("DELETE FROM clients WHERE id=?", (client_id,))
    conn.commit()
    conn.close()


# ─── ANALYSTS ─────────────────────────────────────────────────────────────────

def get_all_analysts(db_path, active_only=False):
    conn = get_connection(db_path)
    sql = "SELECT * FROM analysts"
    if active_only:
        sql += " WHERE active=1"
    sql += " ORDER BY name"
    rows = conn.execute(sql).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_analyst(db_path, name, email="", phone="", notes=""):
    conn = get_connection(db_path)
    conn.execute(
        "INSERT INTO analysts (name, email, phone, notes) VALUES (?,?,?,?)",
        (name, email, phone, notes)
    )
    conn.commit()
    conn.close()

def update_analyst(db_path, analyst_id, name, email="", phone="", notes="", active=1):
    conn = get_connection(db_path)
    conn.execute(
        "UPDATE analysts SET name=?, email=?, phone=?, notes=?, active=? WHERE id=?",
        (name, email, phone, notes, active, analyst_id)
    )
    conn.commit()
    conn.close()

def delete_analyst(db_path, analyst_id):
    conn = get_connection(db_path)
    conn.execute("DELETE FROM analysts WHERE id=?", (analyst_id,))
    conn.commit()
    conn.close()


# ─── ANALYSIS TYPES ───────────────────────────────────────────────────────────

def get_all_analysis_types(db_path):
    conn = get_connection(db_path)
    rows = conn.execute("SELECT * FROM analysis_types ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_analysis_type(db_path, name, description="", incubation_hours=None,
                      temperature_c=None, stages="", unit="", expected_days=None, notes=""):
    conn = get_connection(db_path)
    conn.execute(
        """INSERT INTO analysis_types
           (name, description, incubation_hours, temperature_c, stages, unit, expected_days, notes)
           VALUES (?,?,?,?,?,?,?,?)""",
        (name, description, incubation_hours, temperature_c, stages, unit, expected_days, notes)
    )
    conn.commit()
    conn.close()

def update_analysis_type(db_path, at_id, name, description="", incubation_hours=None,
                         temperature_c=None, stages="", unit="", expected_days=None, notes=""):
    conn = get_connection(db_path)
    conn.execute(
        """UPDATE analysis_types SET name=?, description=?, incubation_hours=?,
           temperature_c=?, stages=?, unit=?, expected_days=?, notes=? WHERE id=?""",
        (name, description, incubation_hours, temperature_c, stages, unit, expected_days, notes, at_id)
    )
    conn.commit()
    conn.close()

def delete_analysis_type(db_path, at_id):
    conn = get_connection(db_path)
    conn.execute("DELETE FROM analysis_types WHERE id=?", (at_id,))
    conn.commit()
    conn.close()


# ─── BATCHES ──────────────────────────────────────────────────────────────────

def get_all_batches(db_path):
    conn = get_connection(db_path)
    rows = conn.execute("""
        SELECT b.*, c.name as client_name, c.code as client_code,
               COUNT(s.id) as sample_count
        FROM batches b
        JOIN clients c ON c.id = b.client_id
        LEFT JOIN samples s ON s.batch_id = b.id
        GROUP BY b.id
        ORDER BY b.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_batch(db_path, batch_id):
    conn = get_connection(db_path)
    row = conn.execute("""
        SELECT b.*, c.name as client_name
        FROM batches b JOIN clients c ON c.id=b.client_id
        WHERE b.id=?
    """, (batch_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_batch(db_path, batch_code, client_id, received_date, notes=""):
    conn = get_connection(db_path)
    conn.execute(
        "INSERT INTO batches (batch_code, client_id, received_date, notes) VALUES (?,?,?,?)",
        (batch_code, client_id, received_date, notes)
    )
    conn.commit()
    last = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return last

def delete_batch(db_path, batch_id):
    conn = get_connection(db_path)
    conn.execute("DELETE FROM sample_history WHERE sample_id IN (SELECT id FROM samples WHERE batch_id=?)", (batch_id,))
    conn.execute("DELETE FROM samples WHERE batch_id=?", (batch_id,))
    conn.execute("DELETE FROM batches WHERE id=?", (batch_id,))
    conn.commit()
    conn.close()

def next_batch_code(db_path, client_identifier: str) -> str:
    """
    Παράγει αυτόματα τον επόμενο κωδικό batch.
    π.χ. αν υπάρχει Γιώργος-3, επιστρέφει Γιώργος-4
    """
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT batch_code FROM batches WHERE batch_code LIKE ?",
        (f"{client_identifier}-%",)
    ).fetchall()
    conn.close()
    max_n = 0
    for r in rows:
        try:
            n = int(r[0].split("-")[-1])
            if n > max_n:
                max_n = n
        except:
            pass
    return f"{client_identifier}-{max_n + 1}"


# ─── SAMPLES ──────────────────────────────────────────────────────────────────

def get_samples_for_batch(db_path, batch_id):
    conn = get_connection(db_path)
    rows = conn.execute("""
        SELECT s.*, at.name as analysis_name, at.expected_days,
               an.name as analyst_name
        FROM samples s
        JOIN analysis_types at ON at.id = s.analysis_type_id
        LEFT JOIN analysts an ON an.id = s.assigned_analyst_id
        WHERE s.batch_id = ?
        ORDER BY s.sample_code
    """, (batch_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_samples(db_path, status_filter=None):
    conn = get_connection(db_path)
    sql = """
        SELECT s.*, at.name as analysis_name, at.expected_days,
               an.name as analyst_name,
               b.batch_code, c.name as client_name
        FROM samples s
        JOIN analysis_types at ON at.id = s.analysis_type_id
        LEFT JOIN analysts an ON an.id = s.assigned_analyst_id
        JOIN batches b ON b.id = s.batch_id
        JOIN clients c ON c.id = b.client_id
    """
    if status_filter:
        sql += f" WHERE s.status = '{status_filter}'"
    sql += " ORDER BY s.created_at DESC"
    rows = conn.execute(sql).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_sample(db_path, sample_code, batch_id, analysis_type_id, notes=""):
    conn = get_connection(db_path)
    conn.execute(
        """INSERT INTO samples (sample_code, batch_id, analysis_type_id, notes)
           VALUES (?,?,?,?)""",
        (sample_code, batch_id, analysis_type_id, notes)
    )
    last = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    # Καταγραφή αρχικής κατάστασης
    conn.execute(
        "INSERT INTO sample_history (sample_id, status) VALUES (?, 'RECEIVED')",
        (last,)
    )
    conn.commit()
    conn.close()
    return last

def update_sample_status(db_path, sample_id, new_status, analyst_id=None, notes=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection(db_path)
    conn.execute(
        "UPDATE samples SET status=?, assigned_analyst_id=?, updated_at=? WHERE id=?",
        (new_status, analyst_id, now, sample_id)
    )
    conn.execute(
        "INSERT INTO sample_history (sample_id, status, analyst_id, notes) VALUES (?,?,?,?)",
        (sample_id, new_status, analyst_id, notes)
    )
    conn.commit()
    conn.close()

def update_sample_result(db_path, sample_id, result_value, result_notes, analyst_id=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection(db_path)
    conn.execute(
        """UPDATE samples SET result_value=?, result_notes=?,
           result_at=?, assigned_analyst_id=?, updated_at=? WHERE id=?""",
        (result_value, result_notes, now, analyst_id, now, sample_id)
    )
    conn.commit()
    conn.close()

def delete_sample(db_path, sample_id):
    conn = get_connection(db_path)
    conn.execute("DELETE FROM sample_history WHERE sample_id=?", (sample_id,))
    conn.execute("DELETE FROM samples WHERE id=?", (sample_id,))
    conn.commit()
    conn.close()

def get_sample_history(db_path, sample_id):
    conn = get_connection(db_path)
    rows = conn.execute("""
        SELECT sh.*, an.name as analyst_name
        FROM sample_history sh
        LEFT JOIN analysts an ON an.id = sh.analyst_id
        WHERE sh.sample_id = ?
        ORDER BY sh.timestamp
    """, (sample_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def next_sample_code(db_path, batch_code: str) -> str:
    """Π.χ. batch Γιώργος-1 → δείγμα Γιώργος-1/S3"""
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT sample_code FROM samples WHERE sample_code LIKE ?",
        (f"{batch_code}/S%",)
    ).fetchall()
    conn.close()
    max_n = 0
    for r in rows:
        try:
            n = int(r[0].split("/S")[-1])
            if n > max_n:
                max_n = n
        except:
            pass
    return f"{batch_code}/S{max_n + 1}"


# ─── DASHBOARD STATS ──────────────────────────────────────────────────────────

def get_dashboard_stats(db_path):
    conn = get_connection(db_path)
    stats = {}
    stats['total_samples'] = conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
    stats['total_batches'] = conn.execute("SELECT COUNT(*) FROM batches").fetchone()[0]
    stats['total_clients'] = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]

    for code, _ in [
        ("RECEIVED","received"), ("IN_ANALYSIS","in_analysis"),
        ("ANALYZED","analyzed"), ("PENDING","pending"),
        ("COMPLETED","completed"), ("SHIPPED","shipped")
    ]:
        n = conn.execute("SELECT COUNT(*) FROM samples WHERE status=?", (code,)).fetchone()[0]
        stats[code.lower()] = n

    # Δείγματα που καθυστερούν (πέρα από expected_days)
    stats['overdue'] = conn.execute("""
        SELECT COUNT(*) FROM samples s
        JOIN analysis_types at ON at.id = s.analysis_type_id
        WHERE s.status NOT IN ('COMPLETED','SHIPPED')
        AND at.expected_days IS NOT NULL
        AND julianday('now') - julianday(s.created_at) > at.expected_days
    """).fetchone()[0]

    conn.close()
    return stats
