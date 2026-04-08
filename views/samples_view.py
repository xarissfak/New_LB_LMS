"""
samples_view.py
Οθόνη Batches & Samples — καθημερινή ροή εργασίας.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QMessageBox, QAbstractItemView,
    QComboBox, QLineEdit, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor

from database.db_manager import STATUS_COLORS, STATUSES, status_label
from models.crud import (
    get_all_batches, add_batch, delete_batch,
    get_samples_for_batch, add_sample, update_sample_status,
    update_sample_result, delete_sample, next_sample_code,
    add_sample_analysis
)
from dialogs.batch_sample_dialogs import (
    BatchDialog, AddSampleDialog, StatusUpdateDialog,
    ResultDialog, HistoryDialog
)
from dialogs.advanced_dialogs import BulkAnalysisAssignmentDialog
from logs.action_logger import get_logger


def _btn(text, color, hover, size=32):
    b = QPushButton(text)
    b.setMinimumHeight(size)
    b.setStyleSheet(f"""
        QPushButton{{background:{color};color:white;border-radius:6px;
                     font-weight:bold;padding:0 10px;font-size:12px;}}
        QPushButton:hover{{background:{hover};}}
    """)
    return b


class SamplesView(QWidget):
    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.logger = get_logger(db_path)
        self.current_batch = None
        self._build()
        self._load_batches()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("🗂 Batches & Δείγματα")
        f = QFont()
        f.setPointSize(16)
        f.setBold(True)
        title.setFont(f)
        layout.addWidget(title)

        splitter = QSplitter(Qt.Horizontal)

        # ── LEFT: Batches panel ──────────────────────────────────────────────
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 8, 0)

        lbl = QLabel("Batches")
        lbl.setStyleSheet("font-weight:bold; font-size:13px;")
        left_layout.addWidget(lbl)

        # Toolbar batches
        bt = QHBoxLayout()
        btn_new_batch = _btn("➕ Νέο Batch", "#3498db", "#2980b9")
        btn_del_batch = _btn("🗑", "#e74c3c", "#c0392b")
        btn_new_batch.clicked.connect(self._new_batch)
        btn_del_batch.clicked.connect(self._delete_batch)
        bt.addWidget(btn_new_batch)
        bt.addWidget(btn_del_batch)
        bt.addStretch()
        left_layout.addLayout(bt)

        self.batch_table = QTableWidget()
        self.batch_table.setColumnCount(4)
        self.batch_table.setHorizontalHeaderLabels(["Κωδικός", "Πελάτης", "Παραλαβή", "Δείγ."])
        self.batch_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.batch_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.batch_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.batch_table.setAlternatingRowColors(True)
        self.batch_table.verticalHeader().setVisible(False)
        self.batch_table.itemSelectionChanged.connect(self._batch_selected)
        left_layout.addWidget(self.batch_table)

        splitter.addWidget(left)

        # ── RIGHT: Samples panel ─────────────────────────────────────────────
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 0, 0, 0)

        self.batch_title = QLabel("Επιλέξτε Batch")
        self.batch_title.setStyleSheet("font-weight:bold; font-size:13px;")
        right_layout.addWidget(self.batch_title)

        # Toolbar samples
        st = QHBoxLayout()
        btn_add_sample = _btn("➕ Δείγμα", "#2ecc71", "#27ae60")
        btn_status = _btn("🔄 Κατάσταση", "#e67e22", "#d35400")
        btn_result = _btn("📝 Αποτέλεσμα", "#9b59b6", "#8e44ad")
        btn_history = _btn("📋 Ιστορικό", "#16a085", "#1abc9c")
        btn_del_sample = _btn("🗑", "#e74c3c", "#c0392b")

        btn_add_sample.clicked.connect(self._add_sample)
        btn_status.clicked.connect(self._update_status)
        btn_result.clicked.connect(self._enter_result)
        btn_history.clicked.connect(self._view_history)
        btn_del_sample.clicked.connect(self._delete_sample)

        st.addWidget(btn_add_sample)
        st.addWidget(btn_status)
        st.addWidget(btn_result)
        st.addWidget(btn_history)
        st.addWidget(btn_del_sample)
        st.addStretch()
        right_layout.addLayout(st)

        # Φίλτρο κατάστασης
        filter_bar = QHBoxLayout()
        filter_bar.addWidget(QLabel("Φίλτρο:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("Όλα", None)
        for code, label in STATUSES:
            self.status_filter.addItem(label, code)
        self.status_filter.currentIndexChanged.connect(self._load_samples)
        filter_bar.addWidget(self.status_filter)
        filter_bar.addStretch()
        right_layout.addLayout(filter_bar)

        self.samples_table = QTableWidget()
        self.samples_table.setColumnCount(7)
        self.samples_table.setHorizontalHeaderLabels([
            "Κωδικός", "Ανάλυση", "Κατάσταση", "Αναλυτής",
            "Αποτέλεσμα", "Αναμ.(d)", "Ημ. Εισαγωγής"
        ])
        self.samples_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.samples_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.samples_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.samples_table.setAlternatingRowColors(True)
        self.samples_table.verticalHeader().setVisible(False)
        self.samples_table.doubleClicked.connect(self._update_status)
        right_layout.addWidget(self.samples_table)

        splitter.addWidget(right)
        splitter.setSizes([340, 660])
        layout.addWidget(splitter)

    # ── BATCHES ──────────────────────────────────────────────────────────────

    def _load_batches(self):
        data = get_all_batches(self.db_path)
        self.batches_data = data
        t = self.batch_table
        t.setRowCount(len(data))
        for row, b in enumerate(data):
            t.setItem(row, 0, QTableWidgetItem(b['batch_code']))
            t.setItem(row, 1, QTableWidgetItem(b['client_name']))
            t.setItem(row, 2, QTableWidgetItem(b['received_date']))
            t.setItem(row, 3, QTableWidgetItem(str(b['sample_count'])))

    def _batch_selected(self):
        row = self.batch_table.currentRow()
        if row < 0 or row >= len(self.batches_data):
            return
        self.current_batch = self.batches_data[row]
        self.batch_title.setText(
            f"Δείγματα: {self.current_batch['batch_code']} | {self.current_batch['client_name']}"
        )
        self._load_samples()

    def _new_batch(self):
        dlg = BatchDialog(self.db_path, self)
        if dlg.exec_():
            d = dlg.get_data()
            try:
                sample_count = d.pop('sample_count', 0)
                batch_id = add_batch(self.db_path, **d)
                
                # Log batch creation
                self.logger.log_action(
                    "CREATE", "BATCH",
                    entity_type="batch", entity_id=batch_id,
                    new_data=d
                )
                
                # Pre-create samples if count > 0
                if sample_count > 0:
                    failed_create = False
                    created_samples = []
                    
                    for i in range(1, sample_count + 1):
                        sample_code = f"{d['batch_code']}/S{i}"
                        try:
                            # Create sample with placeholder analysis (will be updated)
                            # For now, we'll skip this and let user add analyses
                            created_samples.append(sample_code)
                        except Exception as e:
                            failed_create = True
                            self.logger.log_action(
                                "CREATE", "SAMPLE",
                                status="ERROR",
                                entity_type="sample",
                                error_msg=str(e)
                            )
                    
                    # Ask user to assign analyses to samples
                    if created_samples:
                        dlg_assign = BulkAnalysisAssignmentDialog(self.db_path, list(range(1, sample_count + 1)), self)
                        if dlg_assign.exec_():
                            # Would need to implement batch sample creation with analyses
                            pass
                
                self._load_batches()
                QMessageBox.information(self, "Επιτυχία", f"Batch '{d['batch_code']}' δημιουργήθηκε.")
            except Exception as e:
                QMessageBox.critical(self, "Σφάλμα", str(e))
                self.logger.log_action(
                    "CREATE", "BATCH",
                    status="ERROR",
                    error_msg=str(e)
                )

    def _delete_batch(self):
        row = self.batch_table.currentRow()
        if row < 0:
            return
        b = self.batches_data[row]
        if QMessageBox.question(
            self, "Διαγραφή",
            f"Διαγραφή batch '{b['batch_code']}' και ΟΛΩΝ των δειγμάτων του;",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            delete_batch(self.db_path, b['id'])
            self.current_batch = None
            self.samples_table.setRowCount(0)
            self.batch_title.setText("Επιλέξτε Batch")
            self._load_batches()

    # ── SAMPLES ──────────────────────────────────────────────────────────────

    def _load_samples(self):
        if not self.current_batch:
            return
        status_f = self.status_filter.currentData()
        data = get_samples_for_batch(self.db_path, self.current_batch['id'])
        if status_f:
            data = [s for s in data if s['status'] == status_f]
        self.samples_data = data
        t = self.samples_table
        t.setRowCount(len(data))
        for row, s in enumerate(data):
            t.setItem(row, 0, QTableWidgetItem(s['sample_code']))
            t.setItem(row, 1, QTableWidgetItem(s['analysis_name']))

            si = QTableWidgetItem(status_label(s['status']))
            color = STATUS_COLORS.get(s['status'], '#ccc')
            si.setBackground(QColor(color))
            si.setForeground(QColor("white"))
            t.setItem(row, 2, si)

            t.setItem(row, 3, QTableWidgetItem(s.get('analyst_name') or "—"))
            t.setItem(row, 4, QTableWidgetItem(s.get('result_value') or ""))
            t.setItem(row, 5, QTableWidgetItem(str(s.get('expected_days') or "—")))
            t.setItem(row, 6, QTableWidgetItem(s['created_at'][:10]))

    def _add_sample(self):
        if not self.current_batch:
            QMessageBox.information(self, "Batch", "Επιλέξτε πρώτα ένα batch.")
            return
        while True:
            dlg = AddSampleDialog(
                self.db_path,
                self.current_batch['batch_code'],
                self.current_batch['id'],
                self
            )
            if dlg.exec_():
                d = dlg.get_data()
                try:
                    add_sample(self.db_path, **d)
                    self._load_samples()
                    self._load_batches()
                except Exception as e:
                    QMessageBox.critical(self, "Σφάλμα", str(e))
                if not getattr(dlg, 'add_more', False):
                    break
            else:
                break

    def _get_selected_sample(self):
        row = self.samples_table.currentRow()
        if row < 0 or row >= len(self.samples_data):
            QMessageBox.information(self, "Επιλογή", "Επιλέξτε δείγμα πρώτα.")
            return None
        return self.samples_data[row]

    def _update_status(self):
        s = self._get_selected_sample()
        if not s:
            return
        dlg = StatusUpdateDialog(self.db_path, s, self)
        if dlg.exec_():
            d = dlg.get_data()
            update_sample_status(self.db_path, s['id'], d['status'], d['analyst_id'], d['notes'])
            self._load_samples()

    def _enter_result(self):
        s = self._get_selected_sample()
        if not s:
            return
        dlg = ResultDialog(self.db_path, s, self)
        if dlg.exec_():
            d = dlg.get_data()
            update_sample_result(
                self.db_path, s['id'],
                d['result_value'], d['result_notes'], d['analyst_id']
            )
            self._load_samples()

    def _view_history(self):
        s = self._get_selected_sample()
        if not s:
            return
        # Εμπλουτισμός με batch info
        s['batch_code'] = self.current_batch['batch_code']
        s['client_name'] = self.current_batch['client_name']
        HistoryDialog(self.db_path, s, self).exec_()

    def _delete_sample(self):
        s = self._get_selected_sample()
        if not s:
            return
        if QMessageBox.question(
            self, "Διαγραφή",
            f"Διαγραφή δείγματος '{s['sample_code']}';",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            delete_sample(self.db_path, s['id'])
            self._load_samples()
            self._load_batches()

    def refresh(self):
        self._load_batches()
        if self.current_batch:
            self._load_samples()
