"""
all_samples_view.py
Συνολική οθόνη δειγμάτων — αναζήτηση και φίλτρα σε ολόκληρη τη βάση.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QComboBox, QLineEdit, QMessageBox,
    QAbstractItemView
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor

from database.db_manager import STATUS_COLORS, STATUSES, status_label
from models.crud import (
    get_all_samples, update_sample_status, update_sample_result, delete_sample
)
from dialogs.batch_sample_dialogs import (
    StatusUpdateDialog, ResultDialog, HistoryDialog
)


def _btn(text, color, hover, size=32):
    b = QPushButton(text)
    b.setMinimumHeight(size)
    b.setStyleSheet(f"""
        QPushButton{{background:{color};color:white;border-radius:6px;
                     font-weight:bold;padding:0 10px;font-size:12px;}}
        QPushButton:hover{{background:{hover};}}
    """)
    return b


class AllSamplesView(QWidget):
    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.samples_data = []
        self.all_data = []
        self._build()
        self._load()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("🔍 Όλα τα Δείγματα")
        f = QFont()
        f.setPointSize(16)
        f.setBold(True)
        title.setFont(f)
        layout.addWidget(title)

        # Φίλτρα
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(8)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Αναζήτηση (κωδικός, batch, πελάτης, ανάλυση)...")
        self.search_box.setMinimumWidth(280)
        self.search_box.textChanged.connect(self._on_search_changed)

        self.status_filter = QComboBox()
        self.status_filter.addItem("Όλες οι Καταστάσεις", None)
        for code, label in STATUSES:
            self.status_filter.addItem(label, code)
        self.status_filter.currentIndexChanged.connect(self._load)

        btn_refresh = _btn("🔄 Ανανέωση", "#16a085", "#1abc9c")
        btn_refresh.clicked.connect(self._load)

        self.count_label = QLabel("0 δείγματα")
        self.count_label.setStyleSheet("color: #666; font-size: 12px;")

        filter_bar.addWidget(self.search_box)
        filter_bar.addWidget(QLabel("Κατάσταση:"))
        filter_bar.addWidget(self.status_filter)
        filter_bar.addWidget(btn_refresh)
        filter_bar.addStretch()
        filter_bar.addWidget(self.count_label)
        layout.addLayout(filter_bar)

        # Toolbar
        toolbar = QHBoxLayout()
        btn_status = _btn("🔄 Αλλαγή Κατάστασης", "#e67e22", "#d35400")
        btn_result = _btn("📝 Αποτέλεσμα", "#9b59b6", "#8e44ad")
        btn_history = _btn("📋 Ιστορικό", "#16a085", "#1abc9c")
        btn_del = _btn("🗑 Διαγραφή", "#e74c3c", "#c0392b")
        btn_status.clicked.connect(self._update_status)
        btn_result.clicked.connect(self._enter_result)
        btn_history.clicked.connect(self._view_history)
        btn_del.clicked.connect(self._delete_sample)
        toolbar.addWidget(btn_status)
        toolbar.addWidget(btn_result)
        toolbar.addWidget(btn_history)
        toolbar.addWidget(btn_del)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Πίνακας
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Κωδικός Δείγματος", "Batch", "Πελάτης", "Ανάλυση",
            "Κατάσταση", "Αναλυτής", "Αποτέλεσμα", "Ημ. Εισαγωγής"
        ])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self._update_status)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._apply_filter)

    def _on_search_changed(self):
        self._search_timer.start(300)

    def _load(self):
        status_f = self.status_filter.currentData()
        self.all_data = get_all_samples(self.db_path, status_filter=status_f)
        self._apply_filter()

    def _apply_filter(self):
        query = self.search_box.text().strip().lower()
        if query:
            filtered = [
                s for s in self.all_data
                if query in s['sample_code'].lower()
                or query in s['batch_code'].lower()
                or query in s['client_name'].lower()
                or query in s['analysis_name'].lower()
                or (s.get('analyst_name') and query in s['analyst_name'].lower())
            ]
        else:
            filtered = self.all_data
        self.samples_data = filtered
        self.count_label.setText(f"{len(filtered)} δείγματα")
        self._fill_table(filtered)

    def _fill_table(self, data):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(data))
        for row, s in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(s['sample_code']))
            self.table.setItem(row, 1, QTableWidgetItem(s['batch_code']))
            self.table.setItem(row, 2, QTableWidgetItem(s['client_name']))
            self.table.setItem(row, 3, QTableWidgetItem(s['analysis_name']))
            si = QTableWidgetItem(status_label(s['status']))
            color = STATUS_COLORS.get(s['status'], '#ccc')
            si.setBackground(QColor(color))
            si.setForeground(QColor("white"))
            self.table.setItem(row, 4, si)
            self.table.setItem(row, 5, QTableWidgetItem(s.get('analyst_name') or "—"))
            self.table.setItem(row, 6, QTableWidgetItem(s.get('result_value') or ""))
            self.table.setItem(row, 7, QTableWidgetItem(s['created_at'][:10]))
        self.table.setSortingEnabled(True)

    def _get_selected(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.samples_data):
            QMessageBox.information(self, "Επιλογή", "Επιλέξτε δείγμα πρώτα.")
            return None
        return self.samples_data[row]

    def _update_status(self):
        s = self._get_selected()
        if not s:
            return
        dlg = StatusUpdateDialog(self.db_path, s, self)
        if dlg.exec_():
            d = dlg.get_data()
            update_sample_status(self.db_path, s['id'], d['status'], d['analyst_id'], d['notes'])
            self._load()

    def _enter_result(self):
        s = self._get_selected()
        if not s:
            return
        dlg = ResultDialog(self.db_path, s, self)
        if dlg.exec_():
            d = dlg.get_data()
            update_sample_result(self.db_path, s['id'], d['result_value'], d['result_notes'], d['analyst_id'])
            self._load()

    def _view_history(self):
        s = self._get_selected()
        if not s:
            return
        HistoryDialog(self.db_path, s, self).exec_()

    def _delete_sample(self):
        s = self._get_selected()
        if not s:
            return
        if QMessageBox.question(
            self, "Διαγραφή", f"Διαγραφή δείγματος '{s['sample_code']}';",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            delete_sample(self.db_path, s['id'])
            self._load()

    def refresh(self):
        self._load()
