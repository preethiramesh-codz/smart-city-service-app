import sqlite3

conn = sqlite3.connect(r"C:\Users\PREETHI\OneDrive\Documents\hackathon_app\issue.db")

c = conn.cursor()

# USERS TABLE
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    phone TEXT PRIMARY KEY,
    role TEXT
)
""")

# ISSUES TABLE
c.execute("""
CREATE TABLE IF NOT EXISTS issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    title TEXT,
    description TEXT,
    location TEXT,
    status TEXT
)
""")

# PRELOAD ADMIN / COLLECTOR
c.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", ("+919999999999", "Collector"))

conn.commit()
conn.close()

print("✅ Database created successfully")
