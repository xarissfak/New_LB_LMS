"""
main_window.py
Κύριο παράθυρο εφαρμογής με sidebar navigation.
"""

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame,
    QStatusBar, QMenuBar, QMenu, QMessageBox, QAction
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from views.dashboard_view import DashboardView
from views.master_data_view import MasterDataView
from views.samples_view import SamplesView
from views.all_samples_view import AllSamplesView
from database.export_utils import export_samples_csv, export_batches_csv


class SidebarButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setMinimumHeight(50)
        self.setStyleSheet("""
            QPushButton {
                background: transparent; color: #bbb;
                border: none; text-align: left;
                padding: 0 20px; font-size: 13px; border-radius: 0;
            }
            QPushButton:hover { background: rgba(255,255,255,0.08); color: white; }
            QPushButton:checked {
                background: rgba(52,152,219,0.25); color: white;
                border-left: 3px solid #3498db; font-weight: bold;
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path
        self.setWindowTitle(f"🧪 LabTrack — {os.path.basename(db_path)}")
        self.setMinimumSize(1150, 720)
        self._build_menu()
        self._build()

    def _build_menu(self):
        menubar = self.menuBar()

        # Αρχείο
        file_menu = menubar.addMenu("Αρχείο")
        act_export_samples = QAction("📤 Export Δειγμάτων (CSV)", self)
        act_export_batches = QAction("📤 Export Batches (CSV)", self)
        act_exit = QAction("Έξοδος", self)
        act_export_samples.triggered.connect(lambda: export_samples_csv(self.db_path, self))
        act_export_batches.triggered.connect(lambda: export_batches_csv(self.db_path, self))
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_export_samples)
        file_menu.addAction(act_export_batches)
        file_menu.addSeparator()
        file_menu.addAction(act_exit)

        # Βοήθεια
        help_menu = menubar.addMenu("Βοήθεια")
        act_about = QAction("Σχετικά", self)
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── SIDEBAR ──────────────────────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setFixedWidth(215)
        sidebar.setStyleSheet("background: #1a2535;")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(0)

        logo = QLabel("🧪 LabTrack")
        logo.setStyleSheet(
            "color: white; font-size: 18px; font-weight: bold; padding: 22px 20px 10px;"
        )
        sb_layout.addWidget(logo)

        db_label = QLabel(os.path.basename(self.db_path))
        db_label.setStyleSheet("color: #5d7a9a; font-size: 10px; padding: 0 20px 14px;")
        db_label.setWordWrap(True)
        sb_layout.addWidget(db_label)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #2c3e50; max-height: 1px;")
        sb_layout.addWidget(sep)
        sb_layout.addSpacing(6)

        # Ετικέτα ομάδας
        nav_label = QLabel("ΠΛΟΗΓΗΣΗ")
        nav_label.setStyleSheet(
            "color: #5d7a9a; font-size: 9px; font-weight: bold; "
            "padding: 8px 20px 4px; letter-spacing: 1px;"
        )
        sb_layout.addWidget(nav_label)

        self.btn_dashboard = SidebarButton("📊  Dashboard")
        self.btn_samples = SidebarButton("🗂  Batches & Δείγματα")
        self.btn_all_samples = SidebarButton("🔍  Όλα τα Δείγματα")

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("background: #2c3e50; max-height: 1px; margin: 6px 0;")

        master_label = QLabel("ΡΥΘΜΙΣΕΙΣ")
        master_label.setStyleSheet(
            "color: #5d7a9a; font-size: 9px; font-weight: bold; "
            "padding: 8px 20px 4px; letter-spacing: 1px;"
        )

        self.btn_master = SidebarButton("⚙️  Master Data")

        self.nav_buttons = [
            self.btn_dashboard, self.btn_samples,
            self.btn_all_samples, self.btn_master
        ]

        for btn in [self.btn_dashboard, self.btn_samples, self.btn_all_samples]:
            sb_layout.addWidget(btn)
        sb_layout.addWidget(sep2)
        sb_layout.addWidget(master_label)
        sb_layout.addWidget(self.btn_master)

        self.btn_dashboard.clicked.connect(lambda: self._navigate(0))
        self.btn_samples.clicked.connect(lambda: self._navigate(1))
        self.btn_all_samples.clicked.connect(lambda: self._navigate(2))
        self.btn_master.clicked.connect(lambda: self._navigate(3))

        sb_layout.addStretch()

        sep3 = QFrame()
        sep3.setFrameShape(QFrame.HLine)
        sep3.setStyleSheet("background: #2c3e50; max-height: 1px;")
        sb_layout.addWidget(sep3)

        version_label = QLabel("LabTrack v1.0")
        version_label.setStyleSheet("color: #3d5068; font-size: 10px; padding: 10px 20px;")
        sb_layout.addWidget(version_label)

        root.addWidget(sidebar)

        # ── MAIN CONTENT ─────────────────────────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: #f0f3f7;")

        self.dashboard_view = DashboardView(self.db_path)
        self.samples_view = SamplesView(self.db_path)
        self.all_samples_view = AllSamplesView(self.db_path)
        self.master_view = MasterDataView(self.db_path)

        self.stack.addWidget(self.dashboard_view)    # 0
        self.stack.addWidget(self.samples_view)      # 1
        self.stack.addWidget(self.all_samples_view)  # 2
        self.stack.addWidget(self.master_view)       # 3

        root.addWidget(self.stack)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Βάση: {self.db_path}")

        # Auto-refresh κάθε 60 sec
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._auto_refresh)
        self.refresh_timer.start(60_000)

        self._navigate(0)

    def _navigate(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

        views = [
            self.dashboard_view,
            self.samples_view,
            self.all_samples_view,
            self.master_view,
        ]
        if index < len(views):
            views[index].refresh()

        names = ["Dashboard", "Batches & Δείγματα", "Όλα τα Δείγματα", "Master Data"]
        self.status_bar.showMessage(f"{names[index]}  |  Βάση: {self.db_path}")

    def _auto_refresh(self):
        idx = self.stack.currentIndex()
        if idx == 0:
            self.dashboard_view.refresh()

    def _show_about(self):
        QMessageBox.about(
            self, "Σχετικά με το LabTrack",
            "<b>🧪 LabTrack v1.0</b><br><br>"
            "Mini LIMS — Σύστημα Διαχείρισης Δειγμάτων Εργαστηρίου<br><br>"
            "Python + PyQt5 + SQLite<br><br>"
            "<i>Για παραμετροποίηση επεξεργαστείτε τα αρχεία στους φακέλους "
            "database/, models/, dialogs/, views/</i>"
        )
