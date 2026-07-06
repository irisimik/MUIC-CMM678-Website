
import os
from PIL import Image, ImageOps
import io, time, uuid

MAX_OUTPUT_MB = 5
MAX_OUTPUT_BYTES = MAX_OUTPUT_MB * 1024 * 1024

def procandsave(raw: bytes, MAX_DIM = 4096, UPLOAD_DIR="./public/secrethug/giftimg/") -> str:
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

      img.save(output,format="JPEG",quality=quality,optimize=False,progressive=True)

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