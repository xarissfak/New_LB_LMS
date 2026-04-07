"""
master_dialogs.py
Διάλογοι εισαγωγής/επεξεργασίας Master Data:
  ClientDialog, AnalystDialog, AnalysisTypeDialog
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QDoubleSpinBox, QSpinBox,
    QPushButton, QLabel, QMessageBox, QDialogButtonBox
)
from PyQt5.QtCore import Qt


def _styled_btn(text, color, hover):
    btn = QPushButton(text)
    btn.setMinimumHeight(36)
    btn.setStyleSheet(f"""
        QPushButton {{background:{color}; color:white; border-radius:6px; font-weight:bold; padding:0 16px;}}
        QPushButton:hover {{background:{hover};}}
    """)
    return btn


# ─── CLIENT ───────────────────────────────────────────────────────────────────

class ClientDialog(QDialog):
    """Διάλογος προσθήκης / επεξεργασίας Πελάτη."""

    def __init__(self, parent=None, data: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Πελάτης" if not data else "Επεξεργασία Πελάτη")
        self.setMinimumWidth(400)
        self.data = data or {}
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        self.name = QLineEdit(self.data.get("name", ""))
        self.name.setPlaceholderText("π.χ. Γεώργιος Παπαδόπουλος  *")
        self.code = QLineEdit(self.data.get("code", ""))
        self.code.setPlaceholderText("π.χ. 14055")
        self.contact = QLineEdit(self.data.get("contact", ""))
        self.email = QLineEdit(self.data.get("email", ""))
        self.phone = QLineEdit(self.data.get("phone", ""))
        self.notes = QTextEdit(self.data.get("notes", ""))
        self.notes.setMaximumHeight(70)

        form.addRow("Όνομα *", self.name)
        form.addRow("Κωδικός", self.code)
        form.addRow("Επαφή", self.contact)
        form.addRow("Email", self.email)
        form.addRow("Τηλέφωνο", self.phone)
        form.addRow("Σημειώσεις", self.notes)

        layout.addLayout(form)

        btns = QHBoxLayout()
        ok = _styled_btn("Αποθήκευση", "#2ecc71", "#27ae60")
        cancel = _styled_btn("Άκυρο", "#95a5a6", "#7f8c8d")
        ok.clicked.connect(self._accept)
        cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(ok)
        layout.addLayout(btns)

    def _accept(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Υποχρεωτικό", "Το πεδίο Όνομα είναι υποχρεωτικό.")
            self.name.setFocus()
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "name": self.name.text().strip(),
            "code": self.code.text().strip(),
            "contact": self.contact.text().strip(),
            "email": self.email.text().strip(),
            "phone": self.phone.text().strip(),
            "notes": self.notes.toPlainText().strip(),
        }


# ─── ANALYST ──────────────────────────────────────────────────────────────────

class AnalystDialog(QDialog):
    """Διάλογος προσθήκης / επεξεργασίας Αναλυτή."""

    def __init__(self, parent=None, data: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Αναλυτής" if not data else "Επεξεργασία Αναλυτή")
        self.setMinimumWidth(380)
        self.data = data or {}
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        self.name = QLineEdit(self.data.get("name", ""))
        self.name.setPlaceholderText("π.χ. Μαρία Κωνσταντίνου  *")
        self.email = QLineEdit(self.data.get("email", ""))
        self.phone = QLineEdit(self.data.get("phone", ""))
        self.notes = QTextEdit(self.data.get("notes", ""))
        self.notes.setMaximumHeight(60)

        form.addRow("Όνομα *", self.name)
        form.addRow("Email", self.email)
        form.addRow("Τηλέφωνο", self.phone)
        form.addRow("Σημειώσεις", self.notes)

        layout.addLayout(form)

        btns = QHBoxLayout()
        ok = _styled_btn("Αποθήκευση", "#2ecc71", "#27ae60")
        cancel = _styled_btn("Άκυρο", "#95a5a6", "#7f8c8d")
        ok.clicked.connect(self._accept)
        cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(ok)
        layout.addLayout(btns)

    def _accept(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Υποχρεωτικό", "Το πεδίο Όνομα είναι υποχρεωτικό.")
            self.name.setFocus()
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "name": self.name.text().strip(),
            "email": self.email.text().strip(),
            "phone": self.phone.text().strip(),
            "notes": self.notes.toPlainText().strip(),
        }


# ─── ANALYSIS TYPE ────────────────────────────────────────────────────────────

class AnalysisTypeDialog(QDialog):
    """Διάλογος προσθήκης / επεξεργασίας Είδους Ανάλυσης."""

    def __init__(self, parent=None, data: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Είδος Ανάλυσης" if not data else "Επεξεργασία Ανάλυσης")
        self.setMinimumWidth(440)
        self.data = data or {}
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        self.name = QLineEdit(self.data.get("name", ""))
        self.name.setPlaceholderText("π.χ. Μικροβιολογική Ανάλυση  *")

        self.description = QLineEdit(self.data.get("description", ""))

        self.incubation = QDoubleSpinBox()
        self.incubation.setRange(0, 9999)
        self.incubation.setDecimals(1)
        self.incubation.setSuffix(" ώρες")
        self.incubation.setValue(float(self.data.get("incubation_hours") or 0))

        self.temperature = QDoubleSpinBox()
        self.temperature.setRange(-100, 200)
        self.temperature.setDecimals(1)
        self.temperature.setSuffix(" °C")
        self.temperature.setValue(float(self.data.get("temperature_c") or 37))

        self.expected_days = QSpinBox()
        self.expected_days.setRange(0, 365)
        self.expected_days.setSuffix(" ημέρες")
        self.expected_days.setValue(int(self.data.get("expected_days") or 0))

        self.unit = QLineEdit(self.data.get("unit", ""))
        self.unit.setPlaceholderText("π.χ. CFU/mL, mg/L, %")

        self.stages = QTextEdit(self.data.get("stages", ""))
        self.stages.setPlaceholderText(
            "Περιγράψτε τα στάδια της ανάλυσης...\n"
            "π.χ. 1. Προετοιμασία θρεπτικού\n2. Επίστρωση\n3. Επώαση 37°C/48h"
        )
        self.stages.setMinimumHeight(90)

        self.notes = QTextEdit(self.data.get("notes", ""))
        self.notes.setMaximumHeight(60)
        self.notes.setPlaceholderText("Γενικές σημειώσεις...")

        form.addRow("Όνομα Ανάλυσης *", self.name)
        form.addRow("Περιγραφή", self.description)
        form.addRow("Χρόνος Επώασης", self.incubation)
        form.addRow("Θερμοκρασία", self.temperature)
        form.addRow("Αναμ. Ολοκλήρωση", self.expected_days)
        form.addRow("Μονάδα", self.unit)
        form.addRow("Στάδια", self.stages)
        form.addRow("Σημειώσεις", self.notes)

        layout.addLayout(form)

        btns = QHBoxLayout()
        ok = _styled_btn("Αποθήκευση", "#2ecc71", "#27ae60")
        cancel = _styled_btn("Άκυρο", "#95a5a6", "#7f8c8d")
        ok.clicked.connect(self._accept)
        cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(ok)
        layout.addLayout(btns)

    def _accept(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Υποχρεωτικό", "Το πεδίο Όνομα είναι υποχρεωτικό.")
            self.name.setFocus()
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "name": self.name.text().strip(),
            "description": self.description.text().strip(),
            "incubation_hours": self.incubation.value() or None,
            "temperature_c": self.temperature.value() or None,
            "expected_days": self.expected_days.value() or None,
            "unit": self.unit.text().strip(),
            "stages": self.stages.toPlainText().strip(),
            "notes": self.notes.toPlainText().strip(),
        }
