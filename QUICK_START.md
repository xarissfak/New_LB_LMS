# 🚀 Quick Start Guide

Get up and running with LabTrack in 5 minutes!

## Prerequisites
- Python 3.7+
- pip (comes with Python)

## Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/xarissfak/New_LB_LMS.git
   cd New_LB_LMS
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**
   ```bash
   python main.py
   ```

## Initial Setup (First Time Only)

### Step 1: Create Database
1. Application starts → Click "Νέα Βάση"
2. Choose location to save `.db` file
3. Click "Create Database"

### Step 2: Add Master Data
1. Navigate to **⚙️ Master Data** tab
2. Add your data:
   - **👥 Πελάτες** - Click "➕ Νέος Πελάτης"
   - **🔬 Αναλυτές** - Click "➕ Νέος Αναλυτής"
   - **🧪 Είδη Ανάλυσης** - Click "➕ Νέα Ανάλυση"
   - **📐 Μονάδες Μέτρησης** - Click "➕ Νέα Μονάδα"

### Step 3: Create First Batch
1. Go to **🗂 Batches & Δείγματα** tab
2. Click "➕ Νέο Batch"
3. **IMPORTANT:** Specify number of samples upfront
4. Click "Δημιουργία Batch"

## Daily Usage

### Create New Batch
```
1. Click "➕ Νέο Batch"
2. Select Client
3. Enter Number of Samples (e.g., 5)
4. Click "Δημιουργία Batch"
```

### Add Analyses to Samples
```
Option A - Individual:
1. Click sample in table
2. Click "🔄 Κατάσταση"
3. Select analysis type

Option B - Bulk (NEW!):
1. Samples 1-4: Select via range "1-4"
2. Click "Ανάθεση"
3. Select analyses
4. They're assigned to all 4 samples
```

### Update Sample Status
```
1. Select sample
2. Click "🔄 Κατάσταση"
3. Choose new status
4. Optionally assign analyst
5. Click "Αποθήκευση"
```

### Enter Results
```
1. Select sample
2. Click "📝 Αποτέλεσμα"
3. Enter result value
4. Add notes if needed
5. Click "Αποθήκευση Αποτελέσματος"
```

### View Logs
```
1. Logs dialog (to be added to main menu)
2. Filter by category or status
3. View detailed information
4. See before/after data
```

## Tips & Tricks

### 🔢 Range Selection
Select multiple samples quickly:
- `1-4` → Samples 1, 2, 3, 4
- `1-4, 7-13` → Samples 1-4 and 7-13
- `1, 3, 5` → Samples 1, 3, 5

### ➕ Multi-Stage Analysis
Configure analyses with multiple stages:
1. Create Analysis Type
2. Add Stage 1 (default)
3. Click "➕ Προσθήκη Σταδίου"
4. Configure Stage 2 with different parameters
5. Repeat for more stages

### 📐 Measurement Units
Pre-populate common units:
1. Master Data → 📐 Μονάδες Μέτρησης
2. Click "➕ Νέα Μονάδα"
3. Add (e.g., "kg", "pH", "CFU/mL")
4. Organize by category

### 📋 Debugging
Check what's happening:
1. View Logs dialog
2. Filter by BATCH, SAMPLE, or ANALYSIS
3. See errors with error messages
4. View exactly what changed (before/after data)

## Common Issues

### Database Won't Open
- Delete old `.db` file and create new one
- Verify Python version (3.7+)

### No Data Appears After Selection
- Ensure you selected at least one item
- Check database has master data

### Changes Not Appearing
- Refresh view or restart application
- Check action logs for errors

---

## 📚 Learn More

- **[README.md](README.md)** - Full documentation
- **[FEATURES_GUIDE.md](FEATURES_GUIDE.md)** - Detailed feature explanations
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical details

---

## 🆘 Need Help?

1. Check the documentation files above
2. Review action logs for errors
3. Check sample status history
4. Verify all master data is entered

---

**Ready to go!** 🎉 Start creating batches and tracking analyses.
