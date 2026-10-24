from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path
from app.plc_client import PLCClient

app = FastAPI(title="IIoT PLC Inspector")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "templates" / "index.html"

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return TEMPLATE_PATH.read_text(encoding="utf-8")

@app.get("/read")
def read_tag(ip: str, db: int, offset: int, dtype: str, bit: int = 0):
    try:
        plc = PLCClient(ip)
        if not plc.connect():
            return {"status": "Connection Failed", "value": "N/A"}
        
        val = None
        if dtype == "int":
            val = plc.read_int(db_number=db, start=offset)
        elif dtype == "bool":
            try:
                raw_val = plc.read_bool(db_number=db, start=offset, bit_index=bit)
            except TypeError:
                raw_val = plc.read_bool(db_number=db, start=offset)
            val = "TRUE" if raw_val else "FALSE"
        elif dtype == "real":
            val = plc.read_float(db_number=db, start=offset)
        else:
            val = "Unknown Type"
        
        plc.disconnect()
        return {"status": "Connected & Success", "value": str(val)}
    except Exception as e:
        return {"status": f"Error: {str(e)}", "value": "Error"}

@app.get("/write")
def write_tag(ip: str, db: int, offset: int, dtype: str, value: str, bit: int = 0):
    try:
        plc = PLCClient(ip)
        if not plc.connect():
            return {"status": "Connection Failed", "value": "N/A"}
        
        if dtype == "int":
            plc.write_int(db_number=db, start=offset, value=int(value))
        elif dtype == "bool":
            bool_val = value.lower() in ("true", "1", "yes", "on")
            plc.write_bool(db_number=db, start=offset, bit_index=bit, value=bool_val)
        elif dtype == "real":
            plc.write_float(db_number=db, start=offset, value=float(value))
        else:
            return {"status": "Invalid Type", "value": "Error"}
        
        plc.disconnect()
        return {"status": "Write Success", "value": value}
    except Exception as e:
        return {"status": f"Error: {str(e)}", "value": "Error"}