# 📚 API Reference

Complete API reference for Laboratory Management System (LabTrack) v2.0

## Table of Contents

1. [Action Logger API](#action-logger-api)
2. [Undo Manager API](#undo-manager-api)
3. [CRUD Operations - Units](#crud-operations---units)
4. [CRUD Operations - Sample Analysis](#crud-operations---sample-analysis)
5. [Advanced Dialogs API](#advanced-dialogs-api)

---

## Action Logger API

**Module:** `logs.action_logger`

### Class: `ActionLogger`

#### Constructor
```python
ActionLogger(db_path: str)
```

**Parameters:**
- `db_path` (str): Path to SQLite database

**Example:**
```python
from logs.action_logger import ActionLogger

logger = ActionLogger('/path/to/database.db')
```

#### Methods

##### `log_action()`
Log a system operation.

```python
log_action(
    action: str,
    category: str,
    status: str = "SUCCESS",
    entity_type: str = None,
    entity_id: int = None,
    user: str = None,
    old_data: Dict = None,
    new_data: Dict = None,
    error_msg: str = None,
    details: str = None
) -> int
```

**Parameters:**
- `action` (str): Operation name (CREATE, UPDATE, DELETE)
- `category` (str): Category (BATCH, SAMPLE, ANALYSIS, UNIT)
- `status` (str): SUCCESS, ERROR, PENDING
- `entity_type` (str): Type of entity (batch, sample, analysis, unit)
- `entity_id` (int): ID of entity
- `user` (str): User performing action
- `old_data` (dict): Previous data
- `new_data` (dict): New data
- `error_msg` (str): Error message if status=ERROR
- `details` (str): Additional details

**Returns:** Log ID (int)

**Example:**
```python
log_id = logger.log_action(
    "CREATE", "BATCH",
    entity_type="batch", entity_id=1,
    new_data={"batch_code": "ABC-1", "client_id": 1}
)
```

##### `get_logs()`
Retrieve logged operations.

```python
get_logs(
    limit: int = 100,
    category: str = None,
    entity_type: str = None,
    status: str = None
) -> List[Dict]
```

**Returns:** List of log dictionaries

**Example:**
```python
batch_logs = logger.get_logs(limit=50, category="BATCH")
errors = logger.get_logs(status="ERROR")
```

##### `get_entity_logs()`
Get all logs for specific entity.

```python
get_entity_logs(entity_type: str, entity_id: int) -> List[Dict]
```

**Example:**
```python
sample_logs = logger.get_entity_logs("sample", 42)
```

##### `get_recent_errors()`
Get recent error logs.

```python
get_recent_errors(limit: int = 20) -> List[Dict]
```

**Example:**
```python
errors = logger.get_recent_errors(limit=10)
```

##### `clear_old_logs()`
Delete logs older than specified days.

```python
clear_old_logs(days: int = 30)
```

**Example:**
```python
logger.clear_old_logs(days=30)  # Clear logs >30 days old
```

### Singleton Function

#### `get_logger()`
Get singleton logger instance.

```python
get_logger(db_path: str) -> ActionLogger
```

**Example:**
```python
from logs.action_logger import get_logger

logger = get_logger('/path/to/database.db')
```

---

## Undo Manager API

**Module:** `models.undo_manager`

### Class: `Action`

Represents an undoable action.

```python
@dataclass
class Action:
    name: str                    # Action name
    undo_fn: Callable           # Undo function
    redo_fn: Callable           # Redo function
    timestamp: str              # ISO timestamp
    data: Dict                  # Extra data
```

**Example:**
```python
from models.undo_manager import Action

action = Action(
    name="Add Sample",
    undo_fn=lambda: delete_sample(42),
    redo_fn=lambda: add_sample(sample_data),
    data={"sample_id": 42}
)
```

### Class: `UndoManager`

#### Constructor
```python
UndoManager(max_stack_size: int = 20)
```

**Parameters:**
- `max_stack_size` (int): Maximum undo stack size

**Example:**
```python
from models.undo_manager import UndoManager

undo_mgr = UndoManager(max_stack_size=20)
```

#### Methods

##### `record_action()`
Record an undoable action.

```python
record_action(action: Action)
```

**Example:**
```python
undo_mgr.record_action(action)
```

##### `undo()`
Undo last action.

```python
undo() -> tuple[bool, str]
```

**Returns:** (success: bool, message: str)

**Example:**
```python
success, msg = undo_mgr.undo()
if success:
    print(msg)  # "Undo: Add Sample"
```

##### `redo()`
Redo last undone action.

```python
redo() -> tuple[bool, str]
```

**Returns:** (success: bool, message: str)

**Example:**
```python
success, msg = undo_mgr.redo()
```

##### `can_undo()`
Check if undo is available.

```python
can_undo() -> bool
```

##### `can_redo()`
Check if redo is available.

```python
can_redo() -> bool
```

##### `get_undo_text()`
Get text for undo button.

```python
get_undo_text() -> str
```

**Returns:** "Undo" or "Undo: [action_name]"

##### `get_redo_text()`
Get text for redo button.

```python
get_redo_text() -> str
```

##### `get_history()`
Get action history.

```python
get_history() -> Dict
```

**Returns:** Dictionary with undo/redo counts and action names

---

## CRUD Operations - Units

**Module:** `models.crud`

### `get_all_units()`
Get all active measurement units.

```python
get_all_units(db_path: str) -> List[Dict]
```

**Returns:** List of unit dictionaries

**Example:**
```python
from models.crud import get_all_units

units = get_all_units('/path/to/db.sqlite')
for unit in units:
    print(f"{unit['name']} ({unit['symbol']})")
```

### `get_all_units_no_filter()`
Get all units (active + inactive).

```python
get_all_units_no_filter(db_path: str) -> List[Dict]
```

### `add_unit()`
Create new measurement unit.

```python
add_unit(
    db_path: str,
    name: str,
    symbol: str,
    description: str = "",
    category: str = ""
) -> tuple[bool, int|str]
```

**Returns:** (success: bool, result: int|str)
- On success: (True, unit_id)
- On error: (False, error_message)

**Example:**
```python
from models.crud import add_unit

success, result = add_unit(
    db_path,
    name="Χιλιόγραμμο",
    symbol="kg",
    description="Weight unit",
    category="Βάρος"
)

if success:
    print(f"Created unit ID: {result}")
else:
    print(f"Error: {result}")
```

### `update_unit()`
Update measurement unit.

```python
update_unit(
    db_path: str,
    unit_id: int,
    name: str,
    symbol: str,
    description: str = "",
    category: str = "",
    active: int = 1
) -> tuple[bool, str]
```

**Returns:** (success: bool, message: str)

### `delete_unit()`
Soft-delete measurement unit.

```python
delete_unit(db_path: str, unit_id: int)
```

### `get_unit_by_id()`
Get specific unit.

```python
get_unit_by_id(db_path: str, unit_id: int) -> Dict|None
```

---

## CRUD Operations - Sample Analysis

**Module:** `models.crud`

### `add_sample_analysis()`
Link analysis to sample.

```python
add_sample_analysis(
    db_path: str,
    sample_id: int,
    analysis_type_id: int,
    assigned_analyst_id: int = None
) -> tuple[bool, str]
```

**Returns:** (success: bool, message: str)

**Example:**
```python
from models.crud import add_sample_analysis

success, msg = add_sample_analysis(
    db_path,
    sample_id=5,
    analysis_type_id=2,
    assigned_analyst_id=1
)
```

### `get_sample_analyses()`
Get all analyses for sample.

```python
get_sample_analyses(db_path: str, sample_id: int) -> List[Dict]
```

**Returns:** List of analysis dictionaries

### `update_sample_analysis_stage()`
Update analysis stage.

```python
update_sample_analysis_stage(
    db_path: str,
    sample_analysis_id: int,
    stage: int
)
```

### `delete_sample_analysis()`
Remove analysis from sample.

```python
delete_sample_analysis(db_path: str, sample_analysis_id: int)
```

---

## Advanced Dialogs API

**Module:** `dialogs.advanced_dialogs`

### `UnitOfMeasurementDialog`
Dialog for creating/editing units.

```python
UnitOfMeasurementDialog(parent=None, data: dict = None)
```

**Methods:**
- `exec_()` - Show dialog
- `get_data()` - Return unit data

**Example:**
```python
from dialogs.advanced_dialogs import UnitOfMeasurementDialog

dialog = UnitOfMeasurementDialog(parent_window)
if dialog.exec_() == QDialog.Accepted:
    data = dialog.get_data()
    print(data)
```

### `UnitsManagerDialog`
Comprehensive units management.

```python
UnitsManagerDialog(db_path: str, parent=None)
```

### `SampleRangeSelectorDialog`
Select samples using ranges.

```python
SampleRangeSelectorDialog(db_path: str, batch_id: int, parent=None)
```

**Methods:**
- `exec_()` - Show dialog
- `get_selected_samples()` - Get list of selected sample numbers

**Example:**
```python
from dialogs.advanced_dialogs import SampleRangeSelectorDialog

selector = SampleRangeSelectorDialog(db_path, batch_id)
if selector.exec_() == QDialog.Accepted:
    samples = selector.get_selected_samples()
    print(samples)  # [1, 2, 3, 4, 7, 8, 9, ...]
```

### `BulkAnalysisAssignmentDialog`
Assign analyses to samples.

```python
BulkAnalysisAssignmentDialog(db_path: str, sample_numbers: list, parent=None)
```

**Methods:**
- `exec_()` - Show dialog
- `get_selected_analyses()` - Get list of analysis IDs

**Example:**
```python
dialog = BulkAnalysisAssignmentDialog(db_path, [1, 2, 3, 4])
if dialog.exec_() == QDialog.Accepted:
    analyses = dialog.get_selected_analyses()
    # Assign these analyses to all samples
```

### `MultiStageAnalysisDialog`
Configure multi-stage analyses.

```python
MultiStageAnalysisDialog(parent=None, analysis_data: dict = None)
```

**Methods:**
- `exec_()` - Show dialog
- `get_stages()` - Return stage configuration

---

## Database Schema Reference

### `unit_of_measurement` Table
```sql
CREATE TABLE unit_of_measurement (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    symbol      TEXT NOT NULL UNIQUE,
    description TEXT,
    category    TEXT,
    active      INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT NOT NULL DEFAULT (datetime('now','localtime'))
)
```

### `sample_analysis` Table
```sql
CREATE TABLE sample_analysis (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_id           INTEGER NOT NULL REFERENCES samples(id),
    analysis_type_id    INTEGER NOT NULL REFERENCES analysis_types(id),
    assigned_analyst_id INTEGER REFERENCES analysts(id),
    current_stage       INTEGER DEFAULT 1,
    status              TEXT NOT NULL DEFAULT 'PENDING',
    created_at          TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    UNIQUE(sample_id, analysis_type_id)
)
```

### `action_logs` Table
```sql
CREATE TABLE action_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    action      TEXT NOT NULL,
    category    TEXT NOT NULL,
    user        TEXT,
    entity_type TEXT,
    entity_id   INTEGER,
    status      TEXT NOT NULL DEFAULT 'SUCCESS',
    old_data    TEXT,
    new_data    TEXT,
    error_msg   TEXT,
    details     TEXT
)
```

---

## Error Handling

### Logger Error Handling
```python
try:
    logger.log_action(...)
except Exception as e:
    print(f"Logging failed: {e}")
```

### Undo Error Handling
```python
success, msg = undo_mgr.undo()
if not success:
    print(f"Undo failed: {msg}")
```

### CRUD Error Handling
```python
success, message = add_unit(db_path, ...)
if not success:
    print(f"Unit creation failed: {message}")
```

---

## Performance Tips

1. **Use batch operations** for multiple items
2. **Limit undo stack size** based on memory
3. **Clean old logs** regularly (> 30 days)
4. **Use indexes** for frequently searched fields
5. **Cache unit lists** when possible

---

## Version Information

- **API Version:** 2.0
- **Last Updated:** April 2026
- **Python:** 3.7+
- **PyQt5:** 5.15+

---

**For more information, see [FEATURES_GUIDE.md](FEATURES_GUIDE.md) and [README.md](README.md)**
