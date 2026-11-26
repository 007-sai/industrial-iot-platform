from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path
from app.plc_client import PLCClient
import os
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse
from app.auth import  (
    init_user_database,
    authenticate_user,
    get_user_by_username,
    change_password,
)
app = FastAPI(title="IIoT PLC Inspector")
SESSION_SECRET = os.getenv("SESSION_SECRET")

if not SESSION_SECRET:
    raise RuntimeError("SESSION_SECRET environment variable is required")

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="strict",
    https_only=False,
)

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str



@app.on_event("startup")
def startup():
    init_user_database()


@app.post("/login")
def login(data: LoginRequest, request: Request):
    user = authenticate_user(data.username, data.password)

    if user is None:
        return JSONResponse(
            status_code=401,
            content={"authenticated": False, "detail": "Invalid username or password"},
        )

    request.session.clear()
    request.session["username"] = user["username"]

    return {"authenticated": True}

@app.post("/change-password")
def change_user_password(
    data: ChangePasswordRequest,
    request: Request,
):
    user = get_current_user(request)

    if user is None:
        return JSONResponse(
            status_code=401,
            content={"detail": "Please log in first"},
        )

    try:
        changed = change_password(
            user["username"],
            data.current_password,
            data.new_password,
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    if not changed:
        return JSONResponse(
            status_code=400,
            content={"detail": "Current password is incorrect"},
        )

    request.session.clear()

    return {"changed": True, "detail": "Password changed successfully. Please log in again."}

def get_current_user(request: Request):
    username = request.session.get("username")

    if not username:
        return None

    return get_user_by_username(username)
LOGIN_TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "login.html"


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    user = get_current_user(request)

    if user:
        return RedirectResponse(url="/", status_code=303)

    return LOGIN_TEMPLATE_PATH.read_text(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "templates" / "index.html"

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    user = get_current_user(request)

    if not user:
        return RedirectResponse(url="/login", status_code=303)

    return TEMPLATE_PATH.read_text(encoding="utf-8")

@app.get("/read")
def read_tag(request: Request,ip: str, db: int, offset: int, dtype: str, bit: int = 0):
    user = get_current_user(request)

    if user is None:
        return JSONResponse(
            status_code=401,
            content={"detail": "Please log in first"},
        )
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

@app.post("/write")
def write_tag(request: Request,ip: str, db: int, offset: int, dtype: str, value: str, bit: int = 0):
    user = get_current_user(request)

    if user is None:
        return JSONResponse(
            status_code=401,
            content={"detail": "Please log in first"},
        )
    if user["role"] not in ("Operator", "Admin"):
        return JSONResponse(
            status_code=403,
            content={"detail": "You do not have permission to write to the PLC"},
        )
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