"""
dashboard_view.py
Κεντρική οθόνη με στατιστικά και σύνοψη.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QGridLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from database.db_manager import STATUS_COLORS, status_label
from models.crud import get_dashboard_stats, get_all_samples


class StatCard(QFrame):
    def __init__(self, label, value, color="#3498db", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {color}; border-radius: 10px;
                min-width: 120px; min-height: 90px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self._val_label = QLabel(str(value))
        f = QFont()
        f.setPointSize(28)
        f.setBold(True)
        self._val_label.setFont(f)
        self._val_label.setStyleSheet("color: white;")
        self._val_label.setAlignment(Qt.AlignCenter)

        txt_label = QLabel(label)
        txt_label.setStyleSheet("color: rgba(255,255,255,0.85); font-size: 12px;")
        txt_label.setAlignment(Qt.AlignCenter)
        txt_label.setWordWrap(True)

        layout.addWidget(self._val_label)
        layout.addWidget(txt_label)

    def update_value(self, value):
        self._val_label.setText(str(value))


class DashboardView(QWidget):
    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self._build()
        self.refresh()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Τίτλος
        title = QLabel("📊 Dashboard")
        f = QFont()
        f.setPointSize(18)
        f.setBold(True)
        title.setFont(f)
        layout.addWidget(title)

        # Κάρτες στατιστικών
        cards_layout = QGridLayout()
        cards_layout.setSpacing(12)

        self.card_total = StatCard("Σύνολο Δειγμάτων", 0, "#34495e")
        self.card_batches = StatCard("Batches", 0, "#2c3e50")
        self.card_clients = StatCard("Πελάτες", 0, "#16a085")
        self.card_overdue = StatCard("Καθυστερημένα ⚠", 0, "#c0392b")

        self.card_received = StatCard("Παραλαβή", 0, STATUS_COLORS["RECEIVED"])
        self.card_in_analysis = StatCard("Προς Ανάλυση", 0, STATUS_COLORS["IN_ANALYSIS"])
        self.card_analyzed = StatCard("Αναλύθηκε", 0, STATUS_COLORS["ANALYZED"])
        self.card_pending = StatCard("Αναμονή", 0, STATUS_COLORS["PENDING"])
        self.card_completed = StatCard("Ολοκλήρωση", 0, STATUS_COLORS["COMPLETED"])
        self.card_shipped = StatCard("Αποστολή", 0, STATUS_COLORS["SHIPPED"])

        cards_layout.addWidget(self.card_total, 0, 0)
        cards_layout.addWidget(self.card_batches, 0, 1)
        cards_layout.addWidget(self.card_clients, 0, 2)
        cards_layout.addWidget(self.card_overdue, 0, 3)

        cards_layout.addWidget(self.card_received, 1, 0)
        cards_layout.addWidget(self.card_in_analysis, 1, 1)
        cards_layout.addWidget(self.card_analyzed, 1, 2)
        cards_layout.addWidget(self.card_pending, 1, 3)
        cards_layout.addWidget(self.card_completed, 2, 0)
        cards_layout.addWidget(self.card_shipped, 2, 1)

        layout.addLayout(cards_layout)

        # Πρόσφατα δείγματα
        recent_label = QLabel("🕐 Πρόσφατα Δείγματα")
        f2 = QFont()
        f2.setPointSize(13)
        f2.setBold(True)
        recent_label.setFont(f2)
        layout.addWidget(recent_label)

        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(6)
        self.recent_table.setHorizontalHeaderLabels([
            "Κωδικός", "Batch", "Πελάτης", "Ανάλυση", "Κατάσταση", "Ημ. Εισαγωγής"
        ])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recent_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.recent_table.setAlternatingRowColors(True)
        self.recent_table.verticalHeader().setVisible(False)
        self.recent_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.recent_table)

    def refresh(self):
        stats = get_dashboard_stats(self.db_path)

        self.card_total.update_value(stats['total_samples'])
        self.card_batches.update_value(stats['total_batches'])
        self.card_clients.update_value(stats['total_clients'])
        self.card_overdue.update_value(stats['overdue'])
        self.card_received.update_value(stats['received'])
        self.card_in_analysis.update_value(stats['in_analysis'])
        self.card_analyzed.update_value(stats['analyzed'])
        self.card_pending.update_value(stats['pending'])
        self.card_completed.update_value(stats['completed'])
        self.card_shipped.update_value(stats['shipped'])

        # Πρόσφατα 20 δείγματα
        samples = get_all_samples(self.db_path)[:20]
        self.recent_table.setRowCount(len(samples))
        for row, s in enumerate(samples):
            self.recent_table.setItem(row, 0, QTableWidgetItem(s['sample_code']))
            self.recent_table.setItem(row, 1, QTableWidgetItem(s['batch_code']))
            self.recent_table.setItem(row, 2, QTableWidgetItem(s['client_name']))
            self.recent_table.setItem(row, 3, QTableWidgetItem(s['analysis_name']))

            status_item = QTableWidgetItem(status_label(s['status']))
            color = STATUS_COLORS.get(s['status'], '#ccc')
            status_item.setBackground(QColor(color))
            status_item.setForeground(QColor("white"))
            self.recent_table.setItem(row, 4, status_item)
            self.recent_table.setItem(row, 5, QTableWidgetItem(s['created_at'][:10]))
