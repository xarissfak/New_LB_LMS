# 🧪 LabTrack — Mini LIMS

Εφαρμογή διαχείρισης δειγμάτων εργαστηρίου (Python + PyQt6 + SQLite).

## Εγκατάσταση

```bash
pip install PyQt6
```

## Εκτέλεση

```bash
cd lab_lims
python main.py
```

## Δομή Project

```
lab_lims/
├── main.py                        # Σημείο εκκίνησης
├── requirements.txt
├── database/
│   ├── __init__.py
│   └── db_manager.py              # Δημιουργία DB, migration, status constants
├── models/
│   ├── __init__.py
│   └── crud.py                    # Όλες οι CRUD λειτουργίες
├── dialogs/
│   ├── __init__.py
│   ├── startup_dialog.py          # Νέα Βάση / Import Βάσης
│   ├── master_dialogs.py          # Client, Analyst, AnalysisType dialogs
│   └── batch_sample_dialogs.py   # Batch, Sample, Status, Result, History dialogs
└── views/
    ├── __init__.py
    ├── main_window.py             # Κύριο παράθυρο + sidebar
    ├── dashboard_view.py          # Dashboard με στατιστικά
    ├── master_data_view.py        # Διαχείριση Master Data
    └── samples_view.py            # Καθημερινή ροή εργασίας
```

## Ροή Χρήσης

### Πρώτη φορά:
1. Εκτέλεση → `Νέα Βάση` → αποθήκευση `.db` αρχείου
2. `⚙️ Master Data` → Προσθήκη Αναλυτών, Πελατών, Ειδών Ανάλυσης
3. `🗂 Batches & Δείγματα` → Νέο Batch → Προσθήκη Δειγμάτων

### Καθημερινά:
1. Άνοιγμα → `Import Βάσης` → επιλογή `.db`
2. Νέο Batch για κάθε παρτίδα
3. Προσθήκη δειγμάτων με αυτόματο ID (π.χ. `Γιώργος-1/S1`)
4. Ενημέρωση κατάστασης ανά στάδιο

## Στάδια Δείγματος

| Κωδικός | Ελληνικά |
|---------|----------|
| RECEIVED | Παραλαβή |
| IN_ANALYSIS | Προς Ανάλυση |
| ANALYZED | Αναλύθηκε |
| PENDING | Αναμονή |
| COMPLETED | Ολοκλήρωση |
| SHIPPED | Αποστολή |

## Παραμετροποίηση

Για να προσθέσεις νέα πεδία ή αναλύσεις:
- `database/db_manager.py` — αλλαγές στο schema
- `models/crud.py` — προσθήκη CRUD functions
- `dialogs/master_dialogs.py` — νέα UI fields
