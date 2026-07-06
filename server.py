import mimetypes
import aiohttp
import time, secrets, json, uuid
import os

from aiohttp import web
from pathlib import Path
import aiosqlite

import time

import csv
from utils.img import procandsave

ROOT = Path(__file__).parent / "public"
JSONPATH = "jsonsdata/"
#UTILS

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
				f"	{path}\n"
				f"	\"{ua}\"\n"
				f"> CODE : {CLR}{status}\033[0m <\n"
			)

def file_response_with_mime(file_path):
	mime_type, _ = mimetypes.guess_type(str(file_path))
	print(mime_type)
	return web.FileResponse(
		file_path,
		headers={"Content-Type": mime_type or "application/octet-stream"}
	)

async def startup(app):
	app["db"] = await aiosqlite.connect("datastore/database.db")
	await app["db"].execute("PRAGMA journal_mode=WAL")

async def cleanup(app):
	await app["db"].close()

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
async def register(request):
	db = request.app["db"]
	"""
	data store schem
	{
		studentemail TEXT PRIMARY KEY,
		studentid INTEGER UNIQUE
	}
	"""
"""
async def get_stamps(request):
	db = request.app["db"]
	data = await get_json(request)

	device_id = data.get("device_id")
	# fetch from db
	data = await db.execute_fetchall("SELECT stamps FROM BDIL_stamp WHERE device_id=?", (device_id,))
	if not data:
		return web.HTTPError("No")
	result = ""
	if len(data) != 0:
		result = data[0][0]
	print(device_id)
	print("RET",result)
	return web.json_response({"result": result})"""

truepass = "cmm678serveradmin" # hardcoded lmao

async def update_board(request):
	data = await get_json(request)
	password = data.get("password")
	stuff = data.get("newjson")
	if truepass != password:
		return web.HTTPForbidden("incorrect passcode")
	if stuff == None:
		return web.HTTPNoContent()
	old = open("public/boarddata.json", "r").read()
	
	open("public/boarddataold.json", "w").write(old)
	open("public/boarddata.json", "w").write(stuff)
	
	return web.json_response({"result": "ok"})

async def update_board_password_check(request):
	data = await get_json(request)
	password = data.get("password")
	if not password or password != truepass:
		return web.json_response({"auth": False})
	return web.json_response({"auth": True})


def readfilesafe(fname):
	data = None
	with open(fname, "r", encoding="utf-8") as st:
		data = st.read()
	return data or "{}"

ngroupdata = json.loads(readfilesafe("jsonsdata/ngroupdata.json"))
userdata = json.loads(readfilesafe("jsonsdata/userdata.json"))
shpair = json.loads(readfilesafe("jsonsdata/secrethugpair.json"))

lastupdate = time.time()

async def reloadstaticjsons(request):
	global lastupdate
	if time.time() - lastupdate < 1:
		return web.HTTPTooManyRequests
	lastupdate = time.time()
	global ngroupdata
	global userdata
	global shpair
	ngroupdata = json.loads(readfilesafe("jsonsdata/ngroupdata.json"))
	userdata = json.loads(readfilesafe("jsonsdata/userdata.json"))
	shpair = json.loads(readfilesafe("jsonsdata/secrethugpair.json"))
	return web.json_response({"status"," done"})

async def checkncode(request):
	db = request.app["db"]
	data = await get_json(request)
	pstid = str(data.get("id")) # key
	pemail = data.get("email").lower() # 3
	# validate
	if userdata.get(pstid) == None:
		return web.json_response({"status":"REJ","reason": "INVSTID"})
	if userdata.get(pstid)[3].lower().strip() != pemail.lower().strip():
		return web.json_response({"status":"REJ","reason": "INVEMAIL"})
	# retrieve info
	nids = shpair.get(pstid)
	if nids == None:
		return web.json_response({"status":"FAILED", "reason":"NO-NCODE"})
	res = []
	gifted = []
	for nid in nids:
		raw = userdata.get(str(nid))
		full = raw[0]
		nick = raw[1]
		major = raw[2]
		insta = raw[5]
		res.append([str(nid),full, nick, major, insta])
		if await db.execute_fetchall("SELECT ID FROM giftinfo WHERE recpID=? AND claimed=0", (str(nid),)):
			gifted.append(int(nid))
	return web.json_response({"status": "OK", "data": res, "gifted": gifted})

async def rubnongcheckid(request):
	data = await get_json(request)
	stid = data.get("id")
	if stid == None:
		stid = ""
	else:
		stid = str(stid)
	return web.json_response({"group": ngroupdata.get(stid, "n")})

def auth(email, stid):
	return not (userdata.get(str(stid)) == None or userdata.get(str(stid))[3].lower().strip() != email.lower().strip())

async def authsecrethug(request):
	data = await get_json(request)
	stid = str(data.get("id")) # key
	email = data.get("email").lower() # 3
	#if userdata.get(stid) == None:
	#	return web.json_response({"status":"REJ","reason": "INVSTID"})
	#if userdata.get(stid)[3].lower().strip() != email.lower().strip():
	#	return web.json_response({"status":"REJ","reason": "INVEMAIL"})
	return web.json_response({"status": "AUTHOK" if auth(email, stid) else "REJ"})

buckets = json.loads(open(JSONPATH + "giftbucket.json", "r", encoding="utf-8").read())

def updateGiftFile():
	global buckets
	file = open(JSONPATH + "giftbucket.json", "w", encoding="utf-8")
	file.write(json.dumps(buckets))
	file.close()

def generateGiftId():
  lowestbucket = "A"
  lowest = 200000
  for bucket,count in buckets.items():
    if bucket == "COUNTER":
      continue
    if len(count) < lowest:
      lowest = len(count)
      lowestbucket = bucket
  bucketident = buckets["COUNTER"][lowestbucket]
  buckets["COUNTER"][lowestbucket] += 1
  buckets[lowestbucket].append(bucketident)
  updateGiftFile()
  return f"{lowestbucket}{bucketident}"


async def upload_img(request):
	db = request.app["db"]
	global buckets
	route_name = request.match_info.route.name
	adminbypass = (route_name == "ADMINUPLOAD")

	email = request.cookies.get("email")
	stid = request.cookies.get("id")

	if adminbypass:
		# authenticate
		if not auth(email, stid) or userdata.get(str(stid))[0] != "CMM":
			return web.Response(status=401)
	else:
		if not email or not stid:
			print("REJECTED DUE TO NO EMAIL OR ID")
			return web.Response(status=401)
		if not auth(email, stid):
			print("REJECTED DUE TO INVALID EMAIL OR ID")
			return web.Response(status=401)
	# authenticated

	reader = await request.multipart()

	recipientid = None
	content_type = None
	raw = None
	note = ""
	bucket = None

	async for field in reader:
		if field.name == "targetId":
			recipientid = (await field.text()).strip()
		elif field.name == "giftImage":
			content_type = field.headers.get("Content-Type")
			raw = await field.read()
		elif field.name == "note":
			note = await field.text()
		elif adminbypass and field.name == "prefbucket":
			bucket = await field.text()
		elif adminbypass and field.name == "ovid":
			stid = (await field.text()).strip()

	if not adminbypass:
		# check if user can send gift to this person
		pool = [str(i) for i in shpair.get(stid)]
		if str(recipientid) not in pool:
			print(pool, recipientid)
			print("REJECTECD DUE TO INVALID PAIR")
			return web.Response(status=401)
	
	# check if recipient has unclamied gift
	if await db.execute_fetchall("SELECT ID FROM giftinfo WHERE recpID=? AND claimed=0", (str(recipientid),)):
		return web.json_response({"duplicated": True})

	filename = procandsave(raw)
	if bucket:
		giftid = buckets.get("COUNTER").get(bucket)
		buckets[bucket].append(giftid)
		buckets["COUNTER"][bucket] += 1
		giftid = bucket+str(giftid)
		updateGiftFile()
	else:
		giftid = generateGiftId()
	await db.execute("""
		INSERT INTO giftinfo (ID, senderID, imgname, recpID, note)
		VALUES (?, ?, ?, ?, ?)
	""", (giftid, str(stid), filename, str(recipientid), note))
	await db.commit()
	return web.json_response({"giftid": giftid})

async def checkgift(request):
	db = request.app["db"]
	data = await get_json(request)
	stid = str(data.get("id")) # key
	email = data.get("email").lower() # 3
	if not auth(email, stid):
		return web.Response(status=401)
	dbres = await db.execute_fetchall("SELECT ID, imgname, note FROM giftinfo WHERE recpID=? AND claimed=0", (stid,))
	return web.json_response({"isok": dbres != [],"data": dbres})

def removeGift(giftid):
	global buckets
	bucket = giftid[0]
	ident = int(giftid[1:])
	try:
		buckets[bucket].remove(ident)
	except IndexError:
		pass
	updateGiftFile()

async def redeemgift(request):
	db = request.app["db"]
	data = await get_json(request)
	stid = str(data.get("id")) # key
	email = data.get("email").lower() # 3
	giftid = data.get("giftid")
	if not auth(email, stid):
		return web.Response(status=401)
	route_name = request.match_info.route.name
	adminbypass = (route_name == "ADMINEDELETE")
	if adminbypass:
		if userdata.get(str(stid))[0] != "CMM":
			return web.Response(status=401)
	cmd = "UPDATE giftinfo SET claimed=1 WHERE ID=? AND senderID=?"
	args = (giftid, stid)
	if not adminbypass:
		cmd = "UPDATE giftinfo SET claimed=1 WHERE ID=?"
		args = (giftid,)
	await db.execute(cmd, args)
	await db.commit()
	removeGift(giftid)
	return web.json_response({"status": "k"})
import copy
async def admingettableinfo(request):
	global buckets
	db = request.app["db"]
	data = await get_json(request)
	stid = str(data.get("id")) # key
	email = data.get("email").lower() # 3
	if not auth(email, stid) or userdata.get(str(stid))[0] != "CMM":
		return web.Response(status=401)
  
	ready = copy.deepcopy(buckets)
	res = await db.execute_fetchall("SELECT ID, imgname, senderID, recpID, note FROM giftinfo WHERE claimed=0")

	ready["val"] = [list(i) for i in res]

	return web.json_response(ready)


app = web.Application(middlewares=[request_logger], client_max_size=32 * 1024 * 1024)
app.on_startup.append(startup)
app.on_cleanup.append(cleanup)
app.router.add_get("/{path:.*}", doGET)
app.router.add_post("/api/update_board", update_board)
app.router.add_post("/api/update_board_psw_check", update_board_password_check)
app.router.add_post("/api/rubnong/checkidngroup", rubnongcheckid)
app.router.add_post("/api/reloadstaticjsons", reloadstaticjsons)
app.router.add_post("/api/secrethug/checkncode", checkncode)
app.router.add_post("/api/secrethug/auth", authsecrethug)
app.router.add_post("/api/secrethug/uploadgift", upload_img)
app.router.add_post("/api/secrethug/checkgift", checkgift)
app.router.add_post("/api/secrethug/redeemgift", redeemgift)

app.router.add_post("/ADMIN/gettableinfo", admingettableinfo)
app.router.add_post("/ADMIN/deletegift", redeemgift, name="ADMINEDELETE")
app.router.add_post("/ADMIN/uploadgift", upload_img, name="ADMINUPLOAD")

#app.router.add_post("/api/bodyinlove/get_stamps", get_stamps)

web.run_app(app, host="0.0.0.0", port=8000)
