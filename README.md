# 🧪 LabTrack — Laboratory Management System (LB LMS)

**Advanced sample and analysis management system** for laboratory workflows with comprehensive logging, multi-stage analysis support, and batch operations.

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)](https://pypi.org/project/PyQt5/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue.svg)](https://www.sqlite.org/)

## 🎯 Key Features

### Core Features (v1.0)
- ✅ Sample and batch management
- ✅ Multi-step workflow tracking
- ✅ Analyst assignment
- ✅ Result entry and reporting

### New Features (v2.0) 🚀
- ✅ **Action Logging** - Complete audit trail with timestamps, errors, and before/after data
- ✅ **Undo/Redo System** - 20-action stack for mistake recovery
- ✅ **Units of Measurement** - Dedicated master data for measurement units
- ✅ **Multi-Stage Analysis** - Configure and track multi-step analyses
- ✅ **Range-Based Sampling** - Select samples using ranges (1-4, 7-13, 15)
- ✅ **Bulk Operations** - Assign analyses to multiple samples at once
- ✅ **Enhanced Batch Creation** - Pre-define sample count and auto-assign analyses
- ✅ **Comprehensive Logging UI** - View, filter, and search complete action history

---

## 📋 Installation & Setup

### Prerequisites
- Python 3.7+
- pip

### Installation

```bash
# Clone repository
git clone https://github.com/xarissfak/New_LB_LMS.git
cd New_LB_LMS

# Install dependencies
pip install -r requirements.txt
```

### Run Application

```bash
python main.py
```

---

## 📁 Project Structure

```
./
├── main.py                                 # Application entry point
├── requirements.txt                        # Dependencies
│
├── README.md                               # This file
├── FEATURES_GUIDE.md                       # Complete feature documentation
├── IMPLEMENTATION_SUMMARY.md               # Implementation details
│
├── database/
│   ├── __init__.py
│   ├── db_manager.py                       # Database creation, migration, schema v2
│   └── export_utils.py
│
├── models/
│   ├── __init__.py
│   ├── crud.py                             # All CRUD operations (+12 new functions)
│   ├── undo_manager.py                     # ✨ NEW: Undo/redo system
│   └── export_utils.py
│
├── logs/
│   ├── __init__.py
│   └── action_logger.py                    # ✨ NEW: Action logging engine
│
├── dialogs/
│   ├── __init__.py
│   ├── startup_dialog.py                   # New Database / Import Database
│   ├── master_dialogs.py                   # Client, Analyst, AnalysisType
│   ├── batch_sample_dialogs.py             # Batch, Sample, Status, Result, History
│   ├── advanced_dialogs.py                 # ✨ NEW: Advanced features
│   │   ├── UnitOfMeasurementDialog
│   │   ├── UnitsManagerDialog
│   │   ├── SampleRangeSelectorDialog
│   │   ├── BulkAnalysisAssignmentDialog
│   │   └── MultiStageAnalysisDialog
│   └── logs_dialog.py                      # ✨ NEW: Logs viewer UI
│
└── views/
    ├── __init__.py
    ├── main_window.py                      # Main window + sidebar navigation
    ├── dashboard_view.py                   # Dashboard with statistics
    ├── master_data_view.py                 # ⭐ UPDATED: Added units management tab
    └── samples_view.py                     # ⭐ UPDATED: Logger integration, batch handling
```

---

## 🚀 Quick Start

### First Time Setup

1. **Launch Application**
   ```bash
   python main.py
   ```

2. **Create New Database**
   - Click "Νέα Βάση" → Save `.db` file

3. **Setup Master Data** (⚙️ Master Data section)
   - **👥 Πελάτες** - Add clients
   - **🔬 Αναλυτές** - Add analysts
   - **🧪 Είδη Ανάλυσης** - Add analysis types
   - **📐 Μονάδες Μέτρησης** - ✨ Add measurement units

4. **Create First Batch** (🗂 Batches & Δείγματα)
   - Click "➕ Νέο Batch"
   - Select client
   - **Specify number of samples upfront** ✨
   - Optionally bulk-assign analyses ✨

### Daily Workflow

1. **Open Database**
   - Click "Import Βάσης" → Select `.db` file

2. **Create Batch**
   - "➕ Νέο Batch" → Fill details → Create

3. **Manage Samples**
   - ➕ Add individual samples
   - 🔢 Or use range selector (1-4, 7-13) ✨
   - ⚡ Bulk assign analyses ✨

4. **Update Status & Results**
   - Select sample → 🔄 Update status
   - 📝 Enter results

5. **Monitor & Debug**
   - 📋 View logs for complete audit trail ✨
   - Filter by category and status ✨

---

## 📊 Sample Status Workflow

```
RECEIVED (Blue)
    ↓
IN_ANALYSIS (Orange)
    ↓
ANALYZED (Purple)
    ↓
PENDING (Red)
    ↓
COMPLETED (Green)
    ↓
SHIPPED (Gray)
```

| Status Code | Description |
|------------|-------------|
| RECEIVED | Sample received from client |
| IN_ANALYSIS | Analysis in progress |
| ANALYZED | Analysis completed |
| PENDING | Awaiting further action |
| COMPLETED | Final results ready |
| SHIPPED | Sent back to client |

---

## ✨ New Features Guide

### 1. **Action Logging** 📋
Complete audit trail of all operations:
- Timestamp, user, operation type
- Before/after data comparison
- Error tracking and debugging
- **Access:** Logs viewer dialog (to be added to main menu)

**See:** [FEATURES_GUIDE.md](FEATURES_GUIDE.md#-1-action-logging-system) - Feature 1

---

### 2. **Undo/Redo System** ↩️
Recover from mistakes:
- 20-action undo stack
- Automatic error rollback
- Action history with timestamps

**See:** [FEATURES_GUIDE.md](FEATURES_GUIDE.md#-2-undoredo-system) - Feature 2

---

### 3. **Enhanced Batch Creation** 🎯
Pre-define batch details:
- Specify sample count upfront
- Auto-generate sample references
- Optional bulk analysis assignment

**Workflow:**
```
1. Create Batch
   ├─ Select Client
   ├─ Enter Batch Code (auto-generated)
   ├─ ✨ Specify Sample Count (NEW!)
   └─ Add Notes

2. Optional: Bulk Assign Analyses
   ├─ System shows analysis assignment dialog
   ├─ Select desired analysis types
   └─ Apply to all samples
```

**See:** [FEATURES_GUIDE.md](FEATURES_GUIDE.md#-3-enhanced-batch-dialog-with-sample-count) - Feature 3

---

### 4. **Range-Based Sample Selection** 🔢
Quick multi-sample operations:
- Input format: `1-4, 7-13, 15`
- Real-time preview
- Smart validation

**Example:**
```
Input: "1-4, 7-13"
Selected: [1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 13]
```

**See:** [FEATURES_GUIDE.md](FEATURES_GUIDE.md#-6-multi-select-samples-with-range-support) - Feature 6

---

### 5. **Bulk Analysis Assignment** ⚡
Assign analyses to multiple samples:
- Select samples via ranges
- Multi-select analysis types
- Apply all at once

**Workflow:**
```
1. Select samples (1-4, 7-13)
2. Choose analyses from list
3. Click "Ανάθεση"
4. All selected samples get all analyses
```

**See:** [FEATURES_GUIDE.md](FEATURES_GUIDE.md#-7-bulk-analysis-assignment) - Feature 7

---

### 6. **Units of Measurement** 📐
Master data for measurement units:
- **Location:** Master Data → 📐 Μονάδες Μέτρησης tab
- **Operations:** Add, Edit, Delete (all button-based)
- **Manager:** Click "🎯 Διαχείριση" for full view
- **Categories:** Weight, Volume, Concentration, etc.

**Workflow:**
```
⚙️ Master Data
  └─ 📐 Μονάδες Μέτρησης
     ├─ 🎯 Διαχείριση (Full manager)
     ├─ ➕ Νέα Μονάδα
     ├─ ✏️ Επεξεργασία
     └─ 🗑 Διαγραφή
```

**See:** [FEATURES_GUIDE.md](FEATURES_GUIDE.md#-6-units-of-measurement-management) - Feature 6

---

### 7. **Multi-Stage Analysis** ⚙️
Configure complex multi-step analyses:
- Start with STAGE: 1 (default)
- ➕ Add additional stages (2, 3, etc.)
- Configure per stage:
  - Temperature (°C)
  - Duration (hours)
  - Custom notes

**Example Configuration:**
```
STAGE: 1 - Προετοιμασία
├─ Temperature: 25°C
├─ Duration: 2 hours
└─ Notes: Prepare medium

STAGE: 2 - Επώαση
├─ Temperature: 37°C
├─ Duration: 48 hours
└─ Notes: Incubate in oven
```

**See:** [FEATURES_GUIDE.md](FEATURES_GUIDE.md#-5-multi-stage-analysis-configuration) - Feature 5

---

### 8. **Logs Viewer** 📊
Complete audit trail UI:
- 📋 View all operations
- 🔍 Filter by category (BATCH, SAMPLE, ANALYSIS, UNIT)
- 📊 Filter by status (SUCCESS, ERROR, PENDING)
- 📝 View before/after data
- 🗑 Auto-clean old logs (>30 days)

**See:** [FEATURES_GUIDE.md](FEATURES_GUIDE.md#-9-database-enhancements) - Feature 9

---

## 🗄️ Database Schema

### New Tables (v2.0)

#### `unit_of_measurement`
Store measurement units with categories:
```sql
CREATE TABLE unit_of_measurement (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    symbol      TEXT NOT NULL UNIQUE,
    description TEXT,
    category    TEXT,
    active      INTEGER DEFAULT 1,
    created_at  TEXT
)
```

#### `sample_analysis`
Support multiple analyses per sample:
```sql
CREATE TABLE sample_analysis (
    id                  INTEGER PRIMARY KEY,
    sample_id           INTEGER NOT NULL,
    analysis_type_id    INTEGER NOT NULL,
    assigned_analyst_id INTEGER,
    current_stage       INTEGER DEFAULT 1,
    status              TEXT DEFAULT 'PENDING',
    created_at          TEXT
)
```

#### `action_logs`
Complete audit trail:
```sql
CREATE TABLE action_logs (
    id          INTEGER PRIMARY KEY,
    timestamp   TEXT NOT NULL,
    action      TEXT NOT NULL,
    category    TEXT NOT NULL,
    user        TEXT,
    entity_type TEXT,
    entity_id   INTEGER,
    status      TEXT,
    old_data    TEXT,
    new_data    TEXT,
    error_msg   TEXT,
    details     TEXT
)
```

### Schema Version
- **Current:** v2
- **Auto-migration:** Yes (from v1 → v2)
- **Data preservation:** Yes

---

## 🔧 Configuration

### Add New Measurement Unit
```python
from models.crud import add_unit

add_unit(
    db_path,
    name="Χιλιόγραμμο",
    symbol="kg",
    description="Weight unit",
    category="Βάρος"
)
```

### View Action Logs
```python
from dialogs.logs_dialog import ActionLogsDialog

dialog = ActionLogsDialog(db_path, parent_window)
dialog.exec_()
```

### Use Undo System
```python
from models.undo_manager import UndoManager, Action

undo_mgr = UndoManager()

# Create action
action = Action(
    name="Add Sample",
    undo_fn=lambda: delete_sample(id),
    redo_fn=lambda: add_sample(data)
)

# Record and perform undo
undo_mgr.record_action(action)
success, msg = undo_mgr.undo()
```

---

## 📚 Documentation

- **[FEATURES_GUIDE.md](FEATURES_GUIDE.md)** - Comprehensive feature documentation
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Implementation details and integration guide

---

## 🐛 Troubleshooting

### Database Migration Issues
- Application automatically migrates from v1 → v2
- If issues occur, delete existing `.db` and create new

### Logs Not Appearing
- Check `action_logs` table exists
- Verify logging is enabled in operations

### Undo Not Working
- Undo stack is in-memory only (resets on app restart)
- Use action logs for persistent history

---

## 🤝 Contributing

Improvements and suggestions welcome!

---

## 📄 License

Open source - use freely for laboratory management.

---

## 📞 Support

For detailed information about features:
1. See **[FEATURES_GUIDE.md](FEATURES_GUIDE.md)**
2. Check **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)**
3. Review docstrings in source code

---

**Last Updated:** April 2026 | Version 2.0 ✨
