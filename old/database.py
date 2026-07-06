import os
import pickle
import sqlite3


def UserStorage(DB):
  con = sqlite3.connect(DB)
  con.execute("""
    CREATE TABLE IF NOT EXISTS users (
      email TEXT PRIMARY KEY,
      sessionId TEXT UNIQUE,
      expiration REAL,
      name TEXT,
      studentid INT
    )
  """)
  con.commit()
  return con