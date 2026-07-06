from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import json
import requests
import time
import secrets
from database import UserStorage
import websockets
import mimetypes
from threading import Thread

ROOT = "./public"
GOOGLE_CLIENT_ID = "129888425055-3pjo67u82p3q25oe7biebfitfmajjplh.apps.googleusercontent.com"

userdb = UserStorage("datastore/main.db")


class Serv(BaseHTTPRequestHandler):
  def is_thai(self):
    return self.headers.get("CF-IPCountry", "--") == "TH"
  
  def log_request_info(self, status_code):
    ip = self.headers.get("CF-Connecting-IP", self.client_address[0])
    ua = self.headers.get("User-Agent", "-")
    country = self.headers.get("CF-IPCountry", "--")
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    CLR = '\033[31m' if status_code > 299 else '\033[32m'
    print(f"[\033[36m{ts}\033[0m]\n- {ip} {country}\n- {self.command}\n  {self.path}\n  \"{ua}\"\n> CODE : {CLR}{status_code}\033[0m <\n")
  def log_message(self, format, *args):
    pass
  def reply(self, msg, code=200, content_type=None, dontcache = False):
    self.send_response(code)
    self.send_header("Server", "static")

    if content_type:
      self.send_header("Content-Type", content_type)
      self.send_header("Content-Length", str(len(msg)))

    self.send_header("X-Content-Type-Options", "nosniff")
    if dontcache:
      self.send_header("Cache-Control", "no-store")
    self.send_header("Connection", "close")
    self.end_headers()
    self.wfile.write(msg)
    self.log_request_info(code)

  def do_POST(self):
    def getjson():
      length = int(self.headers.get("Content-Length", 0))
      body = self.rfile.read(length).decode("utf-8")
      return json.loads(body) if length != 0 else dict()
    def getcookie():
      if not "Cookie" in self.headers:
        return dict()
      cookie_header_value = self.headers["Cookie"]

      return (dict(i.split('=', 1) for i in cookie_header_value.split('; ')))
      
    if self.path == "/login":
      print("RECV POST IN LOGIN")
      data = getjson()
      id_token_raw = data.get("idToken")
      if not id_token_raw:
        self.reply(b"Missing ID token", 400)
        return

      try:
        res = requests.get("https://oauth2.googleapis.com/tokeninfo?id_token="+id_token_raw)
        payload = res.json()

        if payload["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
          raise ValueError("Wrong issuer")
        email = payload.get("email")
        name = payload.get("name")
        #'iss', 'azp', 'aud', 'sub', 'hd', 'email', 'email_verified', 'nbf', 'name', 'picture', 'given_name', 'family_name', 'iat', 'exp', 'jti', 'alg', 'kid', 'typ']
      except Exception as e:
        print("ERROR DURING AUTH",e)
        self.invreq()
        return

      if not email.endswith("@student.mahidol.edu"):
        self.reply(json.dumps({"status": "Invalid email"}).encode("utf-8"), 200, content_type="application/json")
        return

      print("Authenticated user:", email)

      output = {
        "status": "success",
        "studentid": None,
        "email": email,
        "sessionId": None
      }

      row = userdb.execute(
        "SELECT sessionId, expiration, name, studentid FROM users WHERE email=?",
        (email.split("@")[0],)
      ).fetchone()
      if row is None:
        self.reply(b"Invalid request", 400)
        return

      retdata = {
        "sessionId": row[0] if row else None,
        "expiration": row[1] if row else 0,
        "name": row[2] if row else None,
        "studentid": row[3] if row else None
      }
      print("ROW",row)

      sessionId = retdata.get("sessionId")
      if sessionId is None:
        print("This login is non")
        sessionId = secrets.token_urlsafe(32)
      expirationT = retdata.get("expiration") or 0
      
      if time.time() > expirationT:
        sessionId = secrets.token_urlsafe(32)
        expirationT = time.time() + (60*60*24)
      
      # change sessionid if already exist on other email
      success = False
      for i in range(50):
        result = userdb.execute(
          "SELECT name FROM users WHERE sessionId=? AND email!=?",
          (sessionId, email.split("@")[0])
        ).fetchone()
        if result is None:
          success = True
          break
        sessionId = secrets.token_urlsafe(32)
      if not success:
        print("Exhausted attempt for session id generation for some reason D:")
        self.reply(b"Token generator fault", 500)
        return

      userdb.execute("""
      INSERT INTO users (email, sessionId, expiration, name)
      VALUES (?, ?, ?, ?)
      ON CONFLICT(email) DO UPDATE SET 
        sessionId=excluded.sessionId,
        expiration=excluded.expiration,
        name=excluded.name;
      """, (email.split("@")[0], sessionId, expirationT, payload.get("name")))
      userdb.commit()
      output["sessionId"] = sessionId
      output["studentid"] = retdata.get("studentid")

      self.reply(json.dumps(output).encode("utf-8"), 200, content_type="application/json")
    elif self.path == "/idbind":
      print("RECV POST IN IDBIND")
      data = getjson()

      sessionId = data.get("sessionId")
      studentId = data.get("studentId")
      if sessionId is None or studentId is None:
        self.reply(b"Invalid request", 400)
        print("invalid request in idbind (sessionid or studentid missing)")
        return
      print("SessionID",sessionId)

      # check expiration
      t = userdb.execute(
        "SELECT expiration FROM users WHERE sessionId=?",
        (sessionId,)
      ).fetchone()
      if t is None:
        self.reply(b"Invalid request", 400)
        return
      t = t[0]
      success = False
      if time.time() < t:
        userdb.execute("""
        INSERT INTO users (sessionId, studentid)
        VALUES (?, ?)
        ON CONFLICT(sessionId) DO UPDATE SET
          studentid = excluded.studentid
        """, (sessionId, studentId))
        userdb.commit()
        success = True
      else:
        print("TOKEN EXPIRED")
      self.reply(json.dumps({"success" : success}).encode("utf-8"), 200, "application/json")
    elif self.path == "/stampcheck":
      print("RECV NEW STAMP CHECK")
      data = getjson()
      sessionId = data.get("sessionId")
      if sessionId is None:
        self.reply(b"Invalid request 1", 400)
        return
      queried = userdb.execute(
        "SELECT expiration, stamps FROM users WHERE sessionId=?",
        (sessionId,)
      ).fetchone()
      if queried is None:
        self.reply(b"Invalid token", 400)
        return
      t = queried[0]
      encstamp = queried[1] or ""

      if time.time() > t:
        self.reply(json.dumps({"success": False, "reason": "Expired token"}).encode("utf-8"), 200, "application/json")
        return
      keyv = json.loads(open("stampmapping.json","r").read())
      output = {
        "success": True,
        "stamps": ["default"] + [keyv.get(i, "") for i in encstamp.split(",")]
      }
      self.reply(json.dumps(output).encode("utf-8"), 200, "application/json")
    elif self.path == "/getstampdata":
      self.reply(open("stampdata.json", "rb").read(), 200, "application/json")
    elif self.path == "/getboarddata":
      self.reply(open("boarddata.json", "rb").read(), 200, "application/json")
    elif self.path == "/eventsdata":
      self.reply(open("eventsdata.json", "rb").read(), 200, "application/json")
    elif self.path == "/rubnonggroup":
      data = getcookie()
      sessionId = data.get("session_id")
      if sessionId is None:
        self.reply(b"Invalid request 1", 400)
        return
      queried = userdb.execute(
        "SELECT expiration, studentid FROM users WHERE sessionId=?",
        (sessionId,)
      ).fetchone()
      if queried is None:
        self.reply(json.dumps({"success": False, "reason": "Expired token"}).encode("utf-8"), 200, "application/json")
        return
      t = queried[0]
      studentid = queried[1]

      if time.time() > t:
        self.reply(json.dumps({"success": False, "reason": "Expired token"}).encode("utf-8"), 200, "application/json")
        return
      
      if studentid is None:
        self.reply(json.dumps({"success": False, "reason": "No ID"}).encode("utf-8"), 200, "application/json")
        return
      
      groupdata = json.loads(open("ticketmap.json", "r").read())
      group = json.loads(open("rubnongdata.json", "r").read()).get(str(studentid))

      if group is None:
        group = "default"
      self.reply(json.dumps(groupdata[group]).encode("utf-8"), 200, "application/json")
    else:
      self.reply("unknown path".encode('utf-8'), 404)
    
      

  def do_GET(self):
    #if not self.is_thai():
      #self.reply("Disable your VPN.".encode("utf-8"), 403)
      #print("GEO BLOCKED")
      #return
    #print(self.path.split("?")[1:])
    self.path = self.path.split("?")[0]
    if self.path == '/':
      self.path = '/index.html'

    safe_path = os.path.normpath(self.path).lstrip("/").lstrip("\\")
    full_path = os.path.abspath(os.path.join(ROOT, safe_path))

    #print(f"REQ PATH = {os.path.join(ROOT, safe_path)} comp {full_path}")

    if not full_path.startswith(os.path.abspath(ROOT)):
      self.send_response(403)
      self.end_headers()
      return
    code = 200
    mime_type = None
    try:
      if not os.path.isfile(full_path):
        file_to_open = open(full_path+".html", "rb").read()
        mime_type = "text/html"
      else:
        mime_type, _ = mimetypes.guess_type(full_path)
        file_to_open = open(full_path, "rb").read()
    except:
      file_to_open = "File not found".encode("utf-8")
      code = 404
    self.reply(file_to_open, code, mime_type)

def run_http():
  httpd = HTTPServer(('0.0.0.0',8000),Serv)
  print("Serving https @any:8000")
  httpd.serve_forever()

run_http() #Thread(target=run_http, daemon=True).start()
