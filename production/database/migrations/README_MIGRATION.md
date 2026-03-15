# pgAdmin se Project Database Migration Guide

## Overview

Ye guide aapko pgAdmin 4 (PostgreSQL) se TechCorp Customer Success AI Agent project ke database mein tables migrate karne mein help karegi.

---

## Migration Methods

### Method 1: Python Script (Recommended)

**Step 1: Script configure karein**

File open karein: `production/database/migrations/import_from_pgadmin.py`

Neeche diye gaye section mein apne pgAdmin database ki details enter karein:

```python
# Source Database (pgAdmin - your existing database)
SOURCE_DB_HOST = "localhost"
SOURCE_DB_PORT = 5432
SOURCE_DB_NAME = "your_database_name"  # Change this
SOURCE_DB_USER = "postgres"
SOURCE_DB_PASSWORD = "your_password"  # Change this

# Tables to migrate (leave empty for all tables)
TABLES_TO_MIGRATE = [
    # Add your table names here
    "customers",
    "products",
    "orders",
]
```

**Step 2: Dependencies install karein**

```bash
pip install asyncpg
```

**Step 3: Migration run karein**

```bash
cd D:\GIAIC\Hackathon 5
python production/database/migrations/import_from_pgadmin.py
```

---

### Method 2: pgAdmin GUI Export/Import

**Step 1: pgAdmin mein Export**

1. pgAdmin 4 open karein
2. Apne database par right-click karein
3. **Backup...** select karein
4. Format: **Plain** select karein
5. **Dump options** tab mein:
   - ✓ **Only schema** (agar sirf structure chahiye)
   - ✓ **Only data** (agar sirf data chahiye)
   - ✓ **Pre-data & Post-data** (complete migration)
6. **Backup** button click karein

**Step 2: Target Database mein Import**

1. Project ke database par right-click karein (`fte_db`)
2. **Query Tool** open karein
3. Export ki gayi SQL file load karein
4. **Execute** (⚡) button click karein

---

### Method 3: pg_dump Command Line

**Step 1: Export from pgAdmin database**

```bash
# Sirf schema
pg_dump -U postgres -h localhost -s your_database_name > schema_export.sql

# Sirf data
pg_dump -U postgres -h localhost -a your_database_name > data_export.sql

# Complete (schema + data)
pg_dump -U postgres -h localhost your_database_name > full_export.sql
```

**Step 2: Import to project database**

```bash
# Docker container ke andar import
docker exec -i fte-postgres psql -U fte_user -d fte_db < schema_export.sql

# Ya localhost se (agar port 5432 exposed hai)
psql -U fte_user -h localhost -d fte_db < schema_export.sql
```

---

## Migration Modes

### Schema Only (Structure without data)

Script mein ye change karein:
```python
MIGRATE_SCHEMA_ONLY = True
MIGRATE_DATA_ONLY = False
```

### Data Only (Existing structure mein data)

```python
MIGRATE_SCHEMA_ONLY = False
MIGRATE_DATA_ONLY = True
```

### Complete Migration (Schema + Data)

```python
MIGRATE_SCHEMA_ONLY = False
MIGRATE_DATA_ONLY = False
```

---

## Common Issues & Solutions

### Issue 1: Connection Error

**Error:** `could not connect to database`

**Solution:**
```bash
# Check PostgreSQL is running
docker-compose ps

# Or for local PostgreSQL
pg_ctl status
```

### Issue 2: Database already exists

**Error:** `relation already exists`

**Solution:** Script mein ye change karein:
```python
DROP_EXISTING_TABLES = True
```

### Issue 3: Permission denied

**Error:** `permission denied for table`

**Solution:**
```sql
-- Target database mein run karein
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO fte_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO fte_user;
```

### Issue 4: Data type mismatch

**Error:** `column "X" is of type Y but expression is of type Z`

**Solution:** Manual SQL export use karein aur data types manually fix karein.

---

## Verification

Migration ke baad verify karein:

```bash
# Docker container ke andar
docker exec -it fte-postgres psql -U fte_user -d fte_db

# Tables list
\dt

# Count rows in each table
SELECT 'customers' as table_name, COUNT(*) FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders;
```

---

## Post-Migration Steps

### 1. Run project schema

Agar aapne sirf apni tables migrate ki hain, to project ka schema bhi apply karein:

```bash
docker exec -i fte-postgres psql -U fte_user -d fte_db < production/database/schema.sql
```

### 2. Verify relationships

Check foreign keys:
```sql
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
WHERE constraint_type = 'FOREIGN KEY';
```

### 3. Test application

```bash
# Backend start karein
cd production
docker-compose up -d

# Health check
curl http://localhost:8000/health
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `pg_dump -U postgres -s dbname > schema.sql` | Export schema |
| `pg_dump -U postgres -a dbname > data.sql` | Export data |
| `psql -U fte_user -d fte_db < file.sql` | Import SQL |
| `docker exec -it fte-postgres psql -U fte_user -d fte_db` | DB shell |
| `\dt` | List tables |
| `\d tablename` | Describe table |

---

## Need Help?

Agar migration mein koi issue ho to:

1. **Error logs check karein** - Script detailed error messages deti hai
2. **Database connections verify karein** - Credentials sahi hain?
3. **Table names confirm karein** - Case-sensitive hain (lowercase recommended)

---

**Happy Migrating! 🚀**
