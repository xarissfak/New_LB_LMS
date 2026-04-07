"""
startup_dialog.py
Οθόνη εκκίνησης: Νέα Βάση ή Import Βάσης.
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.db_manager import create_new_database, validate_and_migrate


class StartupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.selected_db_path = None
        self.setWindowTitle("LabTrack — Εκκίνηση")
        self.setMinimumSize(480, 320)
        self.setWindowFlags(Qt.WindowType.Dialog)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Τίτλος
        title = QLabel("🧪 LabTrack")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont()
        f.setPointSize(26)
        f.setBold(True)
        title.setFont(f)

        subtitle = QLabel("Σύστημα Διαχείρισης Δειγμάτων Εργαστηρίου")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-size: 13px;")

        # Διαχωριστής
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #ddd;")

        # Κουμπιά
        btn_new = QPushButton("➕  Νέα Βάση Δεδομένων")
        btn_new.setMinimumHeight(54)
        btn_new.setStyleSheet("""
            QPushButton {
                background: #2ecc71; color: white; border-radius: 8px;
                font-size: 15px; font-weight: bold;
            }
            QPushButton:hover { background: #27ae60; }
        """)
        btn_new.clicked.connect(self._new_database)

        btn_import = QPushButton("📂  Import Υπάρχουσας Βάσης")
        btn_import.setMinimumHeight(54)
        btn_import.setStyleSheet("""
            QPushButton {
                background: #3498db; color: white; border-radius: 8px;
                font-size: 15px; font-weight: bold;
            }
            QPushButton:hover { background: #2980b9; }
        """)
        btn_import.clicked.connect(self._import_database)

        btn_exit = QPushButton("Έξοδος")
        btn_exit.setStyleSheet("color: #999; border: none; font-size: 12px;")
        btn_exit.clicked.connect(self.reject)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(line)
        layout.addWidget(btn_new)
        layout.addWidget(btn_import)
        layout.addStretch()
        layout.addWidget(btn_exit, alignment=Qt.AlignmentFlag.AlignCenter)

    def _new_database(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Αποθήκευση Νέας Βάσης", "lab_data.db",
            "SQLite Database (*.db)"
        )
        if not path:
            return
        try:
            create_new_database(path)
            self.selected_db_path = path
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Σφάλμα", f"Αδυναμία δημιουργίας βάσης:\n{e}")

    def _import_database(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Επιλογή Βάσης Δεδομένων", "",
            "SQLite Database (*.db)"
        )
        if not path:
            return
        ok, msg = validate_and_migrate(path)
        if not ok:
            QMessageBox.warning(
                self, "Πρόβλημα Βάσης",
                f"Η βάση δεν είναι συμβατή:\n{msg}\n\nΠροσπαθήστε με άλλο αρχείο."
            )
            return
        self.selected_db_path = path
        self.accept()
