"""SQLite demo repository. No actual patient information."""
import os
import sqlite3
from pathlib import Path

DB = Path(os.getenv('LAB_DB_PATH', str(Path(__file__).parent.parent / 'lab_demo.sqlite3')))

SCHEMA = '''
CREATE TABLE IF NOT EXISTS tests (code TEXT PRIMARY KEY, name_en TEXT, name_ar TEXT, price_usd REAL, turnaround TEXT, preparation TEXT);
CREATE TABLE IF NOT EXISTS slots (id INTEGER PRIMARY KEY, day TEXT, time TEXT, capacity INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS appointments (id INTEGER PRIMARY KEY AUTOINCREMENT, slot_id INTEGER, customer_name TEXT, test_code TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(slot_id) REFERENCES slots(id));
CREATE TABLE IF NOT EXISTS results (report_id TEXT PRIMARY KEY, access_code TEXT, patient_label TEXT, status TEXT, summary TEXT);
'''

def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    return con

def initialize():
    with connect() as con:
        con.executescript(SCHEMA)
        if not con.execute('SELECT 1 FROM tests LIMIT 1').fetchone():
            con.executemany('INSERT INTO tests VALUES (?,?,?,?,?,?)', [
                ('CBC','Complete Blood Count','تعداد الدم الكامل',12,'Same day','No fasting normally required'),
                ('LIPID','Lipid Profile','دهون الدم',22,'Next working day','Ask the laboratory about fasting instructions'),
                ('TSH','Thyroid Stimulating Hormone','تحليل الغدة الدرقية',18,'Next working day','Tell staff about any thyroid medication'),
                ('VITD','Vitamin D','فيتامين د',28,'2 working days','No special preparation usually required'),
                ('FBS','Fasting Blood Sugar','سكر صائم',9,'Same day','Fasting generally required; confirm with laboratory')])
        if not con.execute('SELECT 1 FROM slots LIMIT 1').fetchone():
            con.executemany('INSERT INTO slots(id,day,time,capacity) VALUES (?,?,?,?)', [
                (1,'2027-01-11','09:00',2),(2,'2027-01-11','10:00',2),(3,'2027-01-12','09:00',2),
                (4,'2027-01-12','11:00',2),(5,'2027-01-13','08:30',2)])
        if not con.execute('SELECT 1 FROM results LIMIT 1').fetchone():
            con.executemany('INSERT INTO results VALUES (?,?,?,?,?)', [
                ('DEMO-1001','472915','Sample Patient A','released','Demo CBC: report ready. Contact the laboratory for clinical interpretation.'),
                ('DEMO-1002','831264','Sample Patient B','pending',''),
                ('DEMO-1003','199204','Sample Patient C','released','Demo Vitamin D: report ready. Contact the laboratory for interpretation.')])
