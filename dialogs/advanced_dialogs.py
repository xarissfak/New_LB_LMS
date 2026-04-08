"""
advanced_dialogs.py
Προχωρημένοι διάλογοι:
  - Units of Measurement (Μονάδες Μέτρησης)
  - Multi-Select Samples με Range Support
  - Bulk Analysis Assignment
  - Multi-Stage Analysis Configuration
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QPushButton, QLabel, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QListWidget, QListWidgetItem, QCheckBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

from models.crud import (
    get_all_units, add_unit, update_unit, delete_unit,
    get_all_analysis_types, add_analysis_type, update_analysis_type
)


def _btn(text, color, hover, size=32):
    """Βοηθητική συνάρτηση δημιουργίας κουμπιών."""
    b = QPushButton(text)
    b.setMinimumHeight(size)
    b.setStyleSheet(f"""
        QPushButton{{background:{color};color:white;border-radius:6px;
                     font-weight:bold;padding:0 10px;font-size:12px;}}
        QPushButton:hover{{background:{hover};}}
    """)
    return b


# ─── UNITS OF MEASUREMENT DIALOG ──────────────────────────────────────────────

class UnitOfMeasurementDialog(QDialog):
    """Διάλογος προσθήκης / επεξεργασίας Μονάδας Μέτρησης."""

    def __init__(self, parent=None, data: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Μονάδα Μέτρησης" if not data else "Επεξεργασία Μονάδας")
        self.setMinimumWidth(400)
        self.data = data or {}
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        self.name = QLineEdit(self.data.get("name", ""))
        self.name.setPlaceholderText("π.χ. Χιλιόγραμμο")
        self.name.setFocus()

        self.symbol = QLineEdit(self.data.get("symbol", ""))
        self.symbol.setPlaceholderText("π.χ. kg")

        self.category = QLineEdit(self.data.get("category", ""))
        self.category.setPlaceholderText("π.χ. Βάρος, Όγκος, Συγκέντρωση...")

        self.description = QTextEdit(self.data.get("description", ""))
        self.description.setMaximumHeight(70)
        self.description.setPlaceholderText("Προαιρετική περιγραφή...")

        form.addRow("Όνομα *", self.name)
        form.addRow("Σύμβολο *", self.symbol)
        form.addRow("Κατηγορία", self.category)
        form.addRow("Περιγραφή", self.description)

        layout.addLayout(form)

        # Κουμπιά
        btns = QHBoxLayout()
        ok = _btn("Αποθήκευση", "#2ecc71", "#27ae60", 36)
        cancel = _btn("Άκυρο", "#95a5a6", "#7f8c8d", 36)
        ok.clicked.connect(self._accept)
        cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(ok)
        layout.addLayout(btns)

    def _accept(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Υποχρεωτικό", "Το όνομα είναι υποχρεωτικό.")
            self.name.setFocus()
            return
        if not self.symbol.text().strip():
            QMessageBox.warning(self, "Υποχρεωτικό", "Το σύμβολο είναι υποχρεωτικό.")
            self.symbol.setFocus()
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "name": self.name.text().strip(),
            "symbol": self.symbol.text().strip(),
            "category": self.category.text().strip(),
            "description": self.description.toPlainText().strip(),
        }


# ─── UNITS MANAGER DIALOG ─────────────────────────────────────────────────────

class UnitsManagerDialog(QDialog):
    """Διάλογος διαχείρισης όλων των Μονάδων Μέτρησης."""

    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.setWindowTitle("Διαχείριση Μονάδων Μέτρησης")
        self.setMinimumSize(700, 500)
        self._build()
        self._load_units()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Title
        title = QLabel("📐 Μονάδες Μέτρησης")
        f = QFont()
        f.setPointSize(14)
        f.setBold(True)
        title.setFont(f)
        layout.addWidget(title)

        # Toolbar
        toolbar = QHBoxLayout()
        btn_add = _btn("➕ Νέα Μονάδα", "#3498db", "#2980b9")
        btn_edit = _btn("✏️ Επεξεργασία", "#f39c12", "#d68910")
        btn_delete = _btn("🗑 Διαγραφή", "#e74c3c", "#c0392b")
        btn_add.clicked.connect(self._add_unit)
        btn_edit.clicked.connect(self._edit_unit)
        btn_delete.clicked.connect(self._delete_unit)
        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_edit)
        toolbar.addWidget(btn_delete)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Όνομα", "Σύμβολο", "Κατηγορία", "Περιγραφή"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # Close button
        btns = QHBoxLayout()
        btn_close = _btn("Κλείσιμο", "#95a5a6", "#7f8c8d", 36)
        btn_close.clicked.connect(self.accept)
        btns.addStretch()
        btns.addWidget(btn_close)
        layout.addLayout(btns)

    def _load_units(self):
        """Φορτώνει τις μονάδες στον πίνακα."""
        units = get_all_units_no_filter(self.db_path)
        self.table.setRowCount(0)
        for unit in units:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(unit.get("name", "")))
            self.table.setItem(row, 1, QTableWidgetItem(unit.get("symbol", "")))
            self.table.setItem(row, 2, QTableWidgetItem(unit.get("category", "")))
            self.table.setItem(row, 3, QTableWidgetItem(unit.get("description", "")))
            self.table.item(row, 0).setData(Qt.UserRole, unit['id'])

    def _add_unit(self):
        """Προσθέτει νέα μονάδα."""
        dlg = UnitOfMeasurementDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            success, msg = add_unit(
                self.db_path,
                data['name'], data['symbol'],
                data['description'], data['category']
            )
            if success:
                QMessageBox.information(self, "Επιτυχία", "Η μονάδα προστέθηκε με επιτυχία.")
                self._load_units()
            else:
                QMessageBox.critical(self, "Σφάλμα", f"Σφάλμα: {msg}")

    def _edit_unit(self):
        """Επεξεργάζεται την επιλεγμένη μονάδα."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Επιλογή", "Επιλέξτε μια μονάδα.")
            return
        unit_id = self.table.item(row, 0).data(Qt.UserRole)
        # Θα πρέπει να λάβουμε τα δεδομένα της μονάδας από τη βάση
        # Για τώρα, απλά ανοίγουμε το διάλογο για επεξεργασία
        dlg = UnitOfMeasurementDialog(
            self,
            {
                "name": self.table.item(row, 0).text(),
                "symbol": self.table.item(row, 1).text(),
                "category": self.table.item(row, 2).text(),
                "description": self.table.item(row, 3).text(),
            }
        )
        dlg.setWindowTitle("Επεξεργασία Μονάδας Μέτρησης")
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            success, msg = update_unit(
                self.db_path, unit_id,
                data['name'], data['symbol'],
                data['description'], data['category']
            )
            if success:
                QMessageBox.information(self, "Επιτυχία", msg)
                self._load_units()
            else:
                QMessageBox.critical(self, "Σφάλμα", f"Σφάλμα: {msg}")

    def _delete_unit(self):
        """Διαγράφει την επιλεγμένη μονάδα."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Επιλογή", "Επιλέξτε μια μονάδα.")
            return
        unit_name = self.table.item(row, 0).text()
        if QMessageBox.question(
            self, "Διαγραφή",
            f"Είστε σίγουροι ότι θέλετε να διαγράψετε τη μονάδα '{unit_name}';",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            unit_id = self.table.item(row, 0).data(Qt.UserRole)
            delete_unit(self.db_path, unit_id)
            self._load_units()


# ─── SAMPLE RANGE SELECTOR ────────────────────────────────────────────────────

class SampleRangeSelectorDialog(QDialog):
    """Διάλογος επιλογής δειγμάτων με range support (π.χ. 1-4, 7-13)."""

    def __init__(self, db_path, batch_id, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.batch_id = batch_id
        self.setWindowTitle("Επιλογή Δειγμάτων")
        self.setMinimumSize(500, 400)
        self.selected_samples = []
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        info = QLabel("Δώστε εύρη δειγμάτων (π.χ. 1-4, 7-13 ή 1,3,5):")
        layout.addWidget(info)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("π.χ. 1-4, 7-13, 15")
        layout.addWidget(self.input_field)

        # Preview
        self.preview = QLabel()
        self.preview.setStyleSheet("background:#f0f4f8; padding:8px; border-radius:4px; color:#555;")
        self.input_field.textChanged.connect(self._update_preview)
        layout.addWidget(self.preview)

        # Buttons
        btns = QHBoxLayout()
        ok = _btn("Επιλογή", "#2ecc71", "#27ae60")
        cancel = _btn("Άκυρο", "#95a5a6", "#7f8c8d")
        ok.clicked.connect(self._accept)
        cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(ok)
        layout.addLayout(btns)

    def _update_preview(self):
        """Ενημερώνει την προεπισκόπηση των επιλεγμένων δειγμάτων."""
        try:
            self.selected_samples = self._parse_ranges(self.input_field.text())
            preview_text = f"✓ Επιλεγμένα δείγματα ({len(self.selected_samples)}): {sorted(self.selected_samples)}"
            self.preview.setText(preview_text)
            self.preview.setStyleSheet("background:#d5f4e6; padding:8px; border-radius:4px; color:#27ae60; font-weight:bold;")
        except Exception as e:
            self.preview.setText(f"✗ Σφάλμα: {str(e)}")
            self.preview.setStyleSheet("background:#f5d5d5; padding:8px; border-radius:4px; color:#c0392b;")
            self.selected_samples = []

    def _parse_ranges(self, text: str):
        """Αναλύει εύρη δειγμάτων (π.χ. '1-4, 7-13' → [1,2,3,4,7,8,9,10,11,12,13])."""
        if not text.strip():
            return []
        
        samples = set()
        parts = text.replace(" ", "").split(",")
        
        for part in parts:
            if "-" in part:
                start, end = part.split("-")
                for i in range(int(start), int(end) + 1):
                    samples.add(i)
            else:
                samples.add(int(part))
        
        return sorted(list(samples))

    def _accept(self):
        if not self.selected_samples:
            QMessageBox.warning(self, "Επιλογή", "Επιλέξτε τουλάχιστον ένα δείγμα.")
            return
        self.accept()

    def get_selected_samples(self):
        """Επιστρέφει τα επιλεγμένα δείγματα."""
        return self.selected_samples


# ─── BULK ANALYSIS ASSIGNMENT ─────────────────────────────────────────────────

class BulkAnalysisAssignmentDialog(QDialog):
    """Μαζική ανάθεση αναλύσεων σε δείγματα."""

    def __init__(self, db_path, sample_numbers: list, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.sample_numbers = sample_numbers
        self.setWindowTitle(f"Ανάθεση Αναλύσεων — {len(sample_numbers)} δείγματα")
        self.setMinimumSize(450, 350)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        info = QLabel(f"Δείγματα: {', '.join(map(str, self.sample_numbers[:10]))}")
        if len(self.sample_numbers) > 10:
            info.setText(info.text() + "...")
        layout.addWidget(info)

        # Analyses selection
        form = QFormLayout()
        
        self.analysis_list = QListWidget()
        self.analysis_list.setSelectionMode(QAbstractItemView.MultiSelection)
        analyses = get_all_analysis_types(self.db_path)
        
        for a in analyses:
            item = QListWidgetItem(a['name'])
            item.setData(Qt.UserRole, a['id'])
            self.analysis_list.addItem(item)
        
        form.addRow("Επιλέξτε Αναλύσεις *", self.analysis_list)
        layout.addLayout(form)

        # Buttons
        btns = QHBoxLayout()
        ok = _btn("Ανάθεση", "#3498db", "#2980b9")
        cancel = _btn("Άκυρο", "#95a5a6", "#7f8c8d")
        ok.clicked.connect(self._accept)
        cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(ok)
        layout.addLayout(btns)

    def _accept(self):
        if not self.analysis_list.selectedItems():
            QMessageBox.warning(self, "Επιλογή", "Επιλέξτε τουλάχιστον μία ανάλυση.")
            return
        self.accept()

    def get_selected_analyses(self):
        """Επιστρέφει τα IDs των επιλεγμένων αναλύσεων."""
        return [item.data(Qt.UserRole) for item in self.analysis_list.selectedItems()]


# Helper function to import get_all_units_no_filter
from models.crud import get_all_units_no_filter


# ─── MULTI-STAGE ANALYSIS CONFIGURATION ────────────────────────────────────────

class MultiStageAnalysisDialog(QDialog):
    """Διάλογος ρύθμισης πολυ-στάδιων αναλύσεων με σύνθετες παραμέτρους."""

    def __init__(self, parent=None, analysis_data: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Πολύ-Στάδια Ανάλυση")
        self.setMinimumSize(600, 500)
        self.analysis_data = analysis_data or {}
        self.stages = []
        self._build()
        self._load_stages()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Title
        title = QLabel("⚙️ Ρύθμιση Σταδίων Ανάλυσης")
        f = QFont()
        f.setPointSize(12)
        f.setBold(True)
        title.setFont(f)
        layout.addWidget(title)

        # Stages list
        self.stages_list = QListWidget()
        self.stages_list.itemSelectionChanged.connect(self._on_stage_selected)
        layout.addWidget(QLabel("Στάδια:"))
        layout.addWidget(self.stages_list)

        # Stage details panel
        details_frame = QFrame()
        details_frame.setStyleSheet("background:#f9f9f9; border-radius:6px; padding:10px;")
        details_layout = QFormLayout(details_frame)

        self.stage_name = QLineEdit()
        self.stage_name.setPlaceholderText("π.χ. Προετοιμασία θρεπτικού")

        self.stage_temp = QDoubleSpinBox()
        self.stage_temp.setRange(-100, 200)
        self.stage_temp.setSuffix(" °C")
        self.stage_temp.setValue(37)

        self.stage_duration = QDoubleSpinBox()
        self.stage_duration.setRange(0, 9999)
        self.stage_duration.setSuffix(" ώρες")

        self.stage_notes = QTextEdit()
        self.stage_notes.setMaximumHeight(70)

        details_layout.addRow("Όνομα Σταδίου", self.stage_name)
        details_layout.addRow("Θερμοκρασία", self.stage_temp)
        details_layout.addRow("Διάρκεια", self.stage_duration)
        details_layout.addRow("Σημειώσεις", self.stage_notes)

        layout.addWidget(QLabel("Λεπτομέρειες Σταδίου:"))
        layout.addWidget(details_frame)

        # Stage management buttons
        stage_btns = QHBoxLayout()
        btn_add_stage = _btn("➕ Προσθήκη Σταδίου", "#3498db", "#2980b9")
        btn_edit_stage = _btn("✏️ Ενημέρωση", "#f39c12", "#d68910")
        btn_del_stage = _btn("🗑 Διαγραφή", "#e74c3c", "#c0392b")
        btn_add_stage.clicked.connect(self._add_stage)
        btn_edit_stage.clicked.connect(self._update_stage)
        btn_del_stage.clicked.connect(self._delete_stage)
        stage_btns.addWidget(btn_add_stage)
        stage_btns.addWidget(btn_edit_stage)
        stage_btns.addWidget(btn_del_stage)
        stage_btns.addStretch()
        layout.addLayout(stage_btns)

        # Bottom buttons
        btns = QHBoxLayout()
        ok = _btn("Αποθήκευση", "#2ecc71", "#27ae60", 36)
        cancel = _btn("Άκυρο", "#95a5a6", "#7f8c8d", 36)
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(ok)
        layout.addLayout(btns)

    def _load_stages(self):
        """Φορτώνει τα στάδια από τα δεδομένα ανάλυσης."""
        # Για τώρα, αρχικοποιούμε με ένα κενό στάδιο 1
        self.stages = [
            {
                "id": 1,
                "name": "ΣΤΑΔΙΟ: 1",
                "temperature": 37.0,
                "duration": 48.0,
                "notes": ""
            }
        ]
        self._refresh_stages_list()

    def _refresh_stages_list(self):
        """Ανανεώνει τη λίστα σταδίων."""
        self.stages_list.clear()
        for stage in self.stages:
            item = QListWidgetItem(f"{stage['name']}")
            item.setData(Qt.UserRole, stage['id'])
            self.stages_list.addItem(item)

    def _on_stage_selected(self):
        """Φορτώνει τις λεπτομέρειες του επιλεγμένου σταδίου."""
        selected = self.stages_list.selectedItems()
        if not selected:
            return
        stage_id = selected[0].data(Qt.UserRole)
        stage = next((s for s in self.stages if s['id'] == stage_id), None)
        if stage:
            self.stage_name.setText(stage['name'])
            self.stage_temp.setValue(stage.get('temperature', 37.0))
            self.stage_duration.setValue(stage.get('duration', 48.0))
            self.stage_notes.setText(stage.get('notes', ''))

    def _add_stage(self):
        """Προσθέτει νέο στάδιο."""
        new_id = max([s['id'] for s in self.stages], default=0) + 1
        new_stage = {
            "id": new_id,
            "name": f"ΣΤΑΔΙΟ: {new_id}",
            "temperature": 37.0,
            "duration": 48.0,
            "notes": ""
        }
        self.stages.append(new_stage)
        self._refresh_stages_list()
        # Select the new stage
        for i in range(self.stages_list.count()):
            if self.stages_list.item(i).data(Qt.UserRole) == new_id:
                self.stages_list.setCurrentRow(i)
                break

    def _update_stage(self):
        """Ενημερώνει το επιλεγμένο στάδιο."""
        selected = self.stages_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Επιλογή", "Επιλέξτε ένα στάδιο.")
            return
        stage_id = selected[0].data(Qt.UserRole)
        stage = next((s for s in self.stages if s['id'] == stage_id), None)
        if stage:
            stage['name'] = self.stage_name.text() or f"ΣΤΑΔΙΟ: {stage_id}"
            stage['temperature'] = self.stage_temp.value()
            stage['duration'] = self.stage_duration.value()
            stage['notes'] = self.stage_notes.toPlainText()
            self._refresh_stages_list()
            # Re-select the stage
            for i in range(self.stages_list.count()):
                if self.stages_list.item(i).data(Qt.UserRole) == stage_id:
                    self.stages_list.setCurrentRow(i)
                    break

    def _delete_stage(self):
        """Διαγράφει το επιλεγμένο στάδιο."""
        selected = self.stages_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Επιλογή", "Επιλέξτε ένα στάδιο.")
            return
        if len(self.stages) <= 1:
            QMessageBox.warning(self, "Σφάλμα", "Πρέπει να υπάρχει τουλάχιστον ένα στάδιο.")
            return
        stage_id = selected[0].data(Qt.UserRole)
        self.stages = [s for s in self.stages if s['id'] != stage_id]
        self._refresh_stages_list()

    def get_stages(self):
        """Επιστρέφει τα στάδια."""
        return self.stages

