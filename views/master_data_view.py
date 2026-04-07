"""
master_data_view.py
Οθόνη διαχείρισης Master Data (Πελάτες, Αναλυτές, Αναλύσεις).
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from models.crud import (
    get_all_clients, add_client, update_client, delete_client,
    get_all_analysts, add_analyst, update_analyst, delete_analyst,
    get_all_analysis_types, add_analysis_type, update_analysis_type, delete_analysis_type,
)
from dialogs.master_dialogs import ClientDialog, AnalystDialog, AnalysisTypeDialog


def _btn(text, color, hover, size=32):
    b = QPushButton(text)
    b.setMinimumHeight(size)
    b.setStyleSheet(f"""
        QPushButton{{background:{color};color:white;border-radius:6px;font-weight:bold;padding:0 12px;}}
        QPushButton:hover{{background:{hover};}}
    """)
    return b


class MasterDataView(QWidget):
    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("⚙️ Master Data — Βασικές Ρυθμίσεις")
        f = QFont()
        f.setPointSize(16)
        f.setBold(True)
        title.setFont(f)
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.addTab(self._build_clients_tab(), "👥 Πελάτες")
        tabs.addTab(self._build_analysts_tab(), "🔬 Αναλυτές")
        tabs.addTab(self._build_analysis_types_tab(), "🧪 Είδη Ανάλυσης")
        layout.addWidget(tabs)
        self.tabs = tabs

    # ── CLIENTS ──────────────────────────────────────────────────────────────

    def _build_clients_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        toolbar = QHBoxLayout()
        btn_add = _btn("➕ Νέος Πελάτης", "#2ecc71", "#27ae60")
        btn_edit = _btn("✏️ Επεξεργασία", "#3498db", "#2980b9")
        btn_del = _btn("🗑 Διαγραφή", "#e74c3c", "#c0392b")
        btn_add.clicked.connect(self._add_client)
        btn_edit.clicked.connect(self._edit_client)
        btn_del.clicked.connect(self._delete_client)
        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_edit)
        toolbar.addWidget(btn_del)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(6)
        self.clients_table.setHorizontalHeaderLabels(
            ["ID", "Όνομα", "Κωδικός", "Επαφή", "Email", "Τηλέφωνο"]
        )
        self.clients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.clients_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.clients_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.clients_table.setAlternatingRowColors(True)
        self.clients_table.verticalHeader().setVisible(False)
        self.clients_table.doubleClicked.connect(self._edit_client)
        layout.addWidget(self.clients_table)

        self._load_clients()
        return w

    def _load_clients(self):
        data = get_all_clients(self.db_path)
        self.clients_data = data
        t = self.clients_table
        t.setRowCount(len(data))
        for row, c in enumerate(data):
            t.setItem(row, 0, QTableWidgetItem(str(c['id'])))
            t.setItem(row, 1, QTableWidgetItem(c['name']))
            t.setItem(row, 2, QTableWidgetItem(c['code'] or ""))
            t.setItem(row, 3, QTableWidgetItem(c['contact'] or ""))
            t.setItem(row, 4, QTableWidgetItem(c['email'] or ""))
            t.setItem(row, 5, QTableWidgetItem(c['phone'] or ""))

    def _add_client(self):
        dlg = ClientDialog(self)
        if dlg.exec_():
            d = dlg.get_data()
            try:
                add_client(self.db_path, **d)
                self._load_clients()
            except Exception as e:
                QMessageBox.critical(self, "Σφάλμα", str(e))

    def _edit_client(self):
        row = self.clients_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Επιλογή", "Επιλέξτε πελάτη πρώτα.")
            return
        c = self.clients_data[row]
        dlg = ClientDialog(self, data=c)
        if dlg.exec_():
            d = dlg.get_data()
            try:
                update_client(self.db_path, c['id'], **d)
                self._load_clients()
            except Exception as e:
                QMessageBox.critical(self, "Σφάλμα", str(e))

    def _delete_client(self):
        row = self.clients_table.currentRow()
        if row < 0:
            return
        c = self.clients_data[row]
        if QMessageBox.question(
            self, "Διαγραφή",
            f"Διαγραφή πελάτη '{c['name']}';\n(Μόνο αν δεν έχει batches)",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            try:
                delete_client(self.db_path, c['id'])
                self._load_clients()
            except Exception as e:
                QMessageBox.critical(self, "Σφάλμα", f"Αδυναμία διαγραφής:\n{e}")

    # ── ANALYSTS ─────────────────────────────────────────────────────────────

    def _build_analysts_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        toolbar = QHBoxLayout()
        btn_add = _btn("➕ Νέος Αναλυτής", "#2ecc71", "#27ae60")
        btn_edit = _btn("✏️ Επεξεργασία", "#3498db", "#2980b9")
        btn_del = _btn("🗑 Διαγραφή", "#e74c3c", "#c0392b")
        btn_add.clicked.connect(self._add_analyst)
        btn_edit.clicked.connect(self._edit_analyst)
        btn_del.clicked.connect(self._delete_analyst)
        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_edit)
        toolbar.addWidget(btn_del)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.analysts_table = QTableWidget()
        self.analysts_table.setColumnCount(5)
        self.analysts_table.setHorizontalHeaderLabels(
            ["ID", "Όνομα", "Email", "Τηλέφωνο", "Ενεργός"]
        )
        self.analysts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.analysts_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.analysts_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.analysts_table.setAlternatingRowColors(True)
        self.analysts_table.verticalHeader().setVisible(False)
        self.analysts_table.doubleClicked.connect(self._edit_analyst)
        layout.addWidget(self.analysts_table)

        self._load_analysts()
        return w

    def _load_analysts(self):
        data = get_all_analysts(self.db_path)
        self.analysts_data = data
        t = self.analysts_table
        t.setRowCount(len(data))
        for row, a in enumerate(data):
            t.setItem(row, 0, QTableWidgetItem(str(a['id'])))
            t.setItem(row, 1, QTableWidgetItem(a['name']))
            t.setItem(row, 2, QTableWidgetItem(a['email'] or ""))
            t.setItem(row, 3, QTableWidgetItem(a['phone'] or ""))
            t.setItem(row, 4, QTableWidgetItem("✅" if a['active'] else "❌"))

    def _add_analyst(self):
        dlg = AnalystDialog(self)
        if dlg.exec_():
            d = dlg.get_data()
            add_analyst(self.db_path, **d)
            self._load_analysts()

    def _edit_analyst(self):
        row = self.analysts_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Επιλογή", "Επιλέξτε αναλυτή πρώτα.")
            return
        a = self.analysts_data[row]
        dlg = AnalystDialog(self, data=a)
        if dlg.exec_():
            d = dlg.get_data()
            update_analyst(self.db_path, a['id'], **d)
            self._load_analysts()

    def _delete_analyst(self):
        row = self.analysts_table.currentRow()
        if row < 0:
            return
        a = self.analysts_data[row]
        if QMessageBox.question(
            self, "Διαγραφή", f"Διαγραφή αναλυτή '{a['name']}';",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            try:
                delete_analyst(self.db_path, a['id'])
                self._load_analysts()
            except Exception as e:
                QMessageBox.critical(self, "Σφάλμα", str(e))

    # ── ANALYSIS TYPES ────────────────────────────────────────────────────────

    def _build_analysis_types_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        toolbar = QHBoxLayout()
        btn_add = _btn("➕ Νέα Ανάλυση", "#2ecc71", "#27ae60")
        btn_edit = _btn("✏️ Επεξεργασία", "#3498db", "#2980b9")
        btn_del = _btn("🗑 Διαγραφή", "#e74c3c", "#c0392b")
        btn_add.clicked.connect(self._add_analysis_type)
        btn_edit.clicked.connect(self._edit_analysis_type)
        btn_del.clicked.connect(self._delete_analysis_type)
        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_edit)
        toolbar.addWidget(btn_del)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.at_table = QTableWidget()
        self.at_table.setColumnCount(7)
        self.at_table.setHorizontalHeaderLabels([
            "ID", "Όνομα", "Επώαση (h)", "Θερμ. (°C)", "Αναμ. (d)", "Μονάδα", "Περιγραφή"
        ])
        self.at_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.at_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.at_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.at_table.setAlternatingRowColors(True)
        self.at_table.verticalHeader().setVisible(False)
        self.at_table.doubleClicked.connect(self._edit_analysis_type)
        layout.addWidget(self.at_table)

        self._load_analysis_types()
        return w

    def _load_analysis_types(self):
        data = get_all_analysis_types(self.db_path)
        self.at_data = data
        t = self.at_table
        t.setRowCount(len(data))
        for row, a in enumerate(data):
            t.setItem(row, 0, QTableWidgetItem(str(a['id'])))
            t.setItem(row, 1, QTableWidgetItem(a['name']))
            t.setItem(row, 2, QTableWidgetItem(str(a['incubation_hours'] or "—")))
            t.setItem(row, 3, QTableWidgetItem(str(a['temperature_c'] or "—")))
            t.setItem(row, 4, QTableWidgetItem(str(a['expected_days'] or "—")))
            t.setItem(row, 5, QTableWidgetItem(a['unit'] or ""))
            t.setItem(row, 6, QTableWidgetItem(a['description'] or ""))

    def _add_analysis_type(self):
        dlg = AnalysisTypeDialog(self)
        if dlg.exec_():
            d = dlg.get_data()
            try:
                add_analysis_type(self.db_path, **d)
                self._load_analysis_types()
            except Exception as e:
                QMessageBox.critical(self, "Σφάλμα", str(e))

    def _edit_analysis_type(self):
        row = self.at_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Επιλογή", "Επιλέξτε ανάλυση πρώτα.")
            return
        a = self.at_data[row]
        dlg = AnalysisTypeDialog(self, data=a)
        if dlg.exec_():
            d = dlg.get_data()
            try:
                update_analysis_type(self.db_path, a['id'], **d)
                self._load_analysis_types()
            except Exception as e:
                QMessageBox.critical(self, "Σφάλμα", str(e))

    def _delete_analysis_type(self):
        row = self.at_table.currentRow()
        if row < 0:
            return
        a = self.at_data[row]
        if QMessageBox.question(
            self, "Διαγραφή", f"Διαγραφή ανάλυσης '{a['name']}';",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            try:
                delete_analysis_type(self.db_path, a['id'])
                self._load_analysis_types()
            except Exception as e:
                QMessageBox.critical(self, "Σφάλμα", str(e))

    def refresh(self):
        self._load_clients()
        self._load_analysts()
        self._load_analysis_types()
