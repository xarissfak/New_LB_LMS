# 👨‍💻 Developer Guide

Guide for developers working with or extending the Laboratory Management System.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Project Architecture](#project-architecture)
3. [Coding Standards](#coding-standards)
4. [Adding New Features](#adding-new-features)
5. [Testing Guidelines](#testing-guidelines)
6. [Database Modifications](#database-modifications)
7. [UI Development](#ui-development)
8. [Debugging Tips](#debugging-tips)

---

## Development Setup

### Prerequisites
- Python 3.7+
- Git
- SQLite 3 (included with Python)
- IDE (VS Code, PyCharm, etc.)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/xarissfak/New_LB_LMS.git
cd New_LB_LMS

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies (optional)
pip install pytest pytest-cov pylint
```

### Project Structure Review
```
New_LB_LMS/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── database/                  # Database layer
├── models/                    # Business logic + CRUD
├── dialogs/                   # UI dialogs
├── logs/                      # Logging system
└── views/                     # Main UI views
```

---

## Project Architecture

### Layered Architecture

```
┌─────────────────────────────────────┐
│      Views (PyQt5 Widgets)          │
│  (main_window, samples_view, etc.)  │
└─────────────────────────────────────┘
              ↑         ↓
┌─────────────────────────────────────┐
│      Dialogs (UI Forms)             │
│  (batch_dialog, advanced_dialogs)   │
└─────────────────────────────────────┘
              ↑         ↓
┌─────────────────────────────────────┐
│  Business Logic & CRUD (models/)    │
│      + Logging (logs/)              │
│      + Undo/Redo (undo_manager)     │
└─────────────────────────────────────┘
              ↑         ↓
┌─────────────────────────────────────┐
│   Database Layer (SQLite)           │
│     (db_manager.py)                 │
└─────────────────────────────────────┘
```

### Data Flow Example

```
User Action in View
    ↓
Dialog opened/Form submitted
    ↓
CRUD function called (models/crud.py)
    ↓
Logger records action (logs/action_logger.py)
    ↓
Database query executed (database/db_manager.py)
    ↓
Result returned up the stack
    ↓
View updated with new data
```

### Key Components

#### Database Layer (`database/`)
- **db_manager.py** - Connection, migrations, schema
- SQLite database with PRAGMA foreign_keys ON
- Transaction support

#### Models Layer (`models/`)
- **crud.py** - All database operations
- **undo_manager.py** - Undo/redo system
- Pure functions, no UI logic

#### Logging (`logs/`)
- **action_logger.py** - Singleton logger
- Tracks all operations
- Persistent audit trail

#### UI Layer (`dialogs/`, `views/`)
- **PyQt5** based components
- Signal/slot mechanism
- Styled with CSS

---

## Coding Standards

### Python Style
- Follow **PEP 8** guidelines
- Use type hints where practical
- Document complex functions

### Naming Conventions
```python
# Functions/Methods - snake_case
def get_all_batches(db_path):
    pass

# Constants - UPPER_CASE
DATABASE_VERSION = 2
MAX_UNDO_STACK = 20

# Classes - PascalCase
class BatchDialog(QDialog):
    pass

# Private - Leading underscore
def _internal_helper():
    pass
```

### Documentation
```python
def add_unit(db_path, name, symbol, description="", category=""):
    """
    Create new measurement unit.
    
    Args:
        db_path (str): Path to database
        name (str): Unit name (e.g., "Χιλιόγραμμο")
        symbol (str): Unit symbol (e.g., "kg")
        description (str): Optional description
        category (str): Category (e.g., "Βάρος")
    
    Returns:
        tuple: (success: bool, result: int|str)
            - On success: (True, unit_id)
            - On error: (False, error_message)
    
    Example:
        >>> add_unit(db, "kg", "kg", category="Weight")
        (True, 1)
    """
```

### Error Handling
```python
# Good: Specific exception handling
try:
    conn.execute(sql, params)
except sqlite3.IntegrityError as e:
    return False, f"Duplicate: {e}"
except sqlite3.OperationalError as e:
    return False, f"Database error: {e}"

# Bad: Broad exception handling
try:
    something()
except:
    pass
```

---

## Adding New Features

### Step 1: Database Changes

If you need a new table or column:

1. Create migration in `db_manager.py`
2. Increment `CURRENT_SCHEMA_VERSION`
3. Update `_run_migration()` function

```python
# In db_manager.py
CURRENT_SCHEMA_VERSION = 3  # Was 2

def _run_migration(cursor):
    # ... existing tables ...
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS new_table (
            id INTEGER PRIMARY KEY,
            ...
        )
    """)
```

### Step 2: Add CRUD Functions

In `models/crud.py`:

```python
def get_some_items(db_path):
    conn = get_connection(db_path)
    rows = conn.execute("SELECT * FROM table").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_some_item(db_path, field1, field2=""):
    conn = get_connection(db_path)
    conn.execute(
        "INSERT INTO table (field1, field2) VALUES (?, ?)",
        (field1, field2)
    )
    conn.commit()
    conn.close()
```

### Step 3: Create or Update Dialog

In `dialogs/` create or modify as needed:

```python
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout
from PyQt5.QtCore import Qt

class MyDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("My Dialog")
        self.data = data or {}
        self._build()
    
    def _build(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Add UI elements
        self.field1 = QLineEdit(self.data.get("field1", ""))
        form.addRow("Label", self.field1)
        
        layout.addLayout(form)
    
    def get_data(self):
        return {"field1": self.field1.text().strip()}
```

### Step 4: Integrate into View

In `views/` update the appropriate view:

```python
def _add_item(self):
    from dialogs.my_dialog import MyDialog
    
    dialog = MyDialog(self)
    if dialog.exec_():
        data = dialog.get_data()
        add_some_item(self.db_path, **data)
        self._refresh_view()
```

### Step 5: Add Logging

Wrap operations with logging:

```python
from logs.action_logger import get_logger

logger = get_logger(db_path)

try:
    item_id = add_some_item(db_path, **data)
    logger.log_action(
        "CREATE", "ITEM",
        entity_type="item", entity_id=item_id,
        new_data=data
    )
except Exception as e:
    logger.log_action(
        "CREATE", "ITEM",
        status="ERROR",
        error_msg=str(e)
    )
```

---

## Testing Guidelines

### Unit Tests

Create tests in `tests/` directory:

```python
# tests/test_crud.py
import unittest
from models.crud import add_unit, get_all_units
import tempfile
import os

class TestUnitCRUD(unittest.TestCase):
    def setUp(self):
        # Create temp database
        self.db_fd, self.db_path = tempfile.mkstemp()
        # Initialize database
    
    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_add_unit(self):
        success, result = add_unit(
            self.db_path,
            "kg", "kg"
        )
        self.assertTrue(success)
        self.assertIsInstance(result, int)
    
    def test_get_all_units(self):
        add_unit(self.db_path, "kg", "kg")
        units = get_all_units(self.db_path)
        self.assertEqual(len(units), 1)
```

### Integration Tests

Test features end-to-end:

```python
def test_batch_creation_with_logging():
    # Create batch
    batch_id = add_batch(db, batch_data)
    
    # Verify in database
    batch = get_batch(db, batch_id)
    assert batch is not None
    
    # Verify in logs
    logs = logger.get_entity_logs("batch", batch_id)
    assert len(logs) > 0
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_crud.py::TestUnitCRUD::test_add_unit
```

---

## Database Modifications

### Safe Migration Process

1. **Test in development first**
2. **Backup existing database**
3. **Run application** (auto-migration occurs)
4. **Verify data integrity**

### Adding a Column

```python
# In db_manager.py
def _run_migration(cursor):
    # ... existing code ...
    
    # Add new column (SQLite supports limited ALTER TABLE)
    try:
        cursor.execute("ALTER TABLE table ADD COLUMN new_column TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
```

### Adding a Table

```python
def _run_migration(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS new_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
```

---

## UI Development

### PyQt5 Best Practices

#### Button Styling
```python
def create_styled_button(text, color, hover_color):
    btn = QPushButton(text)
    btn.setMinimumHeight(36)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {color};
            color: white;
            border-radius: 6px;
            font-weight: bold;
            padding: 0 14px;
        }}
        QPushButton:hover {{ background: {hover_color}; }}
    """)
    return btn
```

#### Table Configuration
```python
table = QTableWidget()
table.setColumnCount(4)
table.setHorizontalHeaderLabels(["Col1", "Col2", "Col3", "Col4"])
table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
table.setEditTriggers(QAbstractItemView.NoEditTriggers)
table.setSelectionBehavior(QAbstractItemView.SelectRows)
table.setAlternatingRowColors(True)
```

#### Dialog Pattern
```python
class MyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
    
    def _build(self):
        layout = QVBoxLayout(self)
        # Add widgets
        buttons = QHBoxLayout()
        ok = QPushButton("OK")
        cancel = QPushButton("Cancel")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        buttons.addStretch()
        buttons.addWidget(cancel)
        buttons.addWidget(ok)
        layout.addLayout(buttons)
    
    def get_data(self):
        # Return validated data
        return {}
```

---

## Debugging Tips

### Logging Debug Information

```python
from logs.action_logger import get_logger

logger = get_logger(db_path)

# Log debug information
logger.log_action(
    "DEBUG", "CUSTOM",
    details=f"Debug info: {variable}",
    new_data={"debug": True}
)

# View in logs viewer
logs = logger.get_logs(limit=100, category="CUSTOM")
```

### Print Debugging

```python
import sys

# Print to console
print(f"DEBUG: variable = {variable}", file=sys.stderr)

# Print Qt signals
obj.signal.connect(lambda: print("Signal fired!"))
```

### Database Inspection

```python
# Open database directly
import sqlite3

conn = sqlite3.connect('/path/to/db.sqlite')
cursor = conn.cursor()

# Query table
cursor.execute("SELECT * FROM action_logs LIMIT 5")
for row in cursor.fetchall():
    print(row)
```

### PyQt5 Debugging

```python
# Print Qt object info
widget = self.sender()
print(f"Sender: {widget}, Type: {type(widget)}")

# Check model/view state
model = table.model()
print(f"Rows: {model.rowCount()}, Cols: {model.columnCount()}")
```

---

## Performance Optimization

### Database Queries
```python
# Bad: N+1 queries
for batch in get_all_batches(db):
    samples = get_samples_for_batch(db, batch['id'])

# Good: Single query with JOIN
def get_batches_with_samples(db_path):
    conn = get_connection(db_path)
    rows = conn.execute("""
        SELECT b.*, COUNT(s.id) as sample_count
        FROM batches b
        LEFT JOIN samples s ON s.batch_id = b.id
        GROUP BY b.id
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
```

### UI Updating
```python
# Bad: Update UI for each item
for item in items:
    add_table_row(item)

# Good: Update UI once
table.setRowCount(0)  # Clear
for item in items:
    add_table_row(item)
table.resizeColumnsToContents()
```

---

## Release Checklist

Before releasing new version:

- [ ] All tests pass
- [ ] No syntax errors
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped (main.py, etc.)
- [ ] Database migration tested
- [ ] No breaking changes documented
- [ ] Code review completed
- [ ] Git commits clean

---

## Useful Commands

```bash
# Check syntax
python -m py_compile models/crud.py

# Format code
python -m autopep8 --in-place myfile.py

# Lint code
pylint models/crud.py

# Find imports
grep -r "^import\|^from" --include="*.py"

# Database backup
cp database.db database.db.backup

# Run with verbose logging
python main.py -v
```

---

## Resources

- [PyQt5 Documentation](https://doc.qt.io/qt-5/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

---

## Support & Questions

For development questions:
1. Check existing code patterns
2. Review documentation files
3. Test in development database
4. Use logging to debug

---

**Happy Coding!** 🚀

Last Updated: April 2026 | Version 2.0 API
