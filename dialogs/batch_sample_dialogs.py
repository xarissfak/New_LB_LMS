"""
batch_sample_dialogs.py
Διάλογοι για Batch και Sample creation / status update / result entry.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QDateEdit,
    QPushButton, QLabel, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QSplitter,
    QListWidget, QListWidgetItem, QAbstractItemView
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont

from database.db_manager import STATUSES, STATUS_COLORS, status_label
from models.crud import (
    get_all_clients, get_all_analysts, get_all_analysis_types,
    next_batch_code, next_sample_code, get_sample_history
)


def _btn(text, color, hover):
    b = QPushButton(text)
    b.setMinimumHeight(34)
    b.setStyleSheet(f"""
        QPushButton {{background:{color};color:white;border-radius:6px;font-weight:bold;padding:0 14px;}}
        QPushButton:hover{{background:{hover};}}
    """)
    return b


# ─── BATCH DIALOG ─────────────────────────────────────────────────────────────

class BatchDialog(QDialog):
    """Δημιουργία νέου Batch."""

    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.setWindowTitle("Νέο Batch")
        self.setMinimumWidth(420)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        # Πελάτης
        self.client_combo = QComboBox()
        self.clients = get_all_clients(self.db_path)
        for c in self.clients:
            label = f"{c['name']}" + (f" [{c['code']}]" if c['code'] else "")
            self.client_combo.addItem(label, c['id'])
        self.client_combo.currentIndexChanged.connect(self._update_batch_code)

        # Batch Code (αυτόματο αλλά επεξεργάσιμο)
        self.batch_code = QLineEdit()
        self.batch_code.setPlaceholderText("Αυτόματη παραγωγή...")

        # Ημερομηνία παραλαβής
        self.received_date = QDateEdit(QDate.currentDate())
        self.received_date.setCalendarPopup(True)
        self.received_date.setDisplayFormat("dd/MM/yyyy")

        self.notes = QTextEdit()
        self.notes.setMaximumHeight(60)
        self.notes.setPlaceholderText("Σημειώσεις batch...")

        form.addRow("Πελάτης *", self.client_combo)
        form.addRow("Κωδικός Batch", self.batch_code)
        form.addRow("Ημ. Παραλαβής", self.received_date)
        form.addRow("Σημειώσεις", self.notes)

        layout.addLayout(form)

        # Κουμπιά
        btns = QHBoxLayout()
        ok = _btn("Δημιουργία Batch", "#3498db", "#2980b9")
        cancel = _btn("Άκυρο", "#95a5a6", "#7f8c8d")
        ok.clicked.connect(self._accept)
        cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(ok)
        layout.addLayout(btns)

        self._update_batch_code()

    def _update_batch_code(self):
        idx = self.client_combo.currentIndex()
        if idx < 0 or not self.clients:
            return
        client = self.clients[idx]
        identifier = client['code'] if client['code'] else client['name'].split()[0]
        suggested = next_batch_code(self.db_path, identifier)
        self.batch_code.setText(suggested)

    def _accept(self):
        if not self.batch_code.text().strip():
            QMessageBox.warning(self, "Υποχρεωτικό", "Ο κωδικός batch είναι υποχρεωτικός.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "batch_code": self.batch_code.text().strip(),
            "client_id": self.client_combo.currentData(),
            "received_date": self.received_date.date().toString("yyyy-MM-dd"),
            "notes": self.notes.toPlainText().strip(),
        }


# ─── ADD SAMPLE DIALOG ────────────────────────────────────────────────────────

class AddSampleDialog(QDialog):
    """Προσθήκη δείγματος/ων σε batch."""

    def __init__(self, db_path, batch_code, batch_id, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.batch_code = batch_code
        self.batch_id = batch_id
        self.setWindowTitle(f"Προσθήκη Δειγμάτων — {batch_code}")
        self.setMinimumWidth(480)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        # Κωδικός δείγματος
        self.sample_code = QLineEdit()
        suggested = next_sample_code(self.db_path, self.batch_code)
        self.sample_code.setText(suggested)

        # Ανάλυση
        self.analysis_combo = QComboBox()
        self.analyses = get_all_analysis_types(self.db_path)
        for a in self.analyses:
            info = f"{a['name']}"
            if a['expected_days']:
                info += f" ({a['expected_days']}d)"
            self.analysis_combo.addItem(info, a['id'])

        self.notes = QTextEdit()
        self.notes.setMaximumHeight(55)
        self.notes.setPlaceholderText("Σημειώσεις δείγματος...")

        form.addRow("Κωδικός Δείγματος *", self.sample_code)
        form.addRow("Ανάλυση *", self.analysis_combo)
        form.addRow("Σημειώσεις", self.notes)

        layout.addLayout(form)

        # Info για επιλεγμένη ανάλυση
        self.analysis_info = QLabel()
        self.analysis_info.setStyleSheet(
            "background:#f0f4f8; border-radius:6px; padding:8px; color:#444; font-size:12px;"
        )
        self.analysis_info.setWordWrap(True)
        self.analysis_combo.currentIndexChanged.connect(self._show_analysis_info)
        layout.addWidget(self.analysis_info)

        btns = QHBoxLayout()
        ok = _btn("Προσθήκη Δείγματος", "#2ecc71", "#27ae60")
        ok_more = _btn("Προσθήκη & Νέο", "#e67e22", "#d35400")
        cancel = _btn("Κλείσιμο", "#95a5a6", "#7f8c8d")
        ok.clicked.connect(self._accept_one)
        ok_more.clicked.connect(self._accept_more)
        cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(ok_more)
        btns.addWidget(ok)
        layout.addLayout(btns)

        self._show_analysis_info()

    def _show_analysis_info(self):
        idx = self.analysis_combo.currentIndex()
        if idx < 0 or not self.analyses:
            return
        a = self.analyses[idx]
        parts = []
        if a.get('incubation_hours'):
            parts.append(f"⏱ Επώαση: {a['incubation_hours']}h")
        if a.get('temperature_c'):
            parts.append(f"🌡 Θερμ.: {a['temperature_c']}°C")
        if a.get('expected_days'):
            parts.append(f"📅 Αναμ. ολοκλ.: {a['expected_days']} ημέρες")
        if a.get('unit'):
            parts.append(f"📐 Μονάδα: {a['unit']}")
        self.analysis_info.setText("  |  ".join(parts) if parts else "Δεν υπάρχουν λεπτομέρειες.")

    def _accept_one(self):
        if self._validate():
            self.add_more = False
            self.accept()

    def _accept_more(self):
        if self._validate():
            self.add_more = True
            self.accept()

    def _validate(self):
        if not self.sample_code.text().strip():
            QMessageBox.warning(self, "Υποχρεωτικό", "Ο κωδικός δείγματος είναι υποχρεωτικός.")
            return False
        if not self.analyses:
            QMessageBox.warning(self, "Χωρίς Αναλύσεις", "Δεν υπάρχουν είδη ανάλυσης. Προσθέστε πρώτα.")
            return False
        return True

    def get_data(self) -> dict:
        return {
            "sample_code": self.sample_code.text().strip(),
            "batch_id": self.batch_id,
            "analysis_type_id": self.analysis_combo.currentData(),
            "notes": self.notes.toPlainText().strip(),
        }


# ─── STATUS UPDATE DIALOG ─────────────────────────────────────────────────────

class StatusUpdateDialog(QDialog):
    """Αλλαγή κατάστασης δείγματος με επιλογή αναλυτή."""

    def __init__(self, db_path, sample: dict, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.sample = sample
        self.setWindowTitle(f"Ενημέρωση Κατάστασης — {sample['sample_code']}")
        self.setMinimumWidth(400)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Τρέχουσα κατάσταση
        cur = QLabel(f"Τρέχουσα κατάσταση: {status_label(self.sample['status'])}")
        cur.setStyleSheet("font-weight:bold; color:#555;")
        layout.addWidget(cur)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        # Νέα κατάσταση
        self.status_combo = QComboBox()
        current_idx = 0
        for i, (code, label) in enumerate(STATUSES):
            self.status_combo.addItem(label, code)
            if code == self.sample['status']:
                current_idx = i
        self.status_combo.setCurrentIndex(min(current_idx + 1, len(STATUSES) - 1))

        # Αναλυτής
        self.analyst_combo = QComboBox()
        self.analyst_combo.addItem("— Δεν ορίζεται —", None)
        self.analysts = get_all_analysts(self.db_path, active_only=True)
        for a in self.analysts:
            self.analyst_combo.addItem(a['name'], a['id'])
        # Προεπιλογή τρέχοντος αναλυτή
        if self.sample.get('assigned_analyst_id'):
            for i in range(self.analyst_combo.count()):
                if self.analyst_combo.itemData(i) == self.sample['assigned_analyst_id']:
                    self.analyst_combo.setCurrentIndex(i)
                    break

        self.notes = QTextEdit()
        self.notes.setMaximumHeight(55)
        self.notes.setPlaceholderText("Σημείωση για αυτή την αλλαγή...")

        form.addRow("Νέα Κατάσταση", self.status_combo)
        form.addRow("Αναλυτής", self.analyst_combo)
        form.addRow("Σημείωση", self.notes)
        layout.addLayout(form)

        btns = QHBoxLayout()
        ok = _btn("Αποθήκευση", "#3498db", "#2980b9")
        cancel = _btn("Άκυρο", "#95a5a6", "#7f8c8d")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(ok)
        layout.addLayout(btns)

    def get_data(self) -> dict:
        return {
            "status": self.status_combo.currentData(),
            "analyst_id": self.analyst_combo.currentData(),
            "notes": self.notes.toPlainText().strip(),
        }


# ─── RESULT DIALOG ────────────────────────────────────────────────────────────

class ResultDialog(QDialog):
    """Εισαγωγή αποτελέσματος ανάλυσης."""

    def __init__(self, db_path, sample: dict, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.sample = sample
        self.setWindowTitle(f"Αποτέλεσμα — {sample['sample_code']}")
        self.setMinimumWidth(420)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        info = QLabel(f"Ανάλυση: {self.sample.get('analysis_name', '')} | "
                      f"Batch: {self.sample.get('batch_code', '')}")
        info.setStyleSheet("color:#555; font-size:12px;")
        layout.addWidget(info)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        self.result_value = QLineEdit(self.sample.get("result_value") or "")
        self.result_value.setPlaceholderText("π.χ. 150, <10, Αρνητικό...")

        self.analyst_combo = QComboBox()
        self.analyst_combo.addItem("— Δεν ορίζεται —", None)
        self.analysts = get_all_analysts(self.db_path, active_only=True)
        for a in self.analysts:
            self.analyst_combo.addItem(a['name'], a['id'])
        if self.sample.get('assigned_analyst_id'):
            for i in range(self.analyst_combo.count()):
                if self.analyst_combo.itemData(i) == self.sample['assigned_analyst_id']:
                    self.analyst_combo.setCurrentIndex(i)
                    break

        self.result_notes = QTextEdit(self.sample.get("result_notes") or "")
        self.result_notes.setMinimumHeight(80)
        self.result_notes.setPlaceholderText("Παρατηρήσεις αποτελέσματος...")

        form.addRow("Αποτέλεσμα *", self.result_value)
        form.addRow("Αναλυτής", self.analyst_combo)
        form.addRow("Παρατηρήσεις", self.result_notes)
        layout.addLayout(form)

        btns = QHBoxLayout()
        ok = _btn("Αποθήκευση Αποτελέσματος", "#9b59b6", "#8e44ad")
        cancel = _btn("Άκυρο", "#95a5a6", "#7f8c8d")
        ok.clicked.connect(self._accept)
        cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(ok)
        layout.addLayout(btns)

    def _accept(self):
        if not self.result_value.text().strip():
            QMessageBox.warning(self, "Υποχρεωτικό", "Συμπληρώστε την τιμή αποτελέσματος.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "result_value": self.result_value.text().strip(),
            "analyst_id": self.analyst_combo.currentData(),
            "result_notes": self.result_notes.toPlainText().strip(),
        }


# ─── HISTORY DIALOG ───────────────────────────────────────────────────────────

class HistoryDialog(QDialog):
    """Ιστορικό κινήσεων δείγματος."""

    def __init__(self, db_path, sample: dict, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.sample = sample
        self.setWindowTitle(f"Ιστορικό — {sample['sample_code']}")
        self.setMinimumSize(560, 360)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        info = QLabel(
            f"<b>{self.sample['sample_code']}</b> | "
            f"Ανάλυση: {self.sample.get('analysis_name','')} | "
            f"Batch: {self.sample.get('batch_code','')} | "
            f"Πελάτης: {self.sample.get('client_name','')}"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Ημ/νία", "Κατάσταση", "Αναλυτής", "Σημείωση"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)

        history = get_sample_history(self.db_path, self.sample['id'])
        table.setRowCount(len(history))
        for row, h in enumerate(history):
            table.setItem(row, 0, QTableWidgetItem(h['timestamp']))
            status_item = QTableWidgetItem(status_label(h['status']))
            color = STATUS_COLORS.get(h['status'], '#ccc')
            status_item.setForeground(QColor("white"))
            status_item.setBackground(QColor(color))
            table.setItem(row, 1, status_item)
            table.setItem(row, 2, QTableWidgetItem(h.get('analyst_name') or "—"))
            table.setItem(row, 3, QTableWidgetItem(h.get('notes') or ""))

        layout.addWidget(table)

        close = _btn("Κλείσιμο", "#95a5a6", "#7f8c8d")
        close.clicked.connect(self.accept)
        layout.addWidget(close, alignment=Qt.AlignRight)
