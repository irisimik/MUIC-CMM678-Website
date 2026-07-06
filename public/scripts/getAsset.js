async function get(path, allowcache = true) {
  let url = new URL(path, window.location.origin);
  if (!allowcache) {url.searchParams.set("t", Date.now());}
  const req = await fetch(url.toString(), {
    cache: allowcache ? "default" : "no-store",
    method: "GET"
  });
  if (!req.ok) {return null;}
  return req;
}

async function getJSON(path, allowcache=false) {
  const req = await get(path, allowcache);
  if (req == null) {return null;}
  return await req.json();
}

async function post(path, payload) { // promise to always return a JSON or NULL
  const req = await fetch(path, {cache: "no-store", method: "POST", body: JSON.stringify(payload)}); 
  if (!req.ok) {
    return null;
  }
  const js = await req.json();
  return js;
} 
