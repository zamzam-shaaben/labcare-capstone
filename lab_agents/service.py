"""Data-access services reused by MCP server and tests."""
import json
import re
import sqlite3
from .database import connect, initialize

HOURS = {'Monday-Friday':'07:30-17:00','Saturday':'08:00-13:00','Sunday':'Closed', 'address':'Demo Lab, Beirut (fictional)', 'phone':'Demo only; no real telephone service'}

def prices(query=''):
    initialize()
    with connect() as con:
        rows = [dict(r) for r in con.execute('SELECT * FROM tests ORDER BY code')]
    q = query.strip().casefold()
    note = 'Illustrative prices only; not a real laboratory quote.'
    if q:
        text = {r['code']:(' '.join(str(v) for v in r.values())).casefold() for r in rows}
        # Whole phrase first, then any word of it (a model may pass "TSH price" rather than "TSH").
        hits = [r for r in rows if q in text[r['code']]] or [r for r in rows if any(w in text[r['code']] for w in q.split() if len(w)>2)]
        if hits: rows = hits
        else: note = 'No test matched the query; the full catalog is returned. ' + note
    return {'currency':'USD','items':rows,'note':note}

def hours(): return {'hours':HOURS,'note':'Fictional schedule; demonstration only.'}

def slots():
    initialize()
    with connect() as con:
        data = [dict(r) for r in con.execute('''SELECT s.id,s.day,s.time,s.capacity-COUNT(a.id) AS remaining
                    FROM slots s LEFT JOIN appointments a ON a.slot_id=s.id
                    GROUP BY s.id ORDER BY s.day,s.time''')]
    return {'slots':[s for s in data if s['remaining']>0], 'note':'Demo-only appointment slots, not connected to a real lab.'}

def booking(slot_id:int,customer_name:str,test_code:str,confirmed:bool=False):
    if not confirmed: return {'ok':False,'error':'Explicit confirmation required before creating a booking.'}
    name = customer_name.strip()
    if not 2<=len(name)<=80 or not re.fullmatch(r'[\w\s\-\u0600-\u06ff]+',name,re.UNICODE):
        return {'ok':False,'error':'Please provide a valid name (2–80 characters).'}
    initialize()
    with connect() as con:
        con.execute('BEGIN IMMEDIATE')
        t = con.execute('SELECT code FROM tests WHERE UPPER(code)=UPPER(?)',(test_code,)).fetchone()
        slot=con.execute('SELECT capacity FROM slots WHERE id=?',(slot_id,)).fetchone()
        count=con.execute('SELECT COUNT(*) FROM appointments WHERE slot_id=?',(slot_id,)).fetchone()[0]
        if not t or not slot: return {'ok':False,'error':'Unknown test or appointment slot.'}
        if count>=slot['capacity']:return {'ok':False,'error':'This appointment is now full.'}
        cur=con.execute('INSERT INTO appointments(slot_id,customer_name,test_code) VALUES (?,?,?)',(slot_id,name,t['code']))
        return {'ok':True,'booking_id':cur.lastrowid,'message':'Demo appointment created; no real laboratory notified.'}

def result(report_id:str,access_code:str):
    initialize()
    # Access code is a demo secret; require both factors, avoid exposing it in output.
    with connect() as con:
        rec=con.execute('SELECT report_id, status, summary FROM results WHERE report_id=? AND access_code=?',(report_id.strip(),access_code.strip())).fetchone()
    if not rec: return {'ok':False,'error':'Report not found or access code incorrect.'}
    if rec['status']!='released':return {'ok':True,'status':'pending','message':'The report is not yet released.'}
    return {'ok':True,'status':'released','report_id':rec['report_id'],'summary':rec['summary'], 'note':'DEMO REPORT ONLY. No diagnosis is provided.'}
