import re
from datetime import datetime, time
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Railway Crew & Load Dashboard",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.block-container {padding-top: 1rem; padding-bottom: 2.2rem; max-width: 1500px;}
.stApp {background:linear-gradient(180deg,#f4f7fc 0%,#f8faff 45%,#f4f7fc 100%);}
[data-testid="stHeader"] {background:transparent;}
.hero {background:linear-gradient(115deg,#102b4a 0%,#1c4777 58%,#2875a8 100%);
 color:white;padding:24px 28px;border-radius:18px;margin:4px 0 20px 0;
 box-shadow:0 10px 28px #15375b22;}
.hero h1 {font-size:1.8rem;font-weight:750;margin:0 0 5px 0;color:white;}
.hero p {margin:0;color:#d8e7f7;font-size:.94rem;}
.section-title {font-size:1.12rem;font-weight:750;color:#172b45;margin:18px 0 10px 0;}
[data-testid="stMetric"] {background:linear-gradient(145deg,#fff,#f9fbff);
 border:1px solid #e1e8f1;padding:15px 17px;border-radius:15px;
 box-shadow:0 5px 16px #1a35510b;min-height:112px;}
div[data-testid="stMetricLabel"] p {font-size:0.8rem;color:#617189;font-weight:600;}
div[data-testid="stMetricValue"] {font-size:1.75rem;font-weight:800;color:#172b45;}
[data-testid="stMetricDelta"] {font-size:.72rem;}
div[data-testid="stSelectbox"] label, div[data-testid="stMultiSelect"] label {font-weight:650;}
div[data-testid="stFileUploader"] section {background:white;border:1px dashed #9db4d0;border-radius:14px;}
div[data-testid="stPlotlyChart"] {background:white;border:1px solid #e5ebf3;border-radius:15px;padding:8px;}
.stDownloadButton button {border-radius:10px;font-weight:650;}
.small-note {color:#68778a;font-size:0.82rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🚆 Railway Crew & Load Command Dashboard</h1>
  <p>Daily operational position • Crew nomination • Load movement • DRM reports</p>
</div>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
def norm(value):
    return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())

def safe_text(series):
    return series.fillna("").astype(str).str.strip()

def is_filled(series):
    s = safe_text(series)
    return s.ne("") & s.str.lower().ne("nan") & s.str.lower().ne("none")

def find_col(columns, aliases):
    normalized = {norm(c): c for c in columns}
    for alias in aliases:
        key = norm(alias)
        if key in normalized:
            return normalized[key]
    for c in columns:
        ckey = norm(c)
        for alias in aliases:
            akey = norm(alias)
            if akey and (akey in ckey or ckey in akey):
                return c
    return None

ALIASES = {
    "load": ["Load stabled", "Load", "Train/Load", "Load No", "Train No"],
    "priority": ["Priority to improve mobility", "Priority", "High Priority"],
    "current_destination": ["Current Destination", "Current Dest", "Current Location"],
    "destination": ["Destination", "Final Destination"],
    "alp_lobby": ["ALP/LPG Lobby", "LPG Lobby", "ALP Lobby", "Lobby"],
    "alp_provided_time": ["ALP/LPG Crew provided time", "Crew provided time", "LPG Crew provided time", "ALP Crew provided time"],
    "alp_id": ["ALP ID", "LPG ID", "ALP/LPG ID"],
    "tm_lobby": ["TM Lobby", "TM Crew Lobby"],
    "tm_provided_time": ["TM Crew provided time", "TM provided time"],
    "tm_id": ["TM ID"],
    "alp_onboard": ["Time reached Destination", "Time Reached Destination_20", "ALP Time reached Destination", "ALP Arrived", "ALP Arrival Time"],
    "alp_leave": ["Time leaving Lobby", "Time leaving Lobby_19", "ALP Time leaving Lobby", "ALP Leaving Time"],
    "alp_means": ["Means", "ALP Means of Transport"],
    "tm_means": ["Means_21", "TM Means", "TM Means of Transport"],
    "tm_onboard": ["TM Time reached Destination", "TM Arrival Time", "TM reached Destination"],
    "tm_leave": ["TM Time leaving Lobby", "TM Leaving Time"],
    "status": ["Status of load", "Load Status", "Status"],
    "duty": ["Duty hours of Crew", "Duty Hours", "Crew Duty Hours"],
    "coal": ["Power House COAL LOAD", "Power House Coal Load", "Coal Load"],
    "path": ["Path Availability", "Path Given", "Path Given (Time)"],
    "readiness": ["Loco readiness given by LPG", "Loco Readiness"],
    "cto_alp": ["CTO LPG/ALP", "CTO ALP", "CTO LPG"],
    "cto_tm": ["CTO TM", "TM CTO"],
}

FIELD_LABELS = {
    "load": "Load Stabled",
    "priority": "Priority",
    "current_destination": "Current Destination",
    "destination": "Destination",
    "alp_lobby": "ALP/LPG Lobby",
    "alp_provided_time": "ALP/LPG Crew Provided Time",
    "alp_id": "ALP/LPG ID",
    "tm_lobby": "TM Lobby",
    "tm_provided_time": "TM Crew Provided Time",
    "tm_id": "TM ID",
    "alp_onboard": "Time Reached Destination (ALP/LPG)",
    "alp_leave": "Time Leaving Lobby (ALP/LPG)",
    "alp_means": "Means (ALP/LPG)",
    "tm_means": "Means_21 (TM)",
    "tm_onboard": "TM Time Reached Destination",
    "tm_leave": "TM Time Leaving Lobby",
    "status": "Status of Load",
    "duty": "Duty Hours of Crew",
    "coal": "Power House Coal Load",
    "path": "Path Given (Time)",
    "readiness": "Loco Readiness Given by LPG",
    "cto_alp": "CTO LPG/ALP",
    "cto_tm": "CTO TM",
}

def status_group(value):
    s = str(value or "").strip().lower()
    if not s or s in {"nan", "none"}:
        return "Blank / Not Entered"
    if "made over" in s or "madeover" in s:
        return "Made Over"
    if "on run" in s or "onrun" in s:
        return "On Run"
    if "enroute" in s or "en route" in s:
        return "Enroute"
    if "platform" in s:
        return "At Platform"
    if "cancel" in s:
        return "Cancelled"
    return "Other Status"

def count_filled(df, col):
    return int(is_filled(df[col]).sum()) if col and col in df.columns else 0

def parse_time_minutes(value):
    if pd.isna(value) or str(value).strip() == "":
        return None
    if isinstance(value, pd.Timestamp):
        return value.hour * 60 + value.minute
    if isinstance(value, datetime):
        return value.hour * 60 + value.minute
    if isinstance(value, time):
        return value.hour * 60 + value.minute
    try:
        ts = pd.to_datetime(str(value), errors="coerce")
        if pd.isna(ts):
            return None
        return ts.hour * 60 + ts.minute
    except Exception:
        return None

def make_chart(data, kind, x, title, color=None):
    if data.empty or x not in data.columns:
        st.info("No data is available for this graph with the current filters.")
        return
    counts = data[x].replace("", "Not specified").fillna("Not specified").astype(str).value_counts().rename_axis(x).reset_index(name="Count")
    if kind == "bar":
        fig = px.bar(counts, x=x, y="Count", text="Count", title=title, color="Count",
                     color_continuous_scale="Blues")
        fig.update_layout(coloraxis_showscale=False, xaxis_title="", yaxis_title="Number of loads")
    elif kind == "pie":
        fig = px.pie(counts, names=x, values="Count", hole=0.48, title=title)
    else:
        fig = px.bar(counts, x="Count", y=x, orientation="h", text="Count", title=title,
                     color="Count", color_continuous_scale="Blues")
        fig.update_layout(coloraxis_showscale=False, xaxis_title="Number of loads", yaxis_title="")
    fig.update_traces(textposition="outside")
    fig.update_layout(height=390, margin=dict(l=15,r=20,t=55,b=25), legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)

# ---------- Upload ----------
uploaded = st.file_uploader("Upload CREW ARRANGEMENT Excel file (.xlsx / .xls)", type=["xlsx", "xls"])
if not uploaded:
    st.info("Upload your Excel workbook to begin. The app supports multiple date-wise worksheets.")
    st.markdown("""
    **Dashboard reports available after upload**
- Work / load position and status
- Destination-wise load distribution
- Crew nomination and lobby distribution
- Crew onboarding / movement
- TM nominated
- Made Over and On Run
- Crew provided but load not moved
- High-priority loads
- Power House Coal loads
    """)
    st.stop()

try:
    excel = pd.ExcelFile(uploaded)
except Exception as exc:
    st.error(f"Could not read this Excel file: {exc}")
    st.stop()

sheet_name = st.sidebar.selectbox("Select worksheet / date", excel.sheet_names)
raw = pd.read_excel(uploaded, sheet_name=sheet_name, header=None)
if raw.empty:
    st.error("The selected worksheet is empty.")
    st.stop()

st.sidebar.subheader("Excel layout")
default_header = 3 if len(raw) > 3 else 0
header_row = st.sidebar.number_input("Header row (Excel row number)", min_value=1,
                                     max_value=max(1, len(raw)), value=default_header+1, step=1)
header_values = raw.iloc[int(header_row)-1].tolist()
headers = []
for i, value in enumerate(header_values):
    name = str(value).strip() if pd.notna(value) and str(value).strip() else f"Unnamed_{i+1}"
    if name in headers:
        name = f"{name}_{i+1}"
    headers.append(name)

df = raw.iloc[int(header_row):].copy()
df.columns = headers
df = df.dropna(how="all").reset_index(drop=True)

auto_map = {key: find_col(df.columns, aliases) for key, aliases in ALIASES.items()}
load_col = auto_map["load"]
if load_col:
    valid_rows = is_filled(df[load_col])
    df = df.loc[valid_rows].copy().reset_index(drop=True)

if df.empty:
    st.warning("No load rows were detected. Check the header row and select the correct Load column below.")
    st.stop()

# ---------- Hide / Show Toggle for Column Mapping ----------
st.sidebar.divider()
show_mapping = st.sidebar.toggle("Show Column Mapping", value=False, key="toggle_col_mapping")

choices = ["(Not available)"] + list(df.columns)
mapping = {}

if show_mapping:
    st.sidebar.subheader("Column mapping")
    st.sidebar.caption("Auto-detected fields are preselected. Correct any field that was not detected.")
    for key in ALIASES:
        detected = auto_map.get(key)
        default_idx = choices.index(detected) if detected in choices else 0
        widget_key = f"map_{sheet_name}_{key}"
        selected_col = st.sidebar.selectbox(
            FIELD_LABELS.get(key, key.replace("_", " ").title()),
            choices,
            index=default_idx,
            key=widget_key,
        )
        mapping[key] = None if selected_col == "(Not available)" else selected_col
else:
    for key in ALIASES:
        widget_key = f"map_{sheet_name}_{key}"
        if widget_key in st.session_state:
            val = st.session_state[widget_key]
            mapping[key] = None if val == "(Not available)" else val
        else:
            mapping[key] = auto_map.get(key)

# ---------- Single Unified Filter Box (All Mapped Columns Included, All Values Selected by Default) ----------
st.sidebar.divider()
st.sidebar.subheader("Filters")
date_label = sheet_name
search = st.sidebar.text_input("Sidebar quick search")

available_filter_map = {"All Records (No Filter)": None}
for key in ALIASES:
    col_name = mapping.get(key)
    if col_name and col_name in df.columns:
        label = FIELD_LABELS.get(key, key.replace("_", " ").title())
        available_filter_map[label] = (key, col_name)

selected_filter_label = st.sidebar.selectbox(
    "Filter by (select one column)",
    options=list(available_filter_map.keys()),
    key=f"single_filter_cat_{sheet_name}"
)

filtered = df.copy()
if search:
    mask = filtered.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
    filtered = filtered.loc[mask]

active_filter = available_filter_map[selected_filter_label]
if active_filter is not None:
    filter_key, filter_col = active_filter
    if filter_key == "status":
        all_vals = sorted(df[filter_col].apply(status_group).unique().tolist())
        selected_vals = st.sidebar.multiselect(
            f"Select {selected_filter_label} values",
            options=all_vals,
            default=all_vals,
            key=f"filter_vals_{sheet_name}_{filter_key}"
        )
        filtered = filtered.loc[filtered[filter_col].apply(status_group).isin(selected_vals)]
    else:
        all_vals = sorted(safe_text(df[filter_col]).replace("", "Not specified").unique().tolist())
        selected_vals = st.sidebar.multiselect(
            f"Select {selected_filter_label} values",
            options=all_vals,
            default=all_vals,
            key=f"filter_vals_{sheet_name}_{filter_key}"
        )
        col_series = safe_text(filtered[filter_col]).replace("", "Not specified")
        filtered = filtered.loc[col_series.isin(selected_vals)]

dest_col = mapping["destination"]

# Derived report frame, without changing the original imported data.
work = filtered.copy()
work["__Status_Group"] = work[mapping["status"]].apply(status_group) if mapping["status"] else "Not Available"
work["__Priority"] = safe_text(work[mapping["priority"]]) if mapping["priority"] else ""
work["__Priority_High"] = work["__Priority"].ne("")
work["__ALP_Nominated"] = is_filled(work[mapping["alp_id"]]) if mapping["alp_id"] else (
    is_filled(work[mapping["alp_lobby"]]) if mapping["alp_lobby"] else False)
work["__TM_Nominated"] = is_filled(work[mapping["tm_id"]]) if mapping["tm_id"] else (
    is_filled(work[mapping["tm_lobby"]]) if mapping["tm_lobby"] else False)
work["__ALP_Provided"] = work["__ALP_Nominated"] | (is_filled(work[mapping["alp_provided_time"]]) if mapping["alp_provided_time"] else False)
work["__TM_Provided"] = work["__TM_Nominated"] | (is_filled(work[mapping["tm_provided_time"]]) if mapping["tm_provided_time"] else False)
work["__Both_Crew"] = work["__ALP_Provided"] & work["__TM_Provided"]
work["__Crew_Not_Moved"] = work["__Both_Crew"] & work["__Status_Group"].isin(["Blank / Not Entered", "Other Status"])
if mapping["coal"]:
    work["__Coal"] = safe_text(work[mapping["coal"]]).str.lower().isin(["yes", "y", "1", "true", "coal", "yes "])
else:
    work["__Coal"] = False

# ---------- KPI dashboard ----------
st.subheader(f"Daily position — {date_label}")
total_loads = len(work)
alp_count = int(work["__ALP_Nominated"].sum())
tm_count = int(work["__TM_Nominated"].sum())
both_count = int(work["__Both_Crew"].sum())
made_over = int((work["__Status_Group"] == "Made Over").sum())
on_run = int((work["__Status_Group"] == "On Run").sum())
not_moved = int(work["__Crew_Not_Moved"].sum())
high_priority = int(work["__Priority_High"].sum())
coal_count = int(work["__Coal"].sum())

kpis = [
    ("Loads in data", total_loads),
    ("ALP/LPG nominated", alp_count),
    ("TM nominated", tm_count),
    ("Both crew provided", both_count),
    ("Made Over", made_over),
    ("On Run", on_run),
    ("Crew provided – not moved*", not_moved),
    ("Priority-marked loads", high_priority),
]
rows = st.columns(4)
for i, (label, value) in enumerate(kpis):
    with rows[i % 4]:
        st.metric(label, value)

st.caption("*Prototype rule: both crew are nominated/provided and the load status is blank or categorized as Other Status. Confirm the official railway definition before operational use.")

# ---------- Dedicated Search by Name / Value Section ----------
st.divider()
st.markdown('<div class="section-title">🔍 Search by Name / Value</div>', unsafe_allow_html=True)
st.caption("Search across all columns or target a specific column by crew name, ID, load number, lobby, destination, or any value.")

s_col1, s_col2, s_col3 = st.columns([2.2, 1.3, 0.8])
with s_col1:
    main_search_query = st.text_input(
        "Enter name or value to search",
        placeholder="e.g., Crew ID, Load No, Lobby, Destination, Status...",
        key=f"main_search_query_{sheet_name}"
    )
with s_col2:
    search_scope_options = ["All Columns"] + list(df.columns)
    search_scope_col = st.selectbox(
        "Search in column",
        options=search_scope_options,
        key=f"main_search_col_{sheet_name}"
    )
with s_col3:
    exact_match = st.checkbox("Exact match", value=False, key=f"main_search_exact_{sheet_name}")

if main_search_query.strip():
    q = main_search_query.strip()
    clean_work = work.drop(columns=[c for c in work.columns if c.startswith("__")], errors="ignore")
    if search_scope_col == "All Columns":
        if exact_match:
            search_mask = clean_work.apply(
                lambda col: safe_text(col).str.lower() == q.lower()
            ).any(axis=1)
        else:
            search_mask = clean_work.apply(
                lambda col: safe_text(col).str.contains(re.escape(q), case=False, na=False)
            ).any(axis=1)
    else:
        if exact_match:
            search_mask = safe_text(clean_work[search_scope_col]).str.lower() == q.lower()
        else:
            search_mask = safe_text(clean_work[search_scope_col]).str.contains(re.escape(q), case=False, na=False)

    search_results = clean_work.loc[search_mask].copy()
    st.success(f"Found **{len(search_results)}** matching record(s) for **'{q}'** in **{search_scope_col}**.")
    if not search_results.empty:
        st.dataframe(search_results, use_container_width=True, hide_index=True)
        search_csv = search_results.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Download search results (CSV)",
            data=search_csv,
            file_name=f"search_{re.sub(r'[^a-zA-Z0-9_-]+', '_', q)}_{sheet_name}.csv",
            mime="text/csv",
            key=f"dl_search_{sheet_name}"
        )
    else:
        st.info("No records matched your search query. Try disabling 'Exact match' or searching in 'All Columns'.")
else:
    st.info("Type any name, ID, load number, or value above to filter and inspect matching rows immediately.")

# ---------- Load section: only the requested load-related fields ----------
st.divider()
st.markdown('<div class="section-title">🚂 Load Section</div>', unsafe_allow_html=True)
st.caption("Choose only from the load-related fields requested. The selected field is shown as a load-wise register and, where meaningful, a distribution graph.")

LOAD_SECTION_OPTIONS = [
    ("Means", "alp_means"),
    ("Time leaving Lobby_19", "alp_leave"),
    ("Time Reached Destination_20", "alp_onboard"),
    ("Means_21", "tm_means"),
    ("Loco readiness given by LPG", "readiness"),
    ("CTO LPG/ALP", "cto_alp"),
    ("CTO TM", "cto_tm"),
    ("Path Given (Time)", "path"),
    ("Status of load", "status"),
    ("Duty hours of Crew", "duty"),
]
load_field_label = st.selectbox(
    "Load section – select field",
    [label for label, _ in LOAD_SECTION_OPTIONS],
    key="load_section_field",
)
load_field_key = dict(LOAD_SECTION_OPTIONS)[load_field_label]
load_field_col = mapping.get(load_field_key)

if load_field_col and load_field_col in work.columns:
    load_view_cols = [c for c in [
        mapping.get("load"), mapping.get("current_destination"), mapping.get("destination"),
        load_field_col
    ] if c and c in work.columns]
    load_view_cols = list(dict.fromkeys(load_view_cols))
    load_view = work[load_view_cols].copy()
    load_view = load_view.rename(columns={load_field_col: load_field_label})
    st.dataframe(load_view, use_container_width=True, hide_index=True)

    if load_field_key in {"alp_means", "tm_means", "readiness",
                          "cto_alp", "cto_tm", "path", "status"}:
        values = safe_text(work[load_field_col]).replace("", "Not entered")
        dist = values.value_counts().rename_axis(load_field_label).reset_index(name="Loads")
        fig = px.bar(dist, x=load_field_label, y="Loads", text="Loads",
                     title=f"{load_field_label} – load distribution", color="Loads",
                     color_continuous_scale="Blues")
        fig.update_layout(coloraxis_showscale=False, height=330,
                          margin=dict(l=15, r=20, t=55, b=35), xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    else:
        entered = int(is_filled(work[load_field_col]).sum())
        missing = int(len(work) - entered)
        summary = pd.DataFrame({
            "Entry status": ["Entered", "Not entered"],
            "Loads": [entered, missing]
        })
        fig = px.pie(summary, names="Entry status", values="Loads", hole=.48,
                     title=f"{load_field_label} – entry position")
        fig.update_layout(height=310, margin=dict(l=15, r=20, t=55, b=20))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning(f"Column '{load_field_label}' was not detected. Toggle 'Show Column Mapping' in the sidebar to map it manually.")

# ---------- Selectable single graph ----------
st.divider()
st.subheader("📊 Select a report graph")
graph_options = [
    "Work / Load position",
    "Destination-wise loads",
    "Crew nomination (ALP/LPG vs TM)",
    "Crew onboarding / movement",
    "TM nominated",
    "Made Over",
    "On Run",
    "Crew not moved",
    "High priority loads",
    "Priority-wise load list",
    "Crew lobby distribution",
    "Power House Coal loads",
    "Duty hours distribution",
]
selected_graph = st.selectbox("Choose one graph to display", graph_options)

if selected_graph == "Work / Load position":
    if mapping["status"]:
        make_chart(work.assign(Report=work["__Status_Group"]), "bar", "Report", "Work / load position by status")
    else:
        st.warning("Map the Status of Load column in the sidebar to show this graph.")
elif selected_graph == "Destination-wise loads":
    if dest_col:
        make_chart(work.assign(Report=safe_text(work[dest_col]).replace("", "Not specified")), "hbar", "Report", "Loads by destination")
    else:
        st.warning("Map the Destination column in the sidebar.")
elif selected_graph == "Crew nomination (ALP/LPG vs TM)":
    crew_df = pd.DataFrame({"Crew Type": ["ALP/LPG", "TM"], "Nominated": [alp_count, tm_count]})
    fig = px.bar(crew_df, x="Crew Type", y="Nominated", text="Nominated", title="Crew nomination")
    fig.update_layout(height=390, margin=dict(l=15,r=20,t=55,b=25))
    st.plotly_chart(fig, use_container_width=True)
elif selected_graph == "Crew onboarding / movement":
    alp_on = count_filled(work, mapping["alp_onboard"])
    tm_on = count_filled(work, mapping["tm_onboard"])
    alp_leave = count_filled(work, mapping["alp_leave"])
    tm_leave = count_filled(work, mapping["tm_leave"])
    movement_df = pd.DataFrame({"Movement stage": ["ALP/LPG left lobby", "ALP/LPG reached destination", "TM left lobby", "TM reached destination"],
                                "Loads": [alp_leave, alp_on, tm_leave, tm_on]})
    fig = px.bar(movement_df, x="Movement stage", y="Loads", text="Loads", title="Crew onboarding / movement events")
    fig.update_layout(height=390, margin=dict(l=15,r=20,t=55,b=65), xaxis_tickangle=-12)
    st.plotly_chart(fig, use_container_width=True)
elif selected_graph == "TM nominated":
    fig = px.pie(pd.DataFrame({"TM status":["Nominated","Not nominated"],"Loads":[tm_count,max(0,total_loads-tm_count)]}),
                 names="TM status", values="Loads", hole=.45, title="TM nomination position")
    fig.update_layout(height=390)
    st.plotly_chart(fig, use_container_width=True)
elif selected_graph == "Made Over":
    fig = px.pie(pd.DataFrame({"Status":["Made Over","Other / remaining"],"Loads":[made_over,max(0,total_loads-made_over)]}),
                 names="Status", values="Loads", hole=.45, title="Made Over loads")
    fig.update_layout(height=390)
    st.plotly_chart(fig, use_container_width=True)
elif selected_graph == "On Run":
    fig = px.pie(pd.DataFrame({"Status":["On Run","Other / remaining"],"Loads":[on_run,max(0,total_loads-on_run)]}),
                 names="Status", values="Loads", hole=.45, title="On Run loads")
    fig.update_layout(height=390)
    st.plotly_chart(fig, use_container_width=True)
elif selected_graph == "Crew not moved":
    fig = px.pie(pd.DataFrame({"Position":["Crew provided – not moved","Other / remaining"],"Loads":[not_moved,max(0,total_loads-not_moved)]}),
                 names="Position", values="Loads", hole=.45, title="Crew provided but load not moved")
    fig.update_layout(height=390)
    st.plotly_chart(fig, use_container_width=True)
elif selected_graph == "High priority loads":
    if mapping["priority"]:
        priority_rows = work.loc[work["__Priority_High"]].copy()
        st.metric("Loads with a priority entry", len(priority_rows))
        if not priority_rows.empty:
            show_cols = [c for c in [mapping["load"], mapping["priority"], mapping["current_destination"],
                                      mapping["destination"], mapping["alp_lobby"], mapping["tm_lobby"],
                                      mapping["status"]] if c]
            st.dataframe(priority_rows[show_cols], use_container_width=True, hide_index=True)
        else:
            st.info("No priority-marked loads match the current filters.")
    else:
        st.warning("Map the Priority column in the sidebar.")
elif selected_graph == "Priority-wise load list":
    if mapping["priority"]:
        make_chart(work.assign(Report=work["__Priority"].replace("", "Not specified")),
                   "hbar", "Report", "Loads by exact priority value from Excel")
    else:
        st.warning("Map the Priority column in the sidebar.")
elif selected_graph == "Crew lobby distribution":
    lobby_parts = []
    for typ, col in [("ALP/LPG", mapping["alp_lobby"]), ("TM", mapping["tm_lobby"])]:
        if col:
            part = safe_text(work[col]).replace("", "Not specified").value_counts().rename_axis("Lobby").reset_index(name="Loads")
            part["Crew Type"] = typ
            lobby_parts.append(part)
    if lobby_parts:
        lobby_df = pd.concat(lobby_parts, ignore_index=True)
        fig = px.bar(lobby_df, x="Lobby", y="Loads", color="Crew Type", barmode="group",
                     text="Loads", title="Crew lobby distribution")
        fig.update_layout(height=390, margin=dict(l=15,r=20,t=55,b=50))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Map ALP/LPG Lobby and/or TM Lobby in the sidebar.")
elif selected_graph == "Power House Coal loads":
    coal_df = pd.DataFrame({"Coal flag":["Power House Coal","Other / not marked"],"Loads":[coal_count,max(0,total_loads-coal_count)]})
    fig = px.pie(coal_df, names="Coal flag", values="Loads", hole=.45, title="Power House Coal load position")
    fig.update_layout(height=390)
    st.plotly_chart(fig, use_container_width=True)
elif selected_graph == "Duty hours distribution":
    if mapping["duty"]:
        duty = pd.to_numeric(work[mapping["duty"]], errors="coerce").dropna()
        if len(duty):
            fig = px.histogram(pd.DataFrame({"Duty hours":duty}), x="Duty hours", nbins=12, title="Crew duty hours distribution")
            fig.update_layout(height=390)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Duty hours values could not be interpreted as numeric. Check the source format.")
    else:
        st.warning("Map the Duty Hours column in the sidebar.")

# ---------- Detail table and exports ----------
st.divider()
st.subheader("📋 Filtered load / crew register")
st.caption(f"{len(work)} records shown from worksheet: {sheet_name}")
display_cols = [c for c in [
    mapping["load"], mapping["priority"], mapping["current_destination"], mapping["destination"],
    mapping["alp_lobby"], mapping["alp_provided_time"], mapping["alp_id"],
    mapping["tm_lobby"], mapping["tm_provided_time"], mapping["tm_id"],
    mapping["alp_leave"], mapping["alp_onboard"], mapping["tm_leave"], mapping["tm_onboard"],
    mapping["status"], mapping["duty"]
] if c and c in work.columns]
display_cols = list(dict.fromkeys(display_cols))
if display_cols:
    st.dataframe(work[display_cols], use_container_width=True, hide_index=True)
else:
    st.dataframe(work, use_container_width=True, hide_index=True)

csv = work.drop(columns=[c for c in work.columns if c.startswith("__")], errors="ignore").to_csv(index=False).encode("utf-8-sig")
st.download_button("⬇️ Download filtered report as CSV", data=csv,
                   file_name=f"crew_report_{sheet_name}.csv", mime="text/csv")

excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    work.drop(columns=[c for c in work.columns if c.startswith("__")], errors="ignore").to_excel(writer, index=False, sheet_name="Filtered Report")
st.download_button("⬇️ Download filtered report as Excel", data=excel_buffer.getvalue(),
                   file_name=f"crew_report_{sheet_name}.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with st.expander("Important: calculation assumptions"):
    st.markdown("""
- **ALP/LPG nominated:** counts a row when an ALP/LPG ID is present; if no ID column is mapped, it uses the ALP/LPG lobby field.
- **TM nominated:** counts a row when a TM ID is present; if no ID column is mapped, it uses the TM lobby field.
- **Both crew provided:** both ALP/LPG and TM are nominated/provided. A crew-provided time can also qualify.
- **Made Over / On Run:** detected from the mapped load-status text.
- **Priority-marked loads:** any non-empty value in the source Priority column is counted. The filter shows all distinct priority values found in the uploaded worksheet by default.
- **Crew not moved:** prototype estimate only; both crew are provided and status is blank or Other Status.
- **Load Section:** the dedicated dropdown contains only the ten requested load-related fields. Each field is linked to its corresponding Excel column using the sidebar mapping.
- **Onboarding/movement:** counts non-empty leaving-lobby and reached-destination fields. These are movement event counts, not unique people.
- **Lobby distribution:** counts load records by the ALP/LPG and TM lobby fields separately.
- **Power House Coal:** recognizes Yes/Y/1/True/Coal in the mapped coal-load field.

    Please confirm these definitions with the applicable railway control/DRM reporting instructions before using the figures as official reports.
    """)