import mimetypes
import aiohttp
import time, secrets, json
import os

from aiohttp import web
from pathlib import Path

import uuid
from PIL import Image
from PIL import ImageOps
import asyncio
import io
import time

import sqlite3

UPLOAD_DIR = "public/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_OUTPUT_MB = 5
MAX_OUTPUT_BYTES = MAX_OUTPUT_MB * 1024 * 1024

GOOGLE_CLIENT_ID = "129888425055-3pjo67u82p3q25oe7biebfitfmajjplh.apps.googleusercontent.com"
ROOT = Path(__file__).parent / "public"
DB_PATH = Path("datastore/main.db")
JSONPATH = "jsonsdata/"
#UTILS
def get_db():
  conn = sqlite3.connect(
    DB_PATH,
    timeout=30,
    isolation_level=None,
    check_same_thread=False
  )
  conn.row_factory = sqlite3.Row
  return conn

def get_cookie(request):
  try:
    cookie_header_value = request.headers.get("Cookie", "")
    return dict(i.split('=', 1) for i in cookie_header_value.split('; '))
  except:
    return {}

async def get_json(request):
  try:
    return await request.json()
  except Exception:
    raise web.HTTPBadRequest(text="Invalid JSON")

#Logger
@web.middleware
async def request_logger(request, handler):
  try:
    response = await handler(request)
    status = response.status
    return response
  except web.HTTPException as exc:
    status = exc.status
    raise
  finally:
    ip = request.headers.get(
      "CF-Connecting-IP",
      request.remote or "-"
    )
    ua = request.headers.get("User-Agent", "-")
    country = request.headers.get("CF-IPCountry", "--")
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    method = request.method
    path = request.path
    CLR = "\033[31m" if status > 299 else "\033[32m"
    if not path.startswith("/ADMIN/"):  
      print(
        f"[\033[36m{ts}\033[0m]\n"
        f"- {ip} {country}\n"
        f"- {method}\n"
        f"  {path}\n"
        f"  \"{ua}\"\n"
        f"> CODE : {CLR}{status}\033[0m <\n"
      )

#GET Handler
async def doGET(request):
  path = request.path
  if path == "/":
    path = "/index.html"
  elif path == "/favicon.ico":
    path = "/logo.png"

  try:
    safe_path = (ROOT / path.lstrip("/")).resolve()
  except Exception:
    raise web.HTTPForbidden()

  if not str(safe_path).startswith(str(ROOT.resolve())):
    raise web.HTTPForbidden()

  if safe_path.is_file():
    return web.FileResponse(safe_path)

  html_fallback = str(safe_path) + ".html"
  if os.path.isfile(html_fallback):
    return web.FileResponse(html_fallback)

  raise web.HTTPNotFound(text="File not found")

#POST Method
async def login(request):
  data = await get_json(request)
  id_token_raw = data.get("idToken")

  if not id_token_raw:
    raise web.HTTPBadRequest(text="Missing ID token")

  async with aiohttp.ClientSession() as session:
    async with session.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": id_token_raw}) as resp:
      payload = await resp.json()

    if payload.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
      raise web.HTTPUnauthorized(text="Wrong issuer")

  email = payload.get("email")
  if payload.get("aud") != GOOGLE_CLIENT_ID:
    raise web.HTTPUnauthorized(text="Wrong audience")

  if payload.get("email_verified") != "true":
    raise web.HTTPUnauthorized(text="Email not verified")
  
  if not email or not email.endswith("@student.mahidol.edu"):
    return web.json_response({"status": "Invalid email"})

  conn = get_db()
  username = email.split("@")[0]
  now = time.time()
  print("Login attempt from", email)
  try:
    row = conn.execute("""
      SELECT sessionId, expiration, studentid
        FROM users
        WHERE email=?
    """, (username,)).fetchone()
  
    if row is None:
      studentid = None
      expiration = 0
      sessionId = secrets.token_urlsafe(32)
    else:
      sessionId = row["sessionId"]
      expiration = row["expiration"] or 0
      studentid = row["studentid"]

    # regenerate session if missing or expired
    if not sessionId or now > expiration:
      sessionId = secrets.token_urlsafe(32)
      expiration = now + 60 * 60 * 24

    for _ in range(20):
      conflict = conn.execute("""
      SELECT 1 FROM users
      WHERE sessionId=? AND email!=?
      """, (sessionId, username)).fetchone()
      if not conflict:
        break
      sessionId = secrets.token_urlsafe(32)
    else:
      raise web.HTTPInternalServerError(text="Session ID generation failure")

    conn.execute("BEGIN IMMEDIATE")
    conn.execute("""
      INSERT INTO users (email, sessionId, expiration, name)
      VALUES (?, ?, ?, ?)
      ON CONFLICT(email) DO UPDATE SET
        sessionId=excluded.sessionId,
        expiration=excluded.expiration,
        name=excluded.name
      """, (username, sessionId, expiration, payload.get("name")))
    conn.commit()
    return web.json_response({
      "status": "success",
      "email": email,
      "sessionId": sessionId,
      "studentid": studentid,
    })
  except sqlite3.OperationalError as e:
    print(e)
    conn.rollback()
    if "locked" in str(e).lower():
      raise web.HTTPServiceUnavailable(text="Database busy, retry")
    raise
  finally:
    conn.close()

async def get_stampdata(request):
  return web.FileResponse(JSONPATH+"stampdata.json")
async def get_boarddata(request):
  return web.FileResponse(JSONPATH+"boarddata.json")
async def get_eventsdata(request):
  return web.FileResponse(JSONPATH+"eventsdata.json")

async def idbind(request):
  data = await get_json(request)
  sessionId = data.get("sessionId")
  studentId = data.get("studentId")
  if sessionId is None or studentId is None:
    raise web.HTTPBadRequest(text="Invalid request")
  conn = get_db()
  try:
    t = conn.execute(
      "SELECT expiration FROM users WHERE sessionId=?",
      (sessionId,)
    ).fetchone()
    if t is None:
      raise web.HTTPBadRequest(text="Session ID is invalid")
    t = t[0]

    if time.time() >= t:
      return web.json_response({
        {"success" : False}
      })
    
    conn.execute("""
      INSERT INTO users (sessionId, studentid)
      VALUES (?, ?)
      ON CONFLICT(sessionId) DO UPDATE SET
        studentid = excluded.studentid
    """, (sessionId, studentId))
    conn.commit()
    return web.json_response({
      "success" : True
    })
  except sqlite3.OperationalError as e:
    conn.rollback()
    if "locked" in str(e).lower():
      raise web.HTTPServiceUnavailable(text="Database busy, retry")
    raise
  finally:
    conn.close()
  
async def stampcheck(request):
  data = await get_json(request)
  sessionId = data.get("sessionId")
  if sessionId is None:
    raise web.HTTPBadRequest(text="Invalid request")
  conn = get_db()
  try:
    queried = conn.execute(
      "SELECT expiration, stamps FROM users WHERE sessionId=?",
      (sessionId,)
    ).fetchone()
    if queried is None:
      return web.json_response({"success": False, "reason": "Expired token"})
    
    t = queried[0]
    encstamp = queried[1] or ""

    if time.time() > t:
      return web.json_response({"success": False, "reason": "Expired token"})
    keyv = json.loads(open(JSONPATH+"stampmapping.json","r").read())
    output = {
      "success": True,
      "stamps": ["default"] + [keyv.get(i, "") for i in encstamp.split(",")]
    }
    return web.json_response(output)
  except sqlite3.OperationalError as e:
    conn.rollback()
    if "locked" in str(e).lower():
      raise web.HTTPServiceUnavailable(text="Database busy, retry")
    raise
  finally:
    conn.close()

async def rubnonggroup(request):
  data = await get_json(request)
  studentid = data.get("studentid")

  if studentid is None:
    return web.HTTPBadRequest(text="Invalid request")
  print(f"RECV POST rubnong {time.strftime("%Y-%m-%d %H:%M:%S")}")
  groupdata = json.loads(open(JSONPATH+"ticketmap.json", "r").read())
  group = json.loads(open(JSONPATH+"rubnongdata.json", "r").read()).get(str(studentid))
  if group is None:
    group = "default"
  return web.json_response(groupdata[group])


async def secrethug_get_junior(request):
  data = get_cookie(request)
  sessionId = data.get("session_id")
  
  if sessionId is None:
    return web.HTTPBadRequest(text="Invalid request")
  conn = get_db()
  print(f"RECV POST secrethug {time.strftime("%Y-%m-%d %H:%M:%S")}")
  try:
    queried = conn.execute(
      "SELECT expiration, studentid FROM users WHERE sessionId=?",
      (sessionId,)
    ).fetchone()
    if queried is None:
      return web.json_response({"success": False, "reason": "Expired token"})
    t = queried[0]
    studentid = queried[1]
    if time.time() > t:
      return web.json_response({"success": False, "reason": "Expired token"})
    if studentid is None:
      return web.json_response({"success": False, "reason": "No ID"})

    nong = json.loads(open(JSONPATH+"secrethug.json", "r").read()).get(str(studentid))
    if nong is None:
      nong = []
    return web.json_response(nong)
  except sqlite3.OperationalError as e:
    conn.rollback()
    if "locked" in str(e).lower():
      raise web.HTTPServiceUnavailable(text="Database busy, retry")
    raise
  finally:
    conn.close()


Image.MAX_IMAGE_PIXELS = 20_000_000

def getNonglistOf(studentid):
  return json.loads(open(JSONPATH + "secrethug.json", "r", encoding="utf-8").read()).get(str(int(studentid)))
  
deskmemory = json.loads(open(JSONPATH+"deskmemory.json", "r", encoding="utf-8").read())
"""{
  "A": [], 
  "B": [],
  "C": [],
  "D": [],
  "E": [],
  "F": [],
  "G": [],
  "H": [],
  "_COUNTER": {
    "A": 1,
    "B": 1,
    "C": 1,
    "D": 1,
    "E": 1,
    "F": 1,
    "G": 1,
    "H": 1
  }
}"""

def updateGiftFile():
  file = open(JSONPATH + "deskmemory.json", "w", encoding="utf-8")
  file.write(json.dumps(deskmemory))
  file.close()

def generateGiftId():
  lowestbucket = "A"
  lowest = 200000
  for bucket,count in deskmemory.items():
    if bucket == "_COUNTER":
      continue
    if len(count) < lowest:
      lowest = len(count)
      lowestbucket = bucket
  bucketident = deskmemory["_COUNTER"][lowestbucket]
  deskmemory["_COUNTER"][lowestbucket] += 1
  deskmemory[lowestbucket].append(bucketident)
  updateGiftFile()
  return f"{lowestbucket}{bucketident}"

def removeGift(giftid):
  bucket = giftid[0]
  ident = int(giftid[1:])
  try:
    deskmemory[bucket].remove(ident)
  except IndexError:
    pass
  updateGiftFile()


import copy
cmmlist = set(json.loads(open(JSONPATH+"cmm.json","r",encoding="utf-8").read()))

def auth(custemail, custid):
  conn = get_db()
  row = conn.execute("SELECT 1 FROM users WHERE email=? AND studentid=?", (custemail.split("@")[0], custid)).fetchone()
  conn.close()
  return row

async def uploadgiftimg(request):
  # verification
  route_name = request.match_info.route.name
  data = get_cookie(request)
  #data = await get_json(request)
  sessionId = data.get("session_id")
  if route_name == "normal":
    sessionId = None
  print(sessionId, "req")

  recipientid = None
  raw = None
  content_type = None
  note = None

  preferedbucket = None
  senderid = None

  custemail = None
  custid = None

  reader = await request.multipart()

  async for field in reader:
    if field.name == "targetId":
      recipientid = (await field.text()).strip()
    elif field.name == "giftImage":
      content_type = field.headers.get("Content-Type")
      raw = await field.read()
    elif field.name == "note":
      note = await field.text()
    elif field.name == "prefbucket" and adminbypass:
      preferedbucket = await field.text()
    elif field.name == "gifterid" and adminbypass:
      senderid = await field.text()
      studentId = int(senderid)
    elif field.name == "email":
      custemail = (await field.text()).strip()
    elif field.name == "id":
      custid = (await field.text()).strip()
  studentId = None
  if sessionId is None:
    if not auth(custemail, custid):
      return web.HTTPBadRequest(text="Invalid request")
    studentId = int(custid)
    
  if studentId == None:
    conn = get_db()
    try:
      studentId = conn.execute("SELECT studentid FROM users WHERE sessionId=?", (sessionId,)).fetchone()[0]
    except Exception as e:
      print("Error retriving stuid",e)
      raise web.HTTPClientError(text="No student ID")
    finally:
      conn.close()

  
  if studentId is None:
    return web.HTTPUnauthorized(text="Expired session")
  if studentId >= 6880000:
    return web.HTTPUnauthorized(text="Unauthorized student ID range")
  adminbypass = False
  if route_name == "elevated" and not studentId in cmmlist:
    return web.HTTPUnauthorized(text="ADMIN POST path unauthorized.")
  elif route_name == "elevated" and studentId in cmmlist:
    adminbypass = True
  
  nonglist = getNonglistOf(studentId) if not adminbypass else [] # list of dict
  if nonglist is None:
    return web.HTTPClientError(text="No Nonglist")

  


  if recipientid is None:
    return web.HTTPBadRequest(text="Missing targetId")
  
  conn = get_db()
  isallowed = False
  # check if the recipient id is allowed
  print("Prahud", studentId, "Nongrahud", recipientid)
  try:
    exist = conn.execute("SELECT 1 FROM gift WHERE recipient=? AND retrieved=0",(int(recipientid),)).fetchone() # check if duplicated
    nonglists = [int(i["id"]) for i in nonglist]
    print(nonglists, recipientid)
    if adminbypass or (int(recipientid) in nonglists): # check if you can target this recipient
      if not exist:
        isallowed = True
      else:
        return web.json_response({"duplicated": True})
    
  except sqlite3.OperationalError as e:
    conn.rollback()
    if "locked" in str(e).lower():
      raise web.HTTPServiceUnavailable(text="Database busy, retry")
    raise
  finally:
    conn.close()
  
  if not isallowed:
    print("USUALLY THIS WILL RAISE DISALLOW TARGET")
  # begin upload
  if raw is None:
    return web.Response(status=400, text="No image")
  
  if content_type is None or not content_type.startswith("image/"):
    return web.Response(status=400, text="Invalid content type")

  loop = asyncio.get_running_loop()

  try:
    filename = await loop.run_in_executor(
      None, process_image_and_save, raw
    )
  except ValueError as e:
    return web.Response(status=400, text=str(e))
  except Exception:
    return web.Response(status=500, text="Image processing failed")

  if preferedbucket and preferedbucket in deskmemory:
    giftid = deskmemory.get("_COUNTER").get(preferedbucket)
    deskmemory[preferedbucket].append(giftid)
    deskmemory["_COUNTER"][preferedbucket] += 1
    giftid = preferedbucket+str(giftid)
    updateGiftFile()
  else:
    giftid = generateGiftId()
  conn = get_db()
  try:
    conn.execute("""
      INSERT INTO gift (giftid, gifter, giftimg, recipient, note)
      VALUES (?, ?, ?, ?, ?)
    """, (giftid, int(studentId), filename, int(recipientid), note))
    conn.commit()
  except sqlite3.OperationalError as e:
    conn.rollback()
    if "locked" in str(e).lower():
      raise web.HTTPServiceUnavailable(text="Database busy, retry")
    raise
  finally:
    conn.close()
  return web.json_response({"giftid": giftid})

async def getgiftrecipientlist(request):
  data = get_cookie(request)
  sessionId = data.get("session_id")
  studentId = None
  if sessionId is None:
    js = await get_json(request)
    email = js.get("email")
    studentId = js.get("id")
    print(js, email, studentId, auth(email, studentId))
    if not email or not studentId or not auth(email, studentId):
      return web.HTTPBadRequest(text="Invalid request")
    studentId = int(studentId)
  if studentId is None:
    conn = get_db()
    try:
      studentId = conn.execute("SELECT studentid FROM users WHERE sessionId=?", (sessionId,)).fetchone()[0]
    except Exception as e:
      print("Error retriving stuid",e)
      raise web.HTTPClientError(text="No student ID")
    finally:
      conn.close()

  if studentId is None:
    return web.HTTPUnauthorized(text="Expired session")
  if studentId >= 6880000:
    return web.HTTPUnauthorized(text="Unauthorized student ID range")
  nonglist = getNonglistOf(studentId) # list of dict
  if nonglist is None:
    return web.HTTPClientError(text="No Nonglist")

  conn = get_db()

  try:
    result = conn.execute("SELECT recipient FROM gift WHERE gifter=? AND retrieved=0", (studentId,)).fetchall()
    gifted = [i[0] for i in result]
  except sqlite3.OperationalError as e:
    conn.rollback()
    if "locked" in str(e).lower():
      raise web.HTTPServiceUnavailable(text="Database busy, retry")
    raise
  finally:
    conn.close()
  return web.json_response({"nongdatas": nonglist, "gifted": gifted})

async def checkcredauth(request):
  js = await get_json(request)
  email = js.get('email')
  studentId = js.get('id')
  return web.json_response({"auth": auth(email, studentId) is not None})


def process_image_and_save(raw: bytes, MAX_DIM = 4096) -> str:
  try:
    Image.open(io.BytesIO(raw)).verify()
  except Exception as e:
    print(e)
    raise ValueError("Invalid image (verify)")
  
  try:
    img = Image.open(io.BytesIO(raw))
  except Exception as e:
    print(e)
    raise ValueError("Invalid image (open)")

  if img.format not in {"JPEG", "PNG", "WEBP"}:
    raise ValueError("Unsupported image format")

  img = ImageOps.exif_transpose(img)
  img = img.convert("RGB")

  img.thumbnail((MAX_DIM, MAX_DIM))

  output = io.BytesIO()
  st = time.time()
  if output.tell() <= MAX_OUTPUT_BYTES:
    img.save(output, format="JPEG")
    print("Saved in", time.time() - st)
  else:
    quality = 85
    output.seek(0)
    while quality > 30:
      output.seek(0)
      output.truncate(0)

      img.save(
        output,
        format="JPEG",
        quality=quality,
        optimize=False,  # avoid CPU DoS
        progressive=True
      )

      if output.tell() <= MAX_OUTPUT_BYTES:
        break
      quality -= 5
    print("Compressed in", time.time() - st)

  if output.tell() > MAX_OUTPUT_BYTES:
    raise ValueError("Could not compress below 5MB")

  filename = f"{uuid.uuid4().hex}.jpg"
  final_path = os.path.join(UPLOAD_DIR, filename)
  tmp_path = final_path + ".tmp"

  with open(tmp_path, "wb") as f:
    f.write(output.getvalue())

  os.replace(tmp_path, final_path)
  return filename

async def admingettableinfo(request):
  data = get_cookie(request)
  sessionId = data.get("session_id")
  
  if sessionId is None:
    return web.HTTPBadRequest(text="Invalid request")
  
  conn = get_db()
  studentId = None
  try:
    studentId = conn.execute("SELECT studentid FROM users WHERE sessionId=?", (sessionId,)).fetchone()
    #print(studentId)
    studentId = studentId[0]
  except Exception as e:
    print("Error retriving stuid",e)
    raise web.HTTPUnauthorized(text="No student ID")
  finally:
    conn.close()

  if studentId is None:
    return web.HTTPUnauthorized(text="Expired session")
  if studentId not in cmmlist:
    return web.HTTPForbidden(text="Not CMM member.")
  
  ready = copy.deepcopy(deskmemory)
  conn = get_db()
  try:
    ready["val"] = [list(i) for i in conn.execute("SELECT giftid, giftimg, gifter, recipient, note FROM gift WHERE retrieved=0").fetchall()]
  except Exception as e:
    print("Error retrieving gift value for admin")
    ready["val"] = []
  finally:
    conn.close()
  return web.json_response(ready)
  
async def redeemgift(request):
  cookie = get_cookie(request)
  sessionId = cookie.get("session_id")
  if request.match_info.route.name == "normalred":
    sessionId = None
  data = await get_json(request)
  giftid = data.get("giftid")
  
  
  studentId = None
  if sessionId is None:
    email = data.get("email")
    studentId = data.get("id")
    if not email or not studentId or not auth(email, studentId):
      return web.HTTPBadRequest(text="Invalid request")
    studentId = int(studentId)
  
  conn = get_db()
  try:
    if studentId is None:
      studentId = conn.execute("SELECT studentid FROM users WHERE sessionId=?", (sessionId,)).fetchone()
      if studentId is None:
        return web.HTTPUnauthorized(text="Expired session")
      studentId = studentId[0]
    authorized = False
    if studentId in cmmlist:
      authorized = True
    
    if not authorized:
      gifts = conn.execute("SELECT giftid FROM gift WHERE (gifter=? OR recipient=?) AND retrieved=0", (studentId,studentId)).fetchall()
      for gift in gifts:
        gift = gift[0]
        if gift == giftid:
          authorized = True
          break
    if not authorized:
      return web.HTTPUnauthorized(text="Unauthorized action request")
    conn.execute("UPDATE gift SET retrieved=1 WHERE giftid=?",(giftid,))
    try:
      removeGift(giftid)
    except Exception as e:
      print(f"Unable to remove {giftid} from desk, due to {e}")
    return web.json_response({"success":True})
  except Exception as e:
    print("Error retriving stuid",e)
    raise web.HTTPUnauthorized(text="No student ID")
  finally:
    conn.close()

async def checkgift(request):
  cookie = get_cookie(request)
  sessionId = cookie.get("session_id")
  studentId = None
  if sessionId is None:
    js = await get_json(request)
    email = js.get("email")
    studentId = js.get("id")
    if not email or not studentId or not auth(email, studentId):
      return web.HTTPBadRequest(text="Invalid request")
  conn = get_db()
  try:
    if not studentId:
      studentId = conn.execute("SELECT studentid FROM users WHERE sessionId=?", (sessionId,)).fetchone()
      if studentId is None:
        return web.HTTPUnauthorized(text="Expired session")
      studentId = studentId[0]
    gift = conn.execute("SELECT giftid, giftimg, note FROM gift WHERE recipient=? AND retrieved=0",(studentId,)).fetchone()
    if gift is None or gift[0] is None:
      return web.json_response({"success": False})
    return web.json_response({"success": True, "data": list(gift)})
  except Exception as e:
    print("Error retriving stuid",e)
    raise web.HTTPUnauthorized(text="No student ID")
  finally:
    conn.close()


async def needrelogin(request):
  data = get_cookie(request)
  sessionId = data.get("session_id")
  
  if sessionId is None:
    return web.json_response({"requirelogin": True})
  
  conn = get_db()
  try:
    t = conn.execute("SELECT expiration FROM users WHERE sessionId=?", (sessionId,)).fetchone()[0]
    if time.time() > t:
      raise
  except:
    return web.json_response({"requirelogin": True})
  finally:
    conn.close()

  return web.json_response({"requirelogin": False})

app = web.Application(middlewares=[request_logger], client_max_size=32 * 1024 * 1024)
app.router.add_get("/{path:.*}", doGET)
app.router.add_post("/login", login)
app.router.add_post("/idbind", idbind)
app.router.add_post("/stampcheck", stampcheck)
app.router.add_post("/getstampdata", get_stampdata)
app.router.add_post("/getboarddata", get_boarddata)
app.router.add_post("/eventsdata", get_eventsdata)
app.router.add_post("/rubnonggroup", rubnonggroup)
app.router.add_post("/secrethugSGETJ", secrethug_get_junior)
app.router.add_post("/getgiftrecipientlist", getgiftrecipientlist)
app.router.add_options("/sessioncheck", needrelogin)
app.router.add_post("/sessioncheck", needrelogin)
app.router.add_post("/checkgift", checkgift)
app.router.add_post("/redeemgift", redeemgift, name="normalred")
app.router.add_post("/sercretauth", checkcredauth)

app.router.add_post("/ADMIN/gettableinfo", admingettableinfo)
app.router.add_post("/ADMIN/deletegift", redeemgift, name="elevatedred")
app.router.add_post("/ADMIN/uploadgift", uploadgiftimg, name="elevated")


conn = get_db()
conn.execute("PRAGMA journal_mode=WAL;")
conn.execute("PRAGMA synchronous=NORMAL;")
conn.close()

web.run_app(app, host="0.0.0.0", port=8000)
