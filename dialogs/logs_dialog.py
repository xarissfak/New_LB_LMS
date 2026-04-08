"""
logs_dialog.py
Διάλογος προεπισκόπησης και διαχείρισης Action Logs.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QComboBox, QMessageBox, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from datetime import datetime
import json

from logs.action_logger import get_logger


class ActionLogsDialog(QDialog):
    """Διάλογος για προεπισκόπηση των action logs."""

    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.logger = get_logger(db_path)
        self.setWindowTitle("📋 Action Logs — Ιστορικό Ενεργειών")
        self.setMinimumSize(900, 600)
        self._build()
        self._load_logs()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Title
        title = QLabel("📋 Action Logs — Ιστορικό Ενεργειών")
        f = QFont()
        f.setPointSize(14)
        f.setBold(True)
        title.setFont(f)
        layout.addWidget(title)

        # Filters
        filters_layout = QHBoxLayout()
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("Όλες οι κατηγορίες", None)
        self.category_filter.addItem("BATCH", "BATCH")
        self.category_filter.addItem("SAMPLE", "SAMPLE")
        self.category_filter.addItem("ANALYSIS", "ANALYSIS")
        self.category_filter.addItem("UNIT", "UNIT")
        self.category_filter.currentIndexChanged.connect(self._load_logs)

        self.status_filter = QComboBox()
        self.status_filter.addItem("Όλα", None)
        self.status_filter.addItem("SUCCESS", "SUCCESS")
        self.status_filter.addItem("ERROR", "ERROR")
        self.status_filter.addItem("PENDING", "PENDING")
        self.status_filter.currentIndexChanged.connect(self._load_logs)

        filters_layout.addWidget(QLabel("Κατηγορία:"))
        filters_layout.addWidget(self.category_filter)
        filters_layout.addWidget(QLabel("Κατάσταση:"))
        filters_layout.addWidget(self.status_filter)
        filters_layout.addStretch()
        layout.addLayout(filters_layout)

        # Logs table
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(7)
        self.logs_table.setHorizontalHeaderLabels([
            "Ώρα", "Ενέργεια", "Κατηγορία", "Κατάσταση", "Οντότητα", "Χρήστης", "Σχόλια"
        ])
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.logs_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.logs_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.logs_table.setAlternatingRowColors(True)
        self.logs_table.verticalHeader().setVisible(False)
        self.logs_table.itemSelectionChanged.connect(self._show_details)
        layout.addWidget(self.logs_table)

        # Details panel
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setMaximumHeight(150)
        layout.addWidget(QLabel("Λεπτομέρειες:"))
        layout.addWidget(self.details)

        # Buttons
        btns = QHBoxLayout()
        btn_refresh = self._make_btn("🔄 Ανανέωση", "#3498db", "#2980b9")
        btn_clear_errors = self._make_btn("🗑 Καθαρισμός Σφαλμάτων", "#e74c3c", "#c0392b")
        btn_close = self._make_btn("Κλείσιμο", "#95a5a6", "#7f8c8d")
        btn_refresh.clicked.connect(self._load_logs)
        btn_clear_errors.clicked.connect(self._clear_errors)
        btn_close.clicked.connect(self.accept)
        btns.addWidget(btn_refresh)
        btns.addWidget(btn_clear_errors)
        btns.addStretch()
        btns.addWidget(btn_close)
        layout.addLayout(btns)

    def _make_btn(self, text, color, hover):
        btn = QPushButton(text)
        btn.setMinimumHeight(36)
        btn.setStyleSheet(f"""
            QPushButton {{background:{color};color:white;border-radius:6px;
                         font-weight:bold;padding:0 14px;}}
            QPushButton:hover{{background:{hover};}}
        """)
        return btn

    def _load_logs(self):
        """Φορτώνει τα logs με βάση τα φίλτρα."""
        category = self.category_filter.currentData()
        status = self.status_filter.currentData()
        
        logs = self.logger.get_logs(limit=200, category=category, status=status)
        
        self.logs_table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            # Χρώμα γραμμής βάσει κατάστασης
            if log['status'] == 'ERROR':
                color = QColor('#ffcccc')
            elif log['status'] == 'PENDING':
                color = QColor('#ffffcc')
            else:
                color = QColor('#ffffff')
            
            self.logs_table.setItem(row, 0, QTableWidgetItem(log['timestamp'][-8:]))  # Ώρα
            self.logs_table.setItem(row, 1, QTableWidgetItem(log['action']))
            self.logs_table.setItem(row, 2, QTableWidgetItem(log['category']))
            
            status_item = QTableWidgetItem(log['status'])
            status_item.setBackground(color)
            self.logs_table.setItem(row, 3, status_item)
            
            self.logs_table.setItem(row, 4, QTableWidgetItem(f"{log.get('entity_type', '')} #{log.get('entity_id', '')}"))
            self.logs_table.setItem(row, 5, QTableWidgetItem(log.get('user', '') or "—"))
            self.logs_table.setItem(row, 6, QTableWidgetItem(log.get('details', '') or ""))
            
            # Store full log data
            self.logs_table.item(row, 0).setData(Qt.UserRole, log)

    def _show_details(self):
        """Εμφανίζει τις λεπτομέρειες του επιλεγμένου log."""
        selected = self.logs_table.selectedItems()
        if not selected:
            self.details.clear()
            return

        log = selected[0].data(Qt.UserRole)
        
        details_text = f"""
        <b>Ενέργεια:</b> {log['action']}<br>
        <b>Κατηγορία:</b> {log['category']}<br>
        <b>Κατάσταση:</b> {log['status']}<br>
        <b>Timestamp:</b> {log['timestamp']}<br>
        <b>Χρήστης:</b> {log.get('user', '—')}<br>
        <b>Οντότητα:</b> {log.get('entity_type', '—')} (ID: {log.get('entity_id', '—')})<br>
        <b>Σημειώσεις:</b> {log.get('details', '—')}<br>
        """
        
        if log.get('error_msg'):
            details_text += f"<b style='color:red;'>Σφάλμα:</b> {log['error_msg']}<br>"
        
        if log.get('old_data'):
            old_data = json.loads(log['old_data'])
            details_text += f"<b>Παλιά Δεδομένα:</b><pre>{json.dumps(old_data, indent=2, ensure_ascii=False)}</pre>"
        
        if log.get('new_data'):
            new_data = json.loads(log['new_data'])
            details_text += f"<b>Νέα Δεδομένα:</b><pre>{json.dumps(new_data, indent=2, ensure_ascii=False)}</pre>"
        
        self.details.setHtml(details_text)

    def _clear_errors(self):
        """Διαγράφει τα παλιά logs."""
        if QMessageBox.question(
            self, "Επιβεβαίωση",
            "Θέλετε να διαγράψετε όλα τα logs παλιότερα από 30 ημέρες;",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            self.logger.clear_old_logs(days=30)
            self._load_logs()
            QMessageBox.information(self, "Επιτυχία", "Τα παλιά logs διαγράφηκαν.")
