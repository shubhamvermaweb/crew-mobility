import hashlib
import hmac
import os
import re
import sqlite3
from datetime import date, datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & RESPONSIVE FIXED HEADER + UNIFIED PILL BOTTOM NAV CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Crew Arrangement & Mobility | Operations Control",
    page_icon="🅰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #F4F7FA;
    color: #1F2937;
}

header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0px !important;
}
#MainMenu, footer {
    visibility: hidden;
}

.block-container {
    padding-top: 76px !important;
    padding-bottom: 88px !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 1280px;
}

/* 1. FIXED TOP HEADER */
.oc-fixed-topbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 64px;
    background: #FFFFFF;
    border-bottom: 1px solid #E5E7EB;
    padding: 0 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 99999;
    box-shadow: 0 1px 4px rgba(15, 23, 42, 0.05);
}
.oc-brand-left {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
}
.oc-brand-title {
    font-size: 0.98rem;
    font-weight: 700;
    color: #1F2937;
    margin: 0;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.oc-brand-sub {
    font-size: 0.67rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    color: #6B7280;
    margin-top: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.oc-brand-right {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
}

.oc-badge-sample {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #FEF9C3;
    border: 1px solid #FDE047;
    color: #92400E;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 999px;
    white-space: nowrap;
}
.oc-badge-uploaded {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #DCFCE7;
    border: 1px solid #86EFAC;
    color: #166534;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 999px;
    white-space: nowrap;
}
.oc-dot-green {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #15803D;
    display: inline-block;
}
.oc-avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: #E0E7FF;
    color: #1E40AF;
    font-weight: 700;
    font-size: 0.8rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

/* 2. UNIFIED PILL-STYLED FIXED BOTTOM NAVIGATION BAR */
.oc-fixed-bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 68px;
    background: #FFFFFF;
    border-top: 1px solid #E5E7EB;
    display: flex;
    flex-direction: row !important;
    justify-content: space-around;
    align-items: center;
    padding: 6px 8px;
    z-index: 99999;
    box-shadow: 0 -2px 10px rgba(15, 23, 42, 0.06);
    overflow-x: auto;
    scrollbar-width: none;
}
.oc-fixed-bottom-nav::-webkit-scrollbar {
    display: none;
}
.oc-nav-item {
    flex: 1 1 0;
    min-width: 58px;
    max-width: 170px;
    height: 54px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-decoration: none !important;
    color: #4B5563 !important;
    font-size: 0.72rem;
    font-weight: 500;
    padding: 4px 6px;
    border-radius: 12px;
    margin: 0 3px;
    transition: all 0.16s ease;
    white-space: nowrap;
}
.oc-nav-item:hover {
    background: #F3F4F6;
    color: #1F2937 !important;
}
.oc-nav-item.active {
    background: #E8F0FE !important;
    color: #1967D2 !important;
    font-weight: 700 !important;
}
.oc-nav-icon {
    font-size: 1.15rem;
    line-height: 1.15;
    margin-bottom: 2px;
}

/* 3. LOGIN PORTAL STYLING */
.login-hero {
    background: linear-gradient(135deg, #0F294A 0%, #1967D2 100%);
    border-radius: 18px 18px 0 0;
    padding: 28px 24px 22px 24px;
    text-align: center;
    color: #FFFFFF;
    box-shadow: 0 10px 25px rgba(25, 103, 210, 0.18);
}
.login-hero-icon {
    width: 54px;
    height: 54px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.14);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.75rem;
    margin-bottom: 10px;
    border: 1px solid rgba(255, 255, 255, 0.22);
}
.login-hero-title {
    font-size: 1.35rem;
    font-weight: 800;
    margin: 0;
    color: #FFFFFF;
}
.login-hero-sub {
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    color: #BFDBFE;
    margin-top: 4px;
    text-transform: uppercase;
}
.login-role-strip {
    display: flex;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 14px;
}
.login-role-chip {
    background: rgba(255, 255, 255, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.24);
    color: #F8FAFC;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 999px;
}

div[data-testid="stForm"] {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-top: none;
    border-radius: 0 0 18px 18px;
    padding: 24px 24px 22px 24px;
    box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08);
}

/* KPI Cards */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    height: 100%;
    margin-bottom: 10px;
}
.kpi-card-active {
    background: #FFFFFF;
    border: 2px solid #1976D2;
    border-radius: 12px;
    padding: 15px 17px;
    box-shadow: 0 2px 6px rgba(25, 118, 210, 0.08);
    height: 100%;
    margin-bottom: 10px;
}
.kpi-card-alert {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-radius: 12px;
    padding: 16px 18px;
    height: 100%;
    margin-bottom: 10px;
}
.kpi-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}
.kpi-label {
    font-size: 0.85rem;
    font-weight: 500;
    color: #4B5563;
}
.kpi-icon-box {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
}
.kpi-val {
    font-size: 1.95rem;
    font-weight: 700;
    color: #1F2937;
    line-height: 1.15;
    margin-bottom: 6px;
}
.kpi-val-blue {
    font-size: 1.95rem;
    font-weight: 700;
    color: #1D4ED8;
    line-height: 1.15;
    margin-bottom: 6px;
}
.kpi-sub {
    font-size: 0.78rem;
    color: #6B7280;
    display: flex;
    align-items: center;
    gap: 5px;
}
.pill-high {
    background: #FEE2E2;
    color: #DC2626;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
}

@media (max-width: 640px) {
    .block-container {
        padding-left: 0.65rem !important;
        padding-right: 0.65rem !important;
    }
    .oc-brand-title {
        font-size: 0.88rem;
    }
    .oc-brand-sub {
        font-size: 0.62rem;
    }
    .oc-badge-sample, .oc-badge-uploaded {
        font-size: 0.65rem;
        padding: 2px 7px;
    }
    .oc-nav-item {
        min-width: 52px;
        font-size: 0.65rem;
        padding: 4px 3px;
        margin: 0 1px;
    }
    .oc-nav-icon {
        font-size: 1.05rem;
    }
    .kpi-val, .kpi-val-blue {
        font-size: 1.6rem;
    }
}
</style>"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

DB_PATH = "operations_control.db"
DEFAULT_SAMPLE_DATE = "Default (Sample)"

# -----------------------------------------------------------------------------
# 2. CRYPTOGRAPHIC SALTED PASSWORD HASHING & ACTIVE SESSION TOKEN
# -----------------------------------------------------------------------------
def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return f"{salt.hex()}:{dk.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, hash_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
        return hmac.compare_digest(candidate, expected)
    except Exception:
        return False


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------------------------------------------------------
# 3. DATABASE INITIALIZATION
# -----------------------------------------------------------------------------
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Super Admin', 'Data Admin', 'User')),
            lobby TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active',
            session_token TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cols = [r[1] for r in cur.execute("PRAGMA table_info(users)").fetchall()]
    if "session_token" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN session_token TEXT")

    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_only_one_super_admin
        ON users(role) WHERE role = 'Super Admin'
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS loads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            op_date TEXT NOT NULL,
            data_source TEXT NOT NULL DEFAULT 'Sample data',
            sr_no TEXT,
            load_code TEXT NOT NULL,
            coal_load TEXT,
            priority TEXT NOT NULL DEFAULT 'Normal',
            current_dest TEXT,
            destination TEXT NOT NULL,
            path_avail TEXT,
            alp_lobby TEXT,
            alp_time TEXT,
            alp_id TEXT,
            lpg_id TEXT,
            alp_status TEXT NOT NULL,
            tm_lobby TEXT,
            tm_time TEXT,
            tm_id TEXT,
            tm_status TEXT NOT NULL,
            leaving_lobby_time TEXT,
            reached_dest_time TEXT,
            means TEXT,
            cto_alp_lpg TEXT,
            cto_tm TEXT,
            path_given_time TEXT,
            load_status TEXT NOT NULL,
            duty_hours TEXT,
            attention_required TEXT,
            nom_diff_min INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS detention_stages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            op_date TEXT NOT NULL,
            data_source TEXT NOT NULL DEFAULT 'Sample data',
            stage TEXT NOT NULL,
            valid_count INTEGER NOT NULL,
            excluded_count INTEGER NOT NULL,
            avg_minutes INTEGER NOT NULL
        )
    """)

    cur.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES ('active_op_date', ?)", (DEFAULT_SAMPLE_DATE,))

    cur.execute("SELECT COUNT(*) FROM loads WHERE data_source = 'Sample data'")
    if cur.fetchone()[0] == 0:
        sample_records = [
            (DEFAULT_SAMPLE_DATE, "Sample data", "1", "MSTB - ASN", "", "Normal", "ASN", "JAJ", "", "ASN", "13:15", "ALP-4101", "LPG-8101", "Provided", "ASN", "13:15", "TM-5101", "Provided", "12:55", "", "BCQ BY 03511", "", "", "", "ON RUN JMT", "06:24", None, 0),
            (DEFAULT_SAMPLE_DATE, "Sample data", "2", "FCON - OYR", "", "Normal", "OYR", "JAJ", "", "UDL", "13:15", "ALP-4102", "LPG-8102", "Provided", "UDL", "13:15", "TM-5102", "Provided", "", "", "", "", "", "", "ON RUN UDL", "06:24", None, 0),
            (DEFAULT_SAMPLE_DATE, "Sample data", "3", "FGDA - DGR", "", "HIGH", "DGR", "JAJ", "", "UDL", "12:00", "ALP-4103", "LPG-8103", "Provided", "UDL", "18:15", "TM-5103", "Provided", "", "", "", "", "", "", "ON RUN VDS", "07:39", None, 375),
            (DEFAULT_SAMPLE_DATE, "Sample data", "4", "FUT- PAN", "", "Normal", "PAN", "JAJ", "", "UDL", "13:15", "ALP-4104", "LPG-8104", "Provided", "UDL", "13:15", "TM-5104", "Provided", "", "", "", "", "", "", "ENROUTE", "06:24", None, 0),
            (DEFAULT_SAMPLE_DATE, "Sample data", "5", "IDBR - ASN", "", "Normal", "ASN", "JAJ", "", "ASN", "12:00", "ALP-4105", "LPG-8105", "Provided", "ASN", "12:15", "TM-5105", "Provided", "11:45", "", "VDS BY 18183", "", "", "", "AT ASN PLATFORM", "07:39", "Crew reached · CTO pending", 15),
            (DEFAULT_SAMPLE_DATE, "Sample data", "6", "KGG/TIL - ASN", "", "Normal", "ASN", "JAJ", "", "ASN", "15:30", "ALP-4106", "LPG-8106", "Provided", "ASN", "15:30", "TM-5106", "Provided", "15:25", "", "L-04 BY FOOT", "", "", "", "ON RUN", "04:09", None, 0),
            (DEFAULT_SAMPLE_DATE, "Sample data", "7", "BJU NOW CONFIRM AT 9/30", "", "Normal", "", "JAJ", "", "ASN", "09:30", "ALP-4107", "LPG-8107", "Provided", "ASN", "09:30", "TM-5107", "Provided", "09:15", "", "MUW BY 63509", "", "", "", "ON RUN", "10:09", None, 0),
            (DEFAULT_SAMPLE_DATE, "Sample data", "8", "SV/CHPG - DEMAND - 00/00- GIVEN 6/00", "", "Normal", "", "JAJ", "", "UDL", "06:00", "ALP-4108", "LPG-8108", "Provided", "UDL", "08:30", "TM-5108", "Provided", "", "", "", "", "", "", "MADE OVER", "13:39", None, 150),
            (DEFAULT_SAMPLE_DATE, "Sample data", "9", "BMKI DEMAND - 3/00- GIVEN 7/00", "", "Normal", "CRJ", "JAJ", "", "ASN", "07:00", "ALP-4109", "LPG-8109", "Provided", "ASN", "17:30", "TM-5109", "Provided", "07:15", "", "KPK BY 63514", "", "", "", "MADE OVER", "12:39", None, 630),
            (DEFAULT_SAMPLE_DATE, "Sample data", "10", "FUT", "", "Normal", "", "JAJ", "", "ASN", "15:00", "ALP-4110", "LPG-8110", "Provided", "ASN", "13:45", "TM-5110", "Provided", "14:30", "", "BCQ BY JEEP", "", "", "", "ON RUN JSME", "04:39", None, 75),
            (DEFAULT_SAMPLE_DATE, "Sample data", "11", "BSPB AT MMU", "", "Normal", "", "JAJ", "", "ASN", "16:30", "ALP-4111", "LPG-8111", "Provided", "ASN", "13:45", "TM-5111", "Provided", "", "", "", "", "", "", "AT MMU/CP", "03:09", "Crew reached · CTO pending", 165),
            (DEFAULT_SAMPLE_DATE, "Sample data", "12", "BSPB JMT", "", "HIGH", "", "JAJ", "", "ASN", "20:00", "ALP-4112", "LPG-8112", "Provided", "ASN", "17:30", "TM-5112", "Provided", "", "", "", "", "", "", "Crew, not moved", "23:39", "Load with crew but not moved", 150),
            (DEFAULT_SAMPLE_DATE, "Sample data", "13", "BSPB STN", "", "HIGH", "", "JAJ", "", "ASN", "19:00", "ALP-4113", "LPG-8113", "Provided", "ASN", "18:00", "TM-5113", "Provided", "", "", "", "", "", "", "Crew, not moved", "00:39", "Load with crew but not moved", 60),
            (DEFAULT_SAMPLE_DATE, "Sample data", "14", "JQSG - BW1 DEMAND 6/00", "", "HIGH", "", "PKA", "", "UDL", "", None, None, "Pending", "UDL", "", None, "Pending", "", "", "", "", "", "", "Awaiting crew", "00:00", "Both ALP/LPG & TM pending", None),
            (DEFAULT_SAMPLE_DATE, "Sample data", "15", "NTV - BW2. DEMAND 3/30", "", "Normal", "", "PKA", "", "UDL", "", None, None, "Pending", "UDL", "", None, "Pending", "", "", "", "", "", "", "Awaiting crew", "00:00", "Both ALP/LPG & TM pending", None),
            (DEFAULT_SAMPLE_DATE, "Sample data", "16", "BSCS/KLG - DSP 16 DEMAND 4/00", "", "Normal", "", "PKA", "", "UDL", "CALL CANCELLED BY AREA", None, None, "Pending", "UDL", "", None, "Pending", "", "", "", "", "", "", "Awaiting crew", "00:00", "Call cancelled by area", None),
            (DEFAULT_SAMPLE_DATE, "Sample data", "17", "CSZ", "", "Normal", "", "KAN", "", "ASN", "", None, None, "Pending", "ASN", "16:00", "TM-5117", "Provided", "", "", "", "", "", "", "ON RUN", "00:00", "ALP/LPG nomination pending", None),
            (DEFAULT_SAMPLE_DATE, "Sample data", "18", "SEB EX KAN - AT DGR DEMAND 3/00", "", "HIGH", "", "PKA", "", "UDL", "10:30", "ALP-4118", "LPG-8118", "Provided", "UDL", "10:30", "TM-5118", "Provided", "", "", "", "", "", "", "MADE OVER", "09:09", None, 0),
        ]
        cur.executemany("""
            INSERT INTO loads (
                op_date, data_source, sr_no, load_code, coal_load, priority, current_dest, destination, path_avail,
                alp_lobby, alp_time, alp_id, lpg_id, alp_status,
                tm_lobby, tm_time, tm_id, tm_status,
                leaving_lobby_time, reached_dest_time, means, cto_alp_lpg, cto_tm, path_given_time,
                load_status, duty_hours, attention_required, nom_diff_min
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_records)

    cur.execute("SELECT COUNT(*) FROM detention_stages WHERE data_source = 'Sample data'")
    if cur.fetchone()[0] == 0:
        stages = [
            (DEFAULT_SAMPLE_DATE, "Sample data", "Crew arrangement", 14, 4, 28),
            (DEFAULT_SAMPLE_DATE, "Sample data", "Nomination → departure", 28, 8, 16),
            (DEFAULT_SAMPLE_DATE, "Sample data", "Crew transportation", 28, 8, 44),
            (DEFAULT_SAMPLE_DATE, "Sample data", "Arrival → CTO", 12, 6, 14),
            (DEFAULT_SAMPLE_DATE, "Sample data", "CTO → path", 12, 6, 10),
            (DEFAULT_SAMPLE_DATE, "Sample data", "Path → movement", 12, 6, 23),
        ]
        cur.executemany(
            "INSERT INTO detention_stages (op_date, data_source, stage, valid_count, excluded_count, avg_minutes) VALUES (?, ?, ?, ?, ?, ?)",
            stages,
        )

    conn.commit()
    conn.close()


# -----------------------------------------------------------------------------
# 4. EXCEL PARSER FOR 'CREW ARRANGEMENT' WORKBOOKS & CSV FILES
# -----------------------------------------------------------------------------
def clean_str(val) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    s = str(val).strip()
    return "" if s.lower() in ("nan", "none", "nat") else s


def format_time_cell(val) -> str:
    s = clean_str(val)
    if not s or s == "0":
        return ""
    if " " in s and ":" in s:
        s = s.split(" ")[-1]
    if len(s) >= 5 and s[2] == ":":
        return s[:5]
    return s


def parse_minutes_diff(t1: str, t2: str):
    try:
        m1 = re.search(r"(\d{1,2}):(\d{2})", t1)
        m2 = re.search(r"(\d{1,2}):(\d{2})", t2)
        if not m1 or not m2:
            return None
        mins1 = int(m1.group(1)) * 60 + int(m1.group(2))
        mins2 = int(m2.group(1)) * 60 + int(m2.group(2))
        diff = abs(mins2 - mins1)
        return diff if diff <= 720 else (1440 - diff)
    except Exception:
        return None


def is_valid_crew_provision(time_str: str) -> bool:
    if not time_str:
        return False
    upper = time_str.upper()
    if "CANCEL" in upper or upper in ("0", "NA", "N/A", "PENDING", "-"):
        return False
    return bool(re.search(r"\d{1,2}[:/\.]\d{2}", time_str)) or "HRS" in upper


def normalize_load_status(raw_status: str, alp_ok: bool, tm_ok: bool) -> str:
    s = raw_status.upper()
    if "MADE OVER" in s or "OVER LOAD" in s:
        return "MADE OVER"
    if "ON RUN" in s:
        return "ON RUN"
    if "ENROUTE" in s or "EN ROUTE" in s:
        return "EN ROUTE"
    if "AT " in s or "PLATFORM" in s or "MMU" in s:
        return "At destination"
    if alp_ok and tm_ok:
        return "Crew, not moved"
    return "Awaiting crew"


def sheet_name_to_date_str(sheet_name: str, fallback_date: str) -> str:
    s = sheet_name.strip()
    if re.fullmatch(r"\d{8}", s):
        return f"{s[0:2]}-{s[2:4]}-{s[4:8]}"
    if re.fullmatch(r"\d{2}[-/\.]\d{2}[-/\.]\d{4}", s):
        return re.sub(r"[/\.]", "-", s)
    return fallback_date


def parse_crew_arrangement_excel(uploaded_file, sheet_name: str, target_op_date: str) -> pd.DataFrame:
    raw = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=None)
    if raw.empty:
        return pd.DataFrame()

    header_idx = 3
    for idx in range(min(10, len(raw))):
        row_vals = [clean_str(x).lower() for x in raw.iloc[idx].tolist()]
        if "load stabled" in row_vals:
            header_idx = idx
            break

    data_rows = raw.iloc[header_idx + 1 :].copy()
    parsed = []

    for _, row in data_rows.iterrows():
        load_code = clean_str(row.iloc[1]) if len(row) > 1 else ""
        if not load_code or load_code.lower() in ("total", "summary", "load stabled"):
            continue

        sr_no = clean_str(row.iloc[0]) if len(row) > 0 else ""
        coal_load = clean_str(row.iloc[2]) if len(row) > 2 else ""
        prio_raw = clean_str(row.iloc[3]) if len(row) > 3 else ""
        priority = "HIGH" if "HIGH" in prio_raw.upper() else ("Normal" if not prio_raw else prio_raw)

        current_dest = clean_str(row.iloc[4]) if len(row) > 4 else ""
        destination = (clean_str(row.iloc[5]) if len(row) > 5 else "").upper() or "N/A"
        path_avail = clean_str(row.iloc[6]) if len(row) > 6 else ""

        alp_lobby = (clean_str(row.iloc[7]) if len(row) > 7 else "").upper()
        alp_time_raw = clean_str(row.iloc[8]) if len(row) > 8 else ""
        alp_time = format_time_cell(alp_time_raw) if "CANCEL" not in alp_time_raw.upper() else alp_time_raw
        alp_id = clean_str(row.iloc[9]) if len(row) > 9 else ""
        lpg_id = clean_str(row.iloc[10]) if len(row) > 10 else ""

        tm_lobby = (clean_str(row.iloc[11]) if len(row) > 11 else "").upper()
        tm_time_raw = clean_str(row.iloc[12]) if len(row) > 12 else ""
        tm_time = format_time_cell(tm_time_raw) if "CANCEL" not in tm_time_raw.upper() else tm_time_raw
        tm_id = clean_str(row.iloc[13]) if len(row) > 13 else ""

        leaving_lobby = format_time_cell(row.iloc[15]) if len(row) > 15 else ""
        reached_dest = format_time_cell(row.iloc[16]) if len(row) > 16 else ""
        means = clean_str(row.iloc[17]) if len(row) > 17 else ""
        cto_alp_lpg = format_time_cell(row.iloc[22]) if len(row) > 22 else ""
        cto_tm = format_time_cell(row.iloc[23]) if len(row) > 23 else ""
        path_given = format_time_cell(row.iloc[24]) if len(row) > 24 else ""
        raw_status = clean_str(row.iloc[25]) if len(row) > 25 else ""
        duty_hours = format_time_cell(row.iloc[26]) if len(row) > 26 else ""

        alp_ok = is_valid_crew_provision(alp_time_raw)
        tm_ok = is_valid_crew_provision(tm_time_raw)
        alp_status = "Provided" if alp_ok else "Pending"
        tm_status = "Provided" if tm_ok else "Pending"
        load_status = normalize_load_status(raw_status, alp_ok, tm_ok)

        attention = None
        if "CANCEL" in alp_time_raw.upper() or "CANCEL" in tm_time_raw.upper():
            attention = "Call cancelled by area"
        elif not alp_ok and not tm_ok:
            attention = "Both ALP/LPG & TM pending"
        elif alp_ok and not tm_ok:
            attention = "TM nomination pending"
        elif tm_ok and not alp_ok:
            attention = "ALP/LPG nomination pending"
        elif load_status == "Crew, not moved":
            attention = "Load with crew but not moved"
        elif load_status == "At destination":
            attention = "Crew reached · CTO pending"

        nom_diff = parse_minutes_diff(alp_time, tm_time) if (alp_ok and tm_ok) else None

        parsed.append({
            "op_date": target_op_date,
            "sr_no": sr_no,
            "load_code": load_code,
            "coal_load": coal_load,
            "priority": priority,
            "current_dest": current_dest,
            "destination": destination,
            "path_avail": path_avail,
            "alp_lobby": alp_lobby,
            "alp_time": alp_time,
            "alp_id": alp_id,
            "lpg_id": lpg_id,
            "alp_status": alp_status,
            "tm_lobby": tm_lobby,
            "tm_time": tm_time,
            "tm_id": tm_id,
            "tm_status": tm_status,
            "leaving_lobby_time": leaving_lobby,
            "reached_dest_time": reached_dest,
            "means": means,
            "cto_alp_lpg": cto_alp_lpg,
            "cto_tm": cto_tm,
            "path_given_time": path_given,
            "load_status": load_status,
            "duty_hours": duty_hours,
            "attention_required": attention,
            "nom_diff_min": nom_diff,
        })

    return pd.DataFrame(parsed)


def save_uploaded_df_to_db(db_conn, parsed_df: pd.DataFrame, target_date: str):
    db_conn.execute("DELETE FROM loads WHERE op_date = ? AND data_source = 'Uploaded data'", (target_date,))
    for _, r in parsed_df.iterrows():
        db_conn.execute("""
            INSERT INTO loads (
                op_date, data_source, sr_no, load_code, coal_load, priority, current_dest, destination, path_avail,
                alp_lobby, alp_time, alp_id, lpg_id, alp_status,
                tm_lobby, tm_time, tm_id, tm_status,
                leaving_lobby_time, reached_dest_time, means, cto_alp_lpg, cto_tm, path_given_time,
                load_status, duty_hours, attention_required, nom_diff_min
            ) VALUES (?, 'Uploaded data', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            target_date,
            clean_str(r.get("sr_no")),
            clean_str(r.get("load_code")),
            clean_str(r.get("coal_load")),
            clean_str(r.get("priority", "Normal")) or "Normal",
            clean_str(r.get("current_dest")),
            clean_str(r.get("destination")) or "N/A",
            clean_str(r.get("path_avail")),
            clean_str(r.get("alp_lobby")),
            clean_str(r.get("alp_time")),
            clean_str(r.get("alp_id")),
            clean_str(r.get("lpg_id")),
            clean_str(r.get("alp_status", "Pending")),
            clean_str(r.get("tm_lobby")),
            clean_str(r.get("tm_time")),
            clean_str(r.get("tm_id")),
            clean_str(r.get("tm_status", "Pending")),
            clean_str(r.get("leaving_lobby_time")),
            clean_str(r.get("reached_dest_time")),
            clean_str(r.get("means")),
            clean_str(r.get("cto_alp_lpg")),
            clean_str(r.get("cto_tm")),
            clean_str(r.get("path_given_time")),
            clean_str(r.get("load_status", "Awaiting crew")),
            clean_str(r.get("duty_hours")),
            None if not clean_str(r.get("attention_required")) else clean_str(r.get("attention_required")),
            None if pd.isna(r.get("nom_diff_min")) else int(r.get("nom_diff_min")),
        ))
    rebuild_detention_stages_for_date(db_conn, target_date, "Uploaded data")


def rebuild_detention_stages_for_date(db_conn, target_date: str, source_type: str):
    df = pd.read_sql_query(
        "SELECT * FROM loads WHERE op_date = ? AND data_source = ?",
        db_conn,
        params=[target_date, source_type],
    )
    total = len(df)
    if total == 0:
        return

    both_valid = int(((df["alp_status"] == "Provided") & (df["tm_status"] == "Provided")).sum())
    excl_crew = total - both_valid
    moving_valid = int(df["load_status"].isin(["ON RUN", "MADE OVER", "EN ROUTE"]).sum())
    excl_move = total - moving_valid
    avg_nom = int(df["nom_diff_min"].dropna().mean()) if not df["nom_diff_min"].dropna().empty else 28

    db_conn.execute("DELETE FROM detention_stages WHERE op_date = ? AND data_source = ?", (target_date, source_type))
    stages = [
        (target_date, source_type, "Crew arrangement", both_valid, excl_crew, avg_nom),
        (target_date, source_type, "Nomination → departure", both_valid * 2, excl_crew * 2, 16),
        (target_date, source_type, "Crew transportation", both_valid * 2, excl_crew * 2, 44),
        (target_date, source_type, "Arrival → CTO", moving_valid, excl_move, 14),
        (target_date, source_type, "CTO → path", moving_valid, excl_move, 10),
        (target_date, source_type, "Path → movement", moving_valid, excl_move, 23),
    ]
    db_conn.executemany(
        "INSERT INTO detention_stages (op_date, data_source, stage, valid_count, excluded_count, avg_minutes) VALUES (?, ?, ?, ?, ?, ?)",
        stages,
    )


init_db()

# -----------------------------------------------------------------------------
# 5. SESSION RECOVERY & UNIFIED BOTTOM NAV QUERY ROUTING
# -----------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "active_nav" not in st.session_state:
    st.session_state.active_nav = "Home"

qp_tab = st.query_params.get("tab", None)
qp_sid = st.query_params.get("sid", None)

if qp_tab == "Logout":
    if st.session_state.user_info:
        c_out = get_conn()
        c_out.execute("UPDATE users SET session_token = NULL WHERE username = ?", (st.session_state.user_info["username"],))
        c_out.commit()
        c_out.close()
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.active_nav = "Home"
    st.query_params.clear()

if not st.session_state.authenticated and qp_sid:
    c_rec = get_conn()
    rec_row = c_rec.execute(
        "SELECT username, full_name, role, lobby, status FROM users WHERE session_token = ? AND status = 'Active'",
        (qp_sid,),
    ).fetchone()
    c_rec.close()
    if rec_row:
        st.session_state.authenticated = True
        st.session_state.user_info = {
            "username": rec_row["username"],
            "full_name": rec_row["full_name"],
            "role": rec_row["role"],
            "lobby": rec_row["lobby"],
            "sid": qp_sid,
        }

valid_tabs = ["Home", "Loads", "Crew", "Analysis", "Data Upload", "User Management", "Lobby Performance", "Password", "More"]
if qp_tab in valid_tabs and qp_tab != st.session_state.active_nav:
    st.session_state.active_nav = qp_tab


def render_auth_gate():
    conn_auth = get_conn()
    super_admin_exists = (
        conn_auth.execute("SELECT COUNT(*) FROM users WHERE role = 'Super Admin'").fetchone()[0] > 0
    )
    conn_auth.close()

    st.markdown(
        '<div class="oc-fixed-topbar">'
        '<div class="oc-brand-left">'
        '<div style="font-size:1.55rem;">🅰️</div>'
        '<div>'
        '<div class="oc-brand-title">Crew Arrangement & Mobility</div>'
        '<div class="oc-brand-sub">OPERATIONS CONTROL · RAILWAY DIVISION</div>'
        '</div>'
        '</div>'
        '<div class="oc-brand-right"><span class="oc-badge-sample">🔒 Sign In Required</span></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    _, center_col, _ = st.columns([1, 1.35, 1])
    with center_col:
        if not super_admin_exists:
            st.markdown(
                '<div class="login-hero">'
                '<div class="login-hero-icon">🛡️</div>'
                '<div class="login-hero-title">Initial System Setup</div>'
                '<div class="login-hero-sub">Register Single Super Admin Account</div>'
                '<div class="login-role-strip">'
                '<span class="login-role-chip">1 Super Admin Limit</span>'
                '<span class="login-role-chip">PBKDF2 Encrypted</span>'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            with st.form("init_super_admin_form"):
                sa_full_name = st.text_input("Super Admin Full Name", placeholder="Enter full name").strip()
                sa_username = st.text_input("Super Admin Username", placeholder="Choose a unique username").strip()
                sa_lobby = st.text_input("Headquarters / Division", value="ASN / HQ").strip()
                sa_password = st.text_input("Password (minimum 6 characters)", type="password", placeholder="••••••••")
                sa_confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••")

                if st.form_submit_button("✅ Register Super Admin & Launch", use_container_width=True, type="primary"):
                    if not sa_full_name or not sa_username or len(sa_password) < 6:
                        st.warning("Full name, username, and a password of at least 6 characters are required.")
                    elif sa_password != sa_confirm:
                        st.error("Passwords do not match.")
                    else:
                        try:
                            sid = os.urandom(16).hex()
                            db_conn = get_conn()
                            db_conn.execute(
                                "INSERT INTO users (username, full_name, role, lobby, password_hash, status, session_token, created_at) VALUES (?, ?, 'Super Admin', ?, ?, 'Active', ?, ?)",
                                (
                                    sa_username,
                                    sa_full_name,
                                    sa_lobby or "HQ",
                                    hash_password(sa_password),
                                    sid,
                                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                                ),
                            )
                            db_conn.commit()
                            db_conn.close()
                            st.session_state.authenticated = True
                            st.session_state.user_info = {
                                "username": sa_username,
                                "full_name": sa_full_name,
                                "role": "Super Admin",
                                "lobby": sa_lobby or "HQ",
                                "sid": sid,
                            }
                            st.query_params["tab"] = "Home"
                            st.query_params["sid"] = sid
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("A Super Admin account already exists.")
        else:
            st.markdown(
                '<div class="login-hero">'
                '<div class="login-hero-icon">🅰️</div>'
                '<div class="login-hero-title">Crew Arrangement & Mobility</div>'
                '<div class="login-hero-sub">Operations Control Portal</div>'
                '<div class="login-role-strip">'
                '<span class="login-role-chip">🛡️ Super Admin</span>'
                '<span class="login-role-chip">📤 Data Admin</span>'
                '<span class="login-role-chip">👤 Operator User</span>'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            with st.form("secure_login_form"):
                username_in = st.text_input("Username", placeholder="Enter your assigned username").strip()
                password_in = st.text_input("Password", type="password", placeholder="Enter your password")

                if st.form_submit_button("🔐 Sign In to Operations Control", use_container_width=True, type="primary"):
                    if not username_in or not password_in:
                        st.warning("Please enter both Username and Password.")
                    else:
                        db_conn = get_conn()
                        row = db_conn.execute(
                            "SELECT username, full_name, role, lobby, password_hash, status FROM users WHERE LOWER(username) = LOWER(?)",
                            (username_in,),
                        ).fetchone()

                        if row is None or not verify_password(password_in, row["password_hash"]):
                            db_conn.close()
                            st.error("Invalid Username or Password.")
                        elif row["status"] != "Active":
                            db_conn.close()
                            st.error("⛔ Your account is inactive. Contact the Super Admin.")
                        else:
                            sid = os.urandom(16).hex()
                            db_conn.execute("UPDATE users SET session_token = ? WHERE username = ?", (sid, row["username"]))
                            db_conn.commit()
                            db_conn.close()

                            st.session_state.authenticated = True
                            st.session_state.user_info = {
                                "username": row["username"],
                                "full_name": row["full_name"],
                                "role": row["role"],
                                "lobby": row["lobby"],
                                "sid": sid,
                            }
                            st.session_state.active_nav = "Home"
                            st.query_params["tab"] = "Home"
                            st.query_params["sid"] = sid
                            st.rerun()


if not st.session_state.authenticated or st.session_state.user_info is None:
    render_auth_gate()
    st.stop()

# -----------------------------------------------------------------------------
# 6. AUTHENTICATED USER DASHBOARD
# -----------------------------------------------------------------------------
current_user = st.session_state.user_info
active_role = current_user["role"]
user_lobby = (current_user.get("lobby") or "ALL").upper()
user_sid = current_user.get("sid", "")
role_initials = {"Super Admin": "SA", "Data Admin": "DA", "User": "US"}[active_role]

conn = get_conn()

uploaded_dates = [
    r[0] for r in conn.execute("SELECT DISTINCT op_date FROM loads WHERE data_source = 'Uploaded data' ORDER BY id DESC").fetchall()
]
default_op_date = conn.execute("SELECT value FROM app_settings WHERE key='active_op_date'").fetchone()[0]

date_options = uploaded_dates + [DEFAULT_SAMPLE_DATE]
if default_op_date not in date_options:
    default_op_date = uploaded_dates[0] if uploaded_dates else DEFAULT_SAMPLE_DATE

temp_uploaded_cnt = conn.execute(
    "SELECT COUNT(*) FROM loads WHERE op_date = ? AND data_source = 'Uploaded data'",
    (default_op_date,),
).fetchone()[0]
preview_source = "Uploaded data" if (default_op_date != DEFAULT_SAMPLE_DATE and temp_uploaded_cnt > 0) else "Sample data"
badge_class = "oc-badge-uploaded" if preview_source == "Uploaded data" else "oc-badge-sample"
badge_label = f"Uploaded sheet ({default_op_date})" if preview_source == "Uploaded data" else "Default data"

# 1. FIXED TOP HEADER (SINGLE-LINE HTML SO MARKDOWN NEVER ESCAPES IT)
topbar_html = (
    f'<div class="oc-fixed-topbar">'
    f'<div class="oc-brand-left">'
    f'<div style="font-size:1.55rem; flex-shrink:0;">🅰️</div>'
    f'<div style="min-width:0;">'
    f'<div class="oc-brand-title">Crew Arrangement & Mobility</div>'
    f'<div class="oc-brand-sub">OPERATIONS CONTROL · {current_user["full_name"]} (@{current_user["username"]} · {active_role})</div>'
    f'</div>'
    f'</div>'
    f'<div class="oc-brand-right">'
    f'<span class="{badge_class}"><span class="oc-dot-green"></span> {badge_label}</span>'
    f'<div class="oc-avatar" title="{active_role}">{role_initials}</div>'
    f'</div>'
    f'</div>'
)
st.markdown(topbar_html, unsafe_allow_html=True)

# 2. UNIFIED PILL-STYLED FIXED BOTTOM NAVIGATION BAR (ZERO LEADING SPACES!)
active_tab = st.session_state.active_nav

bottom_nav_items = [
    ("Home", "🏠", "Home"),
    ("Loads", "📦", "Loads"),
    ("Crew", "👥", "Crew"),
    ("Analysis", "📈", "Analysis"),
]
if active_role in ("Super Admin", "Data Admin"):
    bottom_nav_items.append(("Data Upload", "📤", "Upload"))
if active_role == "Super Admin":
    bottom_nav_items.append(("User Management", "🛡️", "Users"))
bottom_nav_items.append(("More", "•••", "More"))

nav_links_parts = []
for tab_key, icon_char, short_label in bottom_nav_items:
    is_active = "active" if (
        active_tab == tab_key
        or (tab_key == "More" and active_tab in ("Lobby Performance", "Password"))
    ) else ""
    nav_links_parts.append(
        f'<a class="oc-nav-item {is_active}" href="?tab={tab_key}&sid={user_sid}" target="_self">'
        f'<span class="oc-nav-icon">{icon_char}</span>'
        f'<span>{short_label}</span>'
        f'</a>'
    )

bottom_nav_html = f'<div class="oc-fixed-bottom-nav">{"".join(nav_links_parts)}</div>'
st.markdown(bottom_nav_html, unsafe_allow_html=True)

# Filter Bar for Dashboard Views
if st.session_state.active_nav in ("Home", "Loads", "Crew", "Analysis", "Lobby Performance"):
    f_col1, f_col2 = st.columns([1.4, 1.2])
    with f_col1:
        selected_date = st.selectbox(
            "Date Sheet",
            date_options,
            index=date_options.index(default_op_date),
        )
        if selected_date != default_op_date and active_role in ("Super Admin", "Data Admin"):
            conn.execute("UPDATE app_settings SET value = ? WHERE key = 'active_op_date'", (selected_date,))
            conn.commit()
            st.rerun()

    uploaded_count_for_sel = conn.execute(
        "SELECT COUNT(*) FROM loads WHERE op_date = ? AND data_source = 'Uploaded data'",
        (selected_date,),
    ).fetchone()[0]

    if selected_date != DEFAULT_SAMPLE_DATE and uploaded_count_for_sel > 0:
        active_source = "Uploaded data"
        query_date = selected_date
    else:
        active_source = "Sample data"
        query_date = DEFAULT_SAMPLE_DATE

    with f_col2:
        lobby_rows_db = conn.execute(
            "SELECT DISTINCT alp_lobby FROM loads WHERE op_date = ? AND data_source = ? AND alp_lobby != ''",
            (query_date, active_source),
        ).fetchall()
        db_lobbies = sorted([r[0] for r in lobby_rows_db if r[0]])
        all_lobbies = ["All Lobbies"] + db_lobbies

        default_lobby_idx = 0
        if active_role == "User" and user_lobby in db_lobbies:
            default_lobby_idx = all_lobbies.index(user_lobby)

        selected_lobby = st.selectbox("Filter Lobby", all_lobbies, index=default_lobby_idx)
else:
    selected_date = default_op_date
    uploaded_count_for_sel = conn.execute(
        "SELECT COUNT(*) FROM loads WHERE op_date = ? AND data_source = 'Uploaded data'",
        (selected_date,),
    ).fetchone()[0]
    active_source = "Uploaded data" if (selected_date != DEFAULT_SAMPLE_DATE and uploaded_count_for_sel > 0) else "Sample data"
    query_date = selected_date if active_source == "Uploaded data" else DEFAULT_SAMPLE_DATE
    selected_lobby = "All Lobbies"

query = "SELECT * FROM loads WHERE op_date = ? AND data_source = ?"
params = [query_date, active_source]
if selected_lobby != "All Lobbies":
    query += " AND (alp_lobby = ? OR tm_lobby = ?)"
    params.extend([selected_lobby, selected_lobby])

df_loads = pd.read_sql_query(query, conn, params=params)
df_stages = pd.read_sql_query(
    "SELECT * FROM detention_stages WHERE op_date = ? AND data_source = ?",
    conn,
    params=[query_date, active_source],
)


def kpi_html(label, value, subtitle, icon, icon_bg="#EFF6FF", icon_color="#1D4ED8", variant="default"):
    card_cls = "kpi-card"
    val_cls = "kpi-val"
    if variant == "active":
        card_cls = "kpi-card-active"
        val_cls = "kpi-val-blue"
    elif variant == "alert":
        card_cls = "kpi-card-alert"
        val_cls = "kpi-val-blue"
    return (
        f'<div class="{card_cls}">'
        f'<div class="kpi-header">'
        f'<span class="kpi-label">{label}</span>'
        f'<span class="kpi-icon-box" style="background:{icon_bg}; color:{icon_color};">{icon}</span>'
        f'</div>'
        f'<div class="{val_cls}">{value}</div>'
        f'<div class="kpi-sub">↗ {subtitle}</div>'
        f'</div>'
    )


total_loads = len(df_loads)
alp_nom = int((df_loads["alp_status"] == "Provided").sum()) if total_loads else 0
tm_nom = int((df_loads["tm_status"] == "Provided").sum()) if total_loads else 0
both_prov = int(((df_loads["alp_status"] == "Provided") & (df_loads["tm_status"] == "Provided")).sum()) if total_loads else 0
alp_only = int(((df_loads["alp_status"] == "Provided") & (df_loads["tm_status"] != "Provided")).sum()) if total_loads else 0
tm_only = int(((df_loads["alp_status"] != "Provided") & (df_loads["tm_status"] == "Provided")).sum()) if total_loads else 0
neither_prov = int(((df_loads["alp_status"] != "Provided") & (df_loads["tm_status"] != "Provided")).sum()) if total_loads else 0
loads_moving = int(df_loads["load_status"].isin(["ON RUN", "MADE OVER", "EN ROUTE"]).sum()) if total_loads else 0
loads_on_run = int((df_loads["load_status"] == "ON RUN").sum()) if total_loads else 0
loads_made_over = int((df_loads["load_status"] == "MADE OVER").sum()) if total_loads else 0
loads_en_route = int((df_loads["load_status"] == "EN ROUTE").sum()) if total_loads else 0
crew_not_moved = int((df_loads["load_status"] == "Crew, not moved").sum()) if total_loads else 0
awaiting_crew = int((df_loads["load_status"] == "Awaiting crew").sum()) if total_loads else 0
exceptions_df = df_loads[df_loads["attention_required"].notna() & (df_loads["attention_required"] != "")] if total_loads else pd.DataFrame()
high_prio_df = exceptions_df[exceptions_df["priority"].str.upper() == "HIGH"] if not exceptions_df.empty else pd.DataFrame()

# -----------------------------------------------------------------------------
# 7. VIEW: MORE MENU (LOBBY PERFORMANCE, PASSWORD, LOGOUT)
# -----------------------------------------------------------------------------
if st.session_state.active_nav == "More":
    st.subheader("Operations & Account")
    st.caption(f"Signed in as **{current_user['full_name']} (@{current_user['username']})** · Role: **{active_role}** · Lobby: **{user_lobby}**")

    more_menu_html = (
        f'<div style="display:flex; flex-direction:column; gap:10px; max-width:480px; margin-top:12px;">'
        f'<a class="oc-nav-item" style="flex-direction:row; justify-content:flex-start; gap:12px; height:52px; max-width:100%; background:#FFFFFF; border:1px solid #E5E7EB; padding:0 16px; font-size:0.9rem;" href="?tab=Lobby Performance&sid={user_sid}" target="_self">'
        f'<span>🏢</span><span>Lobby Performance</span></a>'
        f'<a class="oc-nav-item" style="flex-direction:row; justify-content:flex-start; gap:12px; height:52px; max-width:100%; background:#FFFFFF; border:1px solid #E5E7EB; padding:0 16px; font-size:0.9rem;" href="?tab=Password&sid={user_sid}" target="_self">'
        f'<span>🔑</span><span>Change My Password</span></a>'
        f'<a class="oc-nav-item" style="flex-direction:row; justify-content:flex-start; gap:12px; height:52px; max-width:100%; background:#FEF2F2; border:1px solid #FECACA; color:#DC2626 !important; font-weight:700; padding:0 16px; font-size:0.9rem;" href="?tab=Logout" target="_self">'
        f'<span>🚪</span><span>Sign Out / Logout</span></a>'
        f'</div>'
    )
    st.markdown(more_menu_html, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. VIEW: EXECUTIVE DASHBOARD (HOME)
# -----------------------------------------------------------------------------
elif st.session_state.active_nav == "Home":
    st.subheader("Executive Dashboard")
    st.caption(f"Sheet: **{selected_date}** · Lobby: **{selected_lobby}** · Source: **{active_source}** · **{total_loads} sets Crew Required**")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_html("Sets crew required", total_loads, f"Sheet: {selected_date}", "📦", variant="active"), unsafe_allow_html=True)
    with c2:
        pct_both = round((both_prov / total_loads) * 100) if total_loads else 0
        st.markdown(kpi_html("ALP/LPG & TM both provided", both_prov, f"{pct_both}% complete crew sets", "👤", "#DCFCE7", "#15803D"), unsafe_allow_html=True)
    with c3:
        pct_alp = round((alp_nom / total_loads) * 100) if total_loads else 0
        st.markdown(kpi_html("ALP/LPG nominated", alp_nom, f"{pct_alp}% of loads", "👥"), unsafe_allow_html=True)
    with c4:
        pct_tm = round((tm_nom / total_loads) * 100) if total_loads else 0
        st.markdown(kpi_html("TM nominated", tm_nom, f"{pct_tm}% of loads", "👤"), unsafe_allow_html=True)

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(kpi_html("Loads on run", loads_on_run, "Active movement", "🅰️", "#DCFCE7", "#15803D"), unsafe_allow_html=True)
    with c6:
        st.markdown(kpi_html("Loads made over", loads_made_over, "Handed over / completed", "✅", "#DCFCE7", "#15803D"), unsafe_allow_html=True)
    with c7:
        st.markdown(kpi_html("Either TM or ALP/LPG only", alp_only + tm_only, "Joint Traffic & OP review", "⚠️", "#FEF3C7", "#D97706"), unsafe_allow_html=True)
    with c8:
        st.markdown(kpi_html("Load with crew, not moved", crew_not_moved, "Operational attention required", "🕒", "#FEE2E2", "#DC2626", variant="alert"), unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("#### Crew arrangement overview")
        donut_df = pd.DataFrame({
            "Category": ["Both ALP/LPG & TM", "ALP/LPG only", "TM only", "Neither provided"],
            "Count": [both_prov, alp_only, tm_only, neither_prov],
        })
        fig_donut = px.pie(
            donut_df,
            values="Count",
            names="Category",
            hole=0.68,
            color="Category",
            color_discrete_map={
                "Both ALP/LPG & TM": "#008744",
                "ALP/LPG only": "#1976D2",
                "TM only": "#D97706",
                "Neither provided": "#DC2626",
            },
        )
        fig_donut.add_annotation(text=f"<b>{both_prov}</b><br>both provided", x=0.5, y=0.5, showarrow=False, font_size=16)
        fig_donut.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=290, legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_right:
        st.markdown("#### Load status distribution")
        status_order = ["On run", "Made over", "En route", "At destination", "Crew, not moved", "Awaiting crew"]
        status_counts = [
            loads_on_run,
            loads_made_over,
            loads_en_route,
            int((df_loads["load_status"] == "At destination").sum()) if total_loads else 0,
            crew_not_moved,
            awaiting_crew,
        ]
        fig_status = go.Figure(
            go.Bar(
                x=status_counts[::-1],
                y=status_order[::-1],
                orientation="h",
                marker_color=["#E5E7EB", "#DC2626", "#D97706", "#003F88", "#1976D2", "#008744"],
                text=status_counts[::-1],
                textposition="auto",
            )
        )
        fig_status.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=290, xaxis_title="Loads")
        st.plotly_chart(fig_status, use_container_width=True)

    p_col, a_col = st.columns([1, 1.6])
    with p_col:
        st.markdown("#### Operational priority")
        st.error(f"🚩 **{len(high_prio_df)} high-priority loads require attention**")
        if not high_prio_df.empty:
            for _, row in high_prio_df.iterrows():
                prio_card = (
                    f'<div style="background:#EFF6FF; border-left:4px solid #1976D2; padding:10px 12px; border-radius:8px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">'
                    f'<div><div style="font-weight:700; color:#1E40AF;">{row["load_code"]}</div>'
                    f'<div style="font-size:0.8rem; color:#6B7280;">Dest: {row["destination"]} · Sr: {row["sr_no"] or "-"}</div></div>'
                    f'<span class="pill-high">{row["load_status"]}</span>'
                    f'</div>'
                )
                st.markdown(prio_card, unsafe_allow_html=True)

    with a_col:
        st.markdown(f"#### ⚠️ Attention Required ({len(exceptions_df)} exceptions)")
        if not exceptions_df.empty:
            st.dataframe(
                exceptions_df[["sr_no", "load_code", "destination", "priority", "alp_status", "tm_status", "attention_required"]].rename(
                    columns={
                        "sr_no": "Sr NO",
                        "load_code": "Load stabled",
                        "destination": "Destination",
                        "priority": "Priority",
                        "alp_status": "ALP/LPG",
                        "tm_status": "TM",
                        "attention_required": "Attention required",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

# -----------------------------------------------------------------------------
# 9. VIEW: LOAD MONITORING (LOADS)
# -----------------------------------------------------------------------------
elif st.session_state.active_nav == "Loads":
    st.subheader("Load Monitoring")
    st.caption(f"Sheet: **{selected_date}** · Lobby: **{selected_lobby}** · Source: **{active_source}**")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_html("Total loads", total_loads, "Sets crew required", "👥", variant="active"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_html("Complete arrangements", both_prov, "ALP/LPG and TM provided", "🕒", "#DCFCE7", "#15803D"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_html("Loads moving", loads_moving, "On run / Made over / En route", "🅰️", "#DCFCE7", "#15803D"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_html("Awaiting crew", awaiting_crew, "Partial or pending crew", "👤", "#FEF3C7", "#D97706"), unsafe_allow_html=True)

    st.markdown("#### Load register")
    search_load = st.text_input("Search load stabled, destination or status", placeholder="e.g., MSTB, FGDA, JAJ, ASN...")
    filtered_reg = df_loads.copy()
    if search_load and not filtered_reg.empty:
        mask = (
            filtered_reg["load_code"].str.contains(search_load, case=False, na=False)
            | filtered_reg["destination"].str.contains(search_load, case=False, na=False)
            | filtered_reg["load_status"].str.contains(search_load, case=False, na=False)
        )
        filtered_reg = filtered_reg[mask]

    st.dataframe(
        filtered_reg[["sr_no", "load_code", "coal_load", "current_dest", "destination", "priority", "alp_status", "tm_status", "load_status", "duty_hours"]].rename(
            columns={
                "sr_no": "Sr NO",
                "load_code": "Load stabled",
                "coal_load": "Coal Load",
                "current_dest": "Curr. Dest",
                "destination": "Destination",
                "priority": "Priority",
                "alp_status": "ALP/LPG",
                "tm_status": "TM",
                "load_status": "Status of load",
                "duty_hours": "Duty hrs",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

# -----------------------------------------------------------------------------
# 10. VIEW: CREW ARRANGEMENT (CREW)
# -----------------------------------------------------------------------------
elif st.session_state.active_nav == "Crew":
    st.subheader("Crew Arrangement")
    st.caption(f"Train Advice LPG/ALP & TM · **{selected_date}** ({active_source})")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_html("ALP/LPG nominated", alp_nom, f"{total_loads - alp_nom} pending", "👥"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_html("TM nominated", tm_nom, f"{total_loads - tm_nom} pending", "🕒", variant="active"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_html("Both provided", both_prov, "Complete crew sets", "🅰️", "#DCFCE7", "#15803D"), unsafe_allow_html=True)
    with c4:
        mean_diff = int(df_loads["nom_diff_min"].dropna().mean()) if not df_loads["nom_diff_min"].dropna().empty else 0
        st.markdown(kpi_html("Nomination difference", f"{mean_diff} min", "Mean ALP vs TM time gap", "👤", "#FEF3C7", "#D97706"), unsafe_allow_html=True)

    st.markdown("#### Lobby-wise nominations")
    dynamic_lobbies = sorted([x for x in set(df_loads["alp_lobby"].dropna().tolist() + df_loads["tm_lobby"].dropna().tolist()) if x])
    lobby_rows = []
    for lb in dynamic_lobbies:
        alp_cnt = int(((df_loads["alp_lobby"] == lb) & (df_loads["alp_status"] == "Provided")).sum())
        tm_cnt = int(((df_loads["tm_lobby"] == lb) & (df_loads["tm_status"] == "Provided")).sum())
        lobby_rows.append({"Lobby": lb, "Category": "ALP/LPG", "Nominated": alp_cnt})
        lobby_rows.append({"Lobby": lb, "Category": "TM", "Nominated": tm_cnt})

    if lobby_rows:
        fig_lobby = px.bar(
            pd.DataFrame(lobby_rows),
            x="Lobby",
            y="Nominated",
            color="Category",
            barmode="group",
            color_discrete_map={"ALP/LPG": "#008744", "TM": "#1976D2"},
        )
        fig_lobby.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_lobby, use_container_width=True)

    st.markdown("#### Crew nomination & lobby movement register")
    st.dataframe(
        df_loads[["sr_no", "load_code", "alp_lobby", "alp_time", "alp_id", "lpg_id", "tm_lobby", "tm_time", "tm_id", "leaving_lobby_time", "means"]].fillna("-").rename(
            columns={
                "sr_no": "Sr NO",
                "load_code": "Load stabled",
                "alp_lobby": "ALP Lobby",
                "alp_time": "ALP Time",
                "alp_id": "ALP ID",
                "lpg_id": "LPG ID",
                "tm_lobby": "TM Lobby",
                "tm_time": "TM Time",
                "tm_id": "TM ID",
                "leaving_lobby_time": "Left Lobby",
                "means": "Means",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

# -----------------------------------------------------------------------------
# 11. VIEW: DETENTION ANALYSIS (ANALYSIS)
# -----------------------------------------------------------------------------
elif st.session_state.active_nav == "Analysis":
    st.subheader("Detention Analysis")
    st.caption(f"Recorded intervals and operational evidence · **{selected_date}** ({active_source})")

    overall_val = int(df_stages["avg_minutes"].sum()) if not df_stages.empty else 135
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_html("Overall recorded interval", f"{overall_val} min", "Identification to actual movement", "👥"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_html("Crew transportation", "44 min", "Departure to destination arrival", "🕒"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_html("Post-arrival to CTO", "14 min", "Both arrivals to both CTO timestamps", "🅰️"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_html("Exceptions / Not moved", len(exceptions_df), "Requires joint Traffic & OP review", "⚠️", "#FEE2E2", "#DC2626", variant="alert"), unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Recorded detention stages")
        if not df_stages.empty:
            fig_det = px.bar(
                df_stages.iloc[::-1],
                x="avg_minutes",
                y="stage",
                orientation="h",
                text="avg_minutes",
                color_discrete_sequence=["#1976D2"],
            )
            fig_det.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10), xaxis_title="Minutes", yaxis_title="")
            st.plotly_chart(fig_det, use_container_width=True)

    with col2:
        st.markdown("#### Evidence completeness")
        if not df_stages.empty:
            st.dataframe(
                df_stages[["stage", "valid_count", "excluded_count", "avg_minutes"]].rename(
                    columns={"stage": "Stage", "valid_count": "Valid", "excluded_count": "Excluded", "avg_minutes": "Average (min)"}
                ),
                use_container_width=True,
                hide_index=True,
            )
        st.warning("ℹ️ Elapsed time alone does not establish a detention cause. Missing evidence is classified as “Reason Not Established”.")

# -----------------------------------------------------------------------------
# 12. VIEW: LOBBY PERFORMANCE
# -----------------------------------------------------------------------------
elif st.session_state.active_nav == "Lobby Performance":
    st.subheader("Lobby Performance & Crew Movement")
    st.caption(f"Load movement rate by associated lobby · **{selected_date}** ({active_source})")

    dynamic_lobbies = sorted([x for x in df_loads["alp_lobby"].dropna().unique().tolist() if x])
    perf_rows = []
    for lb in dynamic_lobbies:
        sub = df_loads[df_loads["alp_lobby"] == lb]
        moved = int(sub["load_status"].isin(["ON RUN", "MADE OVER", "EN ROUTE"]).sum())
        rate = round((moved / len(sub)) * 100) if len(sub) else 0
        perf_rows.append({"Lobby": lb, "Movement Rate (%)": rate, "Total Loads": len(sub), "Moved": moved})

    if perf_rows:
        perf_df = pd.DataFrame(perf_rows).sort_values("Movement Rate (%)", ascending=True)
        fig_perf = px.bar(
            perf_df,
            x="Movement Rate (%)",
            y="Lobby",
            orientation="h",
            text="Movement Rate (%)",
            range_x=[0, 100],
            color_discrete_sequence=["#008744"],
        )
        fig_perf.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_perf, use_container_width=True)
        st.dataframe(perf_df.sort_values("Movement Rate (%)", ascending=False), use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# 13. PANEL: DATA UPLOAD (SUPER ADMIN & DATA ADMIN ONLY)
# -----------------------------------------------------------------------------
elif st.session_state.active_nav == "Data Upload":
    if active_role not in ("Super Admin", "Data Admin"):
        st.error("⛔ Access Denied: Only Super Admin and Data Admin can upload date sheets.")
    else:
        st.subheader("📤 Upload Date Sheet Workbook / CSV")
        st.caption("Upload an Excel workbook with date tabs (e.g. `22102026`, `23102026`, `24102026`) or a CSV file.")

        uploaded_file = st.file_uploader("Select Excel (.xlsx) or CSV (.csv) File", type=["xlsx", "csv"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".xlsx"):
                    xls = pd.ExcelFile(uploaded_file)
                    upload_mode = st.radio(
                        "Import Mode",
                        ["Import Single Selected Sheet", "Import All Non-Empty Date Sheets in Workbook"],
                        horizontal=True,
                    )

                    if upload_mode == "Import Single Selected Sheet":
                        selected_sheet = st.selectbox("Select Date Sheet Tab", xls.sheet_names)
                        inferred_str = sheet_name_to_date_str(selected_sheet, datetime.now().strftime("%d-%m-%Y"))
                        try:
                            default_dt = datetime.strptime(inferred_str, "%d-%m-%Y").date()
                        except ValueError:
                            default_dt = date.today()

                        chosen_date_obj = st.date_input("Set Operational Date for this Sheet", value=default_dt)
                        formatted_upload_date = chosen_date_obj.strftime("%d-%m-%Y")

                        uploaded_file.seek(0)
                        parsed_df = parse_crew_arrangement_excel(uploaded_file, selected_sheet, formatted_upload_date)

                        if parsed_df.empty:
                            st.warning(f"Sheet '{selected_sheet}' is empty. Dashboard will continue showing default values.")
                        else:
                            st.success(f"Found **{len(parsed_df)} loads** in sheet `{selected_sheet}` → Date **{formatted_upload_date}**.")
                            st.dataframe(parsed_df.head(15), use_container_width=True, hide_index=True)

                            if st.button(f"✅ Publish Date Sheet ({formatted_upload_date})", type="primary"):
                                db_conn = get_conn()
                                save_uploaded_df_to_db(db_conn, parsed_df, formatted_upload_date)
                                db_conn.execute("UPDATE app_settings SET value = ? WHERE key = 'active_op_date'", (formatted_upload_date,))
                                db_conn.commit()
                                db_conn.close()
                                st.session_state.active_nav = "Home"
                                st.query_params["tab"] = "Home"
                                st.query_params["sid"] = user_sid
                                st.rerun()
                    else:
                        if st.button("✅ Import All Populated Date Sheets", type="primary"):
                            db_conn = get_conn()
                            imported_dates = []
                            for sh in xls.sheet_names:
                                dt_str = sheet_name_to_date_str(sh, sh)
                                uploaded_file.seek(0)
                                df_sh = parse_crew_arrangement_excel(uploaded_file, sh, dt_str)
                                if not df_sh.empty:
                                    save_uploaded_df_to_db(db_conn, df_sh, dt_str)
                                    imported_dates.append((dt_str, len(df_sh)))
                            if imported_dates:
                                db_conn.execute("UPDATE app_settings SET value = ? WHERE key = 'active_op_date'", (imported_dates[-1][0],))
                                db_conn.commit()
                                db_conn.close()
                                st.session_state.active_nav = "Home"
                                st.query_params["tab"] = "Home"
                                st.query_params["sid"] = user_sid
                                st.rerun()
                            else:
                                db_conn.close()
                                st.warning("All sheets in this workbook were empty.")
                else:
                    chosen_date_obj = st.date_input("Set Operational Date for CSV", value=date.today())
                    formatted_upload_date = chosen_date_obj.strftime("%d-%m-%Y")
                    raw_csv = pd.read_csv(uploaded_file)
                    raw_csv["op_date"] = formatted_upload_date
                    st.dataframe(raw_csv.head(15), use_container_width=True, hide_index=True)
                    if st.button(f"✅ Publish CSV for {formatted_upload_date}", type="primary"):
                        db_conn = get_conn()
                        save_uploaded_df_to_db(db_conn, raw_csv, formatted_upload_date)
                        db_conn.execute("UPDATE app_settings SET value = ? WHERE key = 'active_op_date'", (formatted_upload_date,))
                        db_conn.commit()
                        db_conn.close()
                        st.session_state.active_nav = "Home"
                        st.query_params["tab"] = "Home"
                        st.query_params["sid"] = user_sid
                        st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {e}")

        if uploaded_dates:
            st.markdown("---")
            st.markdown("##### Manage Uploaded Date Sheets")
            rm_col1, rm_col2 = st.columns([2, 1])
            with rm_col1:
                date_to_remove = st.selectbox("Select Uploaded Date Sheet to Remove", uploaded_dates)
            with rm_col2:
                st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Delete Date Sheet", use_container_width=True):
                    db_conn = get_conn()
                    db_conn.execute("DELETE FROM loads WHERE op_date = ? AND data_source = 'Uploaded data'", (date_to_remove,))
                    db_conn.execute("DELETE FROM detention_stages WHERE op_date = ? AND data_source = 'Uploaded data'", (date_to_remove,))
                    db_conn.execute("UPDATE app_settings SET value = ? WHERE key = 'active_op_date'", (DEFAULT_SAMPLE_DATE,))
                    db_conn.commit()
                    db_conn.close()
                    st.rerun()

# -----------------------------------------------------------------------------
# 14. PANEL: USER MANAGEMENT (STRICTLY 1 SUPER ADMIN; CREATES DATA ADMIN & USER)
# -----------------------------------------------------------------------------
elif st.session_state.active_nav == "User Management":
    if active_role != "Super Admin":
        st.error("⛔ Access Denied: User Management is restricted to Super Admin.")
    else:
        st.subheader("🛡️ User Management (Super Admin Control)")
        st.caption("Only **one Super Admin** exists in the system. Create **Data Admin** or **User** accounts below.")

        with st.form("create_operator_form", clear_on_submit=True):
            st.markdown("##### Create New Data Admin / User")
            u1, u2, u3, u4, u5 = st.columns([1.3, 1.7, 1.2, 1.2, 1.4])
            with u1:
                new_username = st.text_input("Username", placeholder="e.g., data_asn").strip()
            with u2:
                new_fullname = st.text_input("Full Name", placeholder="Full name").strip()
            with u3:
                new_role = st.selectbox("Role", ["Data Admin", "User"])
            with u4:
                new_lobby = st.text_input("Assigned Lobby", value="ALL").strip().upper()
            with u5:
                new_pass = st.text_input("Password (min 6 chars)", type="password")

            if st.form_submit_button("➕ Create Account", type="primary"):
                if not new_username or not new_fullname or len(new_pass) < 6:
                    st.warning("Username, Full Name, and a password of at least 6 characters are required.")
                else:
                    try:
                        db_conn = get_conn()
                        db_conn.execute(
                            "INSERT INTO users (username, full_name, role, lobby, password_hash, status, created_at) VALUES (?, ?, ?, ?, ?, 'Active', ?)",
                            (
                                new_username,
                                new_fullname,
                                new_role,
                                new_lobby or "ALL",
                                hash_password(new_pass),
                                datetime.now().strftime("%Y-%m-%d %H:%M"),
                            ),
                        )
                        db_conn.commit()
                        db_conn.close()
                        st.success(f"Account '@{new_username}' ({new_role}) created successfully!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error(f"Username '{new_username}' is already taken.")

        st.markdown("##### Registered Accounts")
        users_df = pd.read_sql_query("SELECT id, username, full_name, role, lobby, status, created_at FROM users ORDER BY id ASC", conn)
        st.dataframe(users_df, use_container_width=True, hide_index=True)

        non_sa_users = users_df[users_df["role"] != "Super Admin"]["username"].tolist()
        if non_sa_users:
            m1, m2, m3, m4 = st.columns([1.5, 1.5, 1.5, 1])
            with m1:
                target_user = st.selectbox("Select Account", non_sa_users)
            with m2:
                action_choice = st.selectbox(
                    "Action",
                    ["Toggle Active/Inactive", "Reset Password", "Switch to Data Admin", "Switch to User", "Delete Account"],
                )
            with m3:
                reset_pw_val = st.text_input("New Password (if resetting)", type="password")
            with m4:
                st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                if st.button("Apply", use_container_width=True):
                    db_conn = get_conn()
                    if action_choice == "Toggle Active/Inactive":
                        curr_status = users_df.loc[users_df["username"] == target_user, "status"].values[0]
                        next_status = "Inactive" if curr_status == "Active" else "Active"
                        db_conn.execute("UPDATE users SET status = ? WHERE username = ?", (next_status, target_user))
                    elif action_choice == "Reset Password":
                        if len(reset_pw_val) < 6:
                            st.warning("New password must be at least 6 characters.")
                        else:
                            db_conn.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hash_password(reset_pw_val), target_user))
                            st.success(f"Password reset for @{target_user}.")
                    elif action_choice == "Switch to Data Admin":
                        db_conn.execute("UPDATE users SET role = 'Data Admin' WHERE username = ?", (target_user,))
                    elif action_choice == "Switch to User":
                        db_conn.execute("UPDATE users SET role = 'User' WHERE username = ?", (target_user,))
                    elif action_choice == "Delete Account":
                        db_conn.execute("DELETE FROM users WHERE username = ?", (target_user,))
                    db_conn.commit()
                    db_conn.close()
                    st.rerun()

# -----------------------------------------------------------------------------
# 15. SELF-SERVICE PASSWORD CHANGE
# -----------------------------------------------------------------------------
elif st.session_state.active_nav == "Password":
    st.subheader("🔑 Change My Password")
    st.caption(f"Account: **{current_user['full_name']} (@{current_user['username']})** · Role: **{active_role}**")

    with st.form("self_password_form", clear_on_submit=True):
        curr_pw = st.text_input("Current Password", type="password")
        new_pw = st.text_input("New Password (minimum 6 characters)", type="password")
        confirm_pw = st.text_input("Confirm New Password", type="password")

        if st.form_submit_button("Update Password", type="primary"):
            if new_pw != confirm_pw:
                st.error("New password and confirmation do not match.")
            elif len(new_pw) < 6:
                st.warning("Password must be at least 6 characters.")
            else:
                db_conn = get_conn()
                row = db_conn.execute("SELECT password_hash FROM users WHERE username = ?", (current_user["username"],)).fetchone()
                if row and verify_password(curr_pw, row["password_hash"]):
                    db_conn.execute(
                        "UPDATE users SET password_hash = ? WHERE username = ?",
                        (hash_password(new_pw), current_user["username"]),
                    )
                    db_conn.commit()
                    st.success("Password updated successfully.")
                else:
                    st.error("Current password is incorrect.")
                db_conn.close()

conn.close()