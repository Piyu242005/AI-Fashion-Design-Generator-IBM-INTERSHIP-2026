"""Vercel serverless endpoint for IDM-VTON virtual try-on."""
from __future__ import annotations
import base64, json, logging, os, tempfile, time, uuid
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)
SPACE_URL = os.getenv("HF_SPACE_URL", "https://yisol-idm-vton.hf.space").rstrip("/")
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
MAX_BYTES = 10 * 1024 * 1024
CONNECT_TIMEOUT, QUEUE_TIMEOUT = 20, 95
CORS_HEADERS = {"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"POST, OPTIONS","Access-Control-Allow-Headers":"Content-Type"}

def _json_error(code, message): return {"success":False,"error":{"code":code,"message":message}}

def _headers(content_type=None):
    h={"User-Agent":"AI-Fashion-Studio/1.0","Accept":"application/json"}
    if HF_TOKEN: h["Authorization"]=f"Bearer {HF_TOKEN}"
    if content_type: h["Content-Type"]=content_type
    return h

def _http(req, timeout):
    try: return urlopen(req, timeout=timeout)
    except HTTPError as e: raise RuntimeError(f"HTTP {e.code}: {e.read(1200).decode(errors='replace')}") from e
    except URLError as e: raise RuntimeError(f"Network error: {e.reason}") from e

def _parse_multipart(content_type, raw):
    from multipart import MultipartParser
    boundary=""
    for p in content_type.split(";"):
        p=p.strip()
        if p.startswith("boundary="): boundary=p[9:].strip().strip('"'); break
    if not boundary: raise ValueError("Missing multipart boundary")
    fields={}
    def on_field(field):
        name=field.field_name.decode() if isinstance(field.field_name,bytes) else str(field.field_name)
        value=field.value
        fields[name]=value.decode("utf-8",errors="replace") if isinstance(value,bytes) else str(value)
    def on_file(field):
        name=field.field_name.decode() if isinstance(field.field_name,bytes) else str(field.field_name)
        fields[name]=(field.file_object.read(), field.headers or {})
    # python-multipart's current API takes callbacks as the third positional argument.
    parser=MultipartParser(boundary.encode(), 1 << 24, {"on_field":on_field,"on_file":on_file})
    parser.write(raw); parser.finalize()
    person,garment=fields.get("person"),fields.get("garment")
    if not isinstance(person,tuple) or not isinstance(garment,tuple): raise ValueError("Both person and garment image files are required")
    def ctype(headers):
        for k in (b"Content-Type","Content-Type"):
            if k in headers:
                v=headers[k]; return v.decode() if isinstance(v,bytes) else str(v)
        return ""
    return person[0],garment[0],str(fields.get("garment_description","")),ctype(person[1]),ctype(garment[1])

def _ext(ct):
    ct=(ct or "").lower()
    return "png" if "png" in ct else "webp" if "webp" in ct else "jpg"

def _upload(person_path, garment_path):
    boundary=f"----AIFashionStudio{uuid.uuid4().hex}"; chunks=[]
    for path in (person_path,garment_path):
        data=Path(path).read_bytes(); filename=Path(path).name
        chunks += [f"--{boundary}\r\n".encode(),f'Content-Disposition: form-data; name="files"; filename="{filename}"\r\n'.encode(),b"Content-Type: application/octet-stream\r\n\r\n",data,b"\r\n"]
    chunks.append(f"--{boundary}--\r\n".encode())
    req=Request(f"{SPACE_URL}/gradio_api/upload",data=b"".join(chunks),headers=_headers(f"multipart/form-data; boundary={boundary}"),method="POST")
    with _http(req,CONNECT_TIMEOUT) as r: payload=json.loads(r.read().decode())
    if not isinstance(payload,list) or len(payload)<2: raise RuntimeError(f"Unexpected upload response: {payload!r}")
    return str(payload[0]),str(payload[1])

def _submit(person_file,garment_file,description):
    data=[{"background":person_file,"layers":[],"composite":None},garment_file,description[:200] or "fashion garment",True,True,30,42]
    req=Request(f"{SPACE_URL}/gradio_api/call/tryon",data=json.dumps({"data":data}).encode(),headers=_headers("application/json"),method="POST")
    with _http(req,CONNECT_TIMEOUT) as r: payload=json.loads(r.read().decode())
    event_id=payload.get("event_id") if isinstance(payload,dict) else None
    if not event_id: raise RuntimeError(f"No event_id returned by IDM-VTON: {payload!r}")
    return event_id

def _wait(event_id):
    req=Request(f"{SPACE_URL}/gradio_api/call/tryon/{event_id}",headers={**_headers(),"Accept":"text/event-stream"},method="GET")
    deadline=time.monotonic()+QUEUE_TIMEOUT
    with _http(req,QUEUE_TIMEOUT) as r:
        buffer=""
        while time.monotonic()<deadline:
            chunk=r.read(4096)
            if not chunk: break
            buffer+=chunk.decode(errors="replace")
            while "\n\n" in buffer:
                block,buffer=buffer.split("\n\n",1); event=data_text=None
                for line in block.splitlines():
                    if line.startswith("event:"): event=line[6:].strip()
                    elif line.startswith("data:"): data_text=line[5:].strip()
                if not data_text: continue
                try: data=json.loads(data_text)
                except json.JSONDecodeError: data=data_text
                if event=="error": raise RuntimeError(str(data))
                if event=="complete": return data
    raise TimeoutError("IDM-VTON generation timed out while waiting for the GPU queue.")

def _download(result):
    value=result[0] if isinstance(result,list) and result else result
    if isinstance(value,dict): value=value.get("path") or value.get("url") or value.get("image") or value.get("data")
    if not isinstance(value,str): raise RuntimeError(f"Unexpected IDM-VTON output: {value!r}")
    if value.startswith("data:image/"): return base64.b64decode(value.split(",",1)[1])
    url=value if value.startswith("http") else urljoin(f"{SPACE_URL}/",value.lstrip("/"))
    with _http(Request(url,headers=_headers(),method="GET"),CONNECT_TIMEOUT) as r: return r.read()

def _run(person,garment,pe,ge,description):
    with tempfile.TemporaryDirectory() as tmp:
        pp=str(Path(tmp)/f"person.{pe}"); gp=str(Path(tmp)/f"garment.{ge}"); Path(pp).write_bytes(person); Path(gp).write_bytes(garment)
        try:
            pf,gf=_upload(pp,gp); event=_submit(pf,gf,description); result=_wait(event); image=_download(result)
            if not image: raise RuntimeError("IDM-VTON returned an empty image")
            mime="image/jpeg" if image[:2]==b"\xff\xd8" else "image/png"
            return {"success":True,"image":f"data:{mime};base64,{base64.b64encode(image).decode()}","provider":"idm-vton"}
        except TimeoutError as e: return _json_error("TIMEOUT",str(e))
        except Exception as e:
            msg=str(e); low=msg.lower(); logger.exception("IDM-VTON request failed")
            if "401" in low or "403" in low: return _json_error("AUTH_ERROR","Hugging Face rejected the request. Check HF_TOKEN in Vercel.")
            if "429" in low or "quota" in low or "exceeded" in low: return _json_error("QUOTA_EXCEEDED","Hugging Face/ZeroGPU quota is currently exhausted. Please retry later.")
            if "503" in low or "sleep" in low or "loading" in low or "unavailable" in low: return _json_error("SPACE_LOADING","IDM-VTON is waking up. Please wait and retry.")
            return _json_error("TRYON_FAILED",f"IDM-VTON request failed: {msg[:300]}")

class handler(BaseHTTPRequestHandler):
    def _send(self,status,data):
        body=json.dumps(data).encode(); self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(body)))
        for k,v in CORS_HEADERS.items(): self.send_header(k,v)
        self.end_headers(); self.wfile.write(body)
    def do_OPTIONS(self):
        self.send_response(204)
        for k,v in CORS_HEADERS.items(): self.send_header(k,v)
        self.end_headers()
    def do_POST(self):
        try:
            length=int(self.headers.get("Content-Length","0"))
            if length<=0 or length>MAX_BYTES*2+1024*1024: self._send(413,_json_error("FILE_TOO_LARGE","The uploaded images are too large.")); return
            raw=self.rfile.read(length); person,garment,desc,pt,gt=_parse_multipart(self.headers.get("Content-Type",""),raw)
            if len(person)>MAX_BYTES or len(garment)>MAX_BYTES: self._send(413,_json_error("FILE_TOO_LARGE","Each image must be under 10 MB.")); return
            result=_run(person,garment,_ext(pt),_ext(gt),desc)
            if result.get("success"): self._send(200,result); return
            code=result.get("error",{}).get("code","TRYON_FAILED"); status={"AUTH_ERROR":401,"QUOTA_EXCEEDED":429,"SPACE_LOADING":503,"TIMEOUT":504}.get(code,500); self._send(status,result)
        except Exception as e:
            logger.exception("Try-on handler error"); self._send(400,_json_error("BAD_REQUEST",f"Could not process try-on request: {str(e)[:300]}"))
