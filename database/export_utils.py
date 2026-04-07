"""
export_utils.py
Export δεδομένων σε CSV και Excel.
"""

import csv
import os
from datetime import datetime
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from database.db_manager import status_label
from models.crud import get_all_samples, get_all_batches, get_sample_history


def _timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def export_samples_csv(db_path: str, parent=None):
    """Export όλων των δειγμάτων σε CSV."""
    path, _ = QFileDialog.getSaveFileName(
        parent, "Export Δειγμάτων σε CSV",
        f"samples_{_timestamp()}.csv",
        "CSV Files (*.csv)"
    )
    if not path:
        return

    samples = get_all_samples(db_path)
    headers = [
        "Κωδικός Δείγματος", "Batch", "Πελάτης", "Ανάλυση",
        "Κατάσταση", "Αναλυτής", "Αποτέλεσμα",
        "Παρατηρήσεις Αποτελέσματος", "Ημ. Αποτελέσματος",
        "Ημ. Εισαγωγής", "Τελ. Ενημέρωση"
    ]

    try:
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for s in samples:
                writer.writerow([
                    s['sample_code'],
                    s['batch_code'],
                    s['client_name'],
                    s['analysis_name'],
                    status_label(s['status']),
                    s.get('analyst_name') or "",
                    s.get('result_value') or "",
                    s.get('result_notes') or "",
                    s.get('result_at') or "",
                    s['created_at'],
                    s['updated_at'],
                ])
        QMessageBox.information(parent, "Export", f"Εξήχθησαν {len(samples)} δείγματα.\n{path}")
    except Exception as e:
        QMessageBox.critical(parent, "Σφάλμα Export", str(e))


def export_batches_csv(db_path: str, parent=None):
    """Export συνόψεως Batches σε CSV."""
    path, _ = QFileDialog.getSaveFileName(
        parent, "Export Batches σε CSV",
        f"batches_{_timestamp()}.csv",
        "CSV Files (*.csv)"
    )
    if not path:
        return

    batches = get_all_batches(db_path)
    headers = ["Κωδικός Batch", "Πελάτης", "Κωδικός Πελάτη", "Ημ. Παραλαβής", "Αρ. Δειγμάτων", "Σημειώσεις"]

    try:
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for b in batches:
                writer.writerow([
                    b['batch_code'],
                    b['client_name'],
                    b.get('client_code') or "",
                    b['received_date'],
                    b['sample_count'],
                    b.get('notes') or "",
                ])
        QMessageBox.information(parent, "Export", f"Εξήχθησαν {len(batches)} batches.\n{path}")
    except Exception as e:
        QMessageBox.critical(parent, "Σφάλμα Export", str(e))


def export_history_csv(db_path: str, sample: dict, parent=None):
    """Export ιστορικού συγκεκριμένου δείγματος."""
    path, _ = QFileDialog.getSaveFileName(
        parent, f"Export Ιστορικού — {sample['sample_code']}",
        f"history_{sample['sample_code'].replace('/', '_')}_{_timestamp()}.csv",
        "CSV Files (*.csv)"
    )
    if not path:
        return

    history = get_sample_history(db_path, sample['id'])
    headers = ["Timestamp", "Κατάσταση", "Αναλυτής", "Σημείωση"]

    try:
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for h in history:
                writer.writerow([
                    h['timestamp'],
                    status_label(h['status']),
                    h.get('analyst_name') or "",
                    h.get('notes') or "",
                ])
        QMessageBox.information(parent, "Export", f"Εξήχθη ιστορικό {len(history)} εγγραφών.\n{path}")
    except Exception as e:
        QMessageBox.critical(parent, "Σφάλμα Export", str(e))
