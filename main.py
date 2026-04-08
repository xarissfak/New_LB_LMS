"""
main.py - Laboratory Management System (LabTrack)
Version: 2.0 ✨

Advanced laboratory sample and analysis management system with:
  ✅ Action Logging - Complete audit trail
  ✅ Undo/Redo System - 20-action stack
  ✅ Units of Measurement - Master data management
  ✅ Multi-Stage Analysis - Complex analysis workflows
  ✅ Range-Based Sampling - Bulk operations (1-4, 7-13)
  ✅ Comprehensive Logging UI - Search & filter operations

Installation:
    pip install -r requirements.txt

Execution:
    python main.py

For more information:
    See README.md, FEATURES_GUIDE.md, IMPLEMENTATION_SUMMARY.md
"""
import sys
import os

# Βεβαιωνόμαστε ότι το working directory είναι το root του project
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

from dialogs.startup_dialog import StartupDialog
from views.main_window import MainWindow


def apply_global_style(app: QApplication):
    app.setStyle("Fusion")
    app.setStyleSheet("""
        QWidget { font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; }
        QTableWidget { gridline-color: #e0e0e0; }
        QTableWidget::item:selected { background: #3498db; color: white; }
        QHeaderView::section {
            background: #2c3e50; color: white; padding: 6px;
            border: none; font-weight: bold;
        }
        QComboBox, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit {
            border: 1px solid #ccc; border-radius: 4px;
            padding: 4px 8px; background: white;
        }
        QComboBox:focus, QLineEdit:focus, QTextEdit:focus { border-color: #3498db; }
        QTabWidget::pane { border: 1px solid #ddd; }
        QTabBar::tab {
            background: #ecf0f1; padding: 8px 18px;
            border-top-left-radius: 4px; border-top-right-radius: 4px;
            margin-right: 2px;
        }
        QTabBar::tab:selected { background: white; font-weight: bold; }
        QScrollBar:vertical { width: 8px; background: #f0f0f0; }
        QScrollBar::handle:vertical { background: #bbb; border-radius: 4px; }
    """)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LabTrack")
    app.setOrganizationName("Lab")

    apply_global_style(app)

    startup = StartupDialog()
    if startup.exec_():
        db_path = startup.selected_db_path
        window = MainWindow(db_path)
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
