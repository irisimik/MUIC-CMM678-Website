import sqlite3

file = [i.lower().split("\t") for i in open(("cmm.txt"), "r").read().strip().split("\n")]

conn = sqlite3.connect("datastore/main.db", timeout=30, isolation_level=None,check_same_thread=False)
conn.row_factory = sqlite3.Row

for i in file:
  stdid, email = i[0], i[1]
  print(email, stdid)
  conn.execute("""
    INSERT INTO users (email, studentid)
    VALUES (?, ?)
    ON CONFLICT(email) DO UPDATE SET
      studentid = excluded.studentid
  """, (email.split("@")[0], int(stdid)))
conn.commit()
