import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import requests
import time

st.set_page_config(
    page_title="Cyber Threat Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# ---------------- SESSION ----------------
if "tick" not in st.session_state:
    st.session_state.tick = 0
st.session_state.tick += 1

# ---------------- AUTO REFRESH ----------------
if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

if time.time() - st.session_state.last_update > 15:
    st.session_state.last_update = time.time()
    st.rerun()

# ---------------- THEME ----------------
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #000000 !important;
    color: #00ff00 !important;
    font-family: "Courier New", monospace !important;
}
.block-container {
    padding-top: 0rem !important;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.card {
    background: rgba(0,255,0,0.05);
    border: 1px solid #00ff00;
    padding: 16px;
    border-radius: 12px;
    text-align: center;
    animation: glow 1.5s infinite;
}
@keyframes glow {
    0% { box-shadow: 0 0 5px #00ff00; }
    50% { box-shadow: 0 0 25px #00ff00; }
    100% { box-shadow: 0 0 5px #00ff00; }
}
h1, h2, h3 {
    text-shadow: 0 0 10px #00ff00;
}
section[data-testid="stSidebar"] {
    background-color: black !important;
    border-right: 2px solid #00ff00;
}
</style>
""", unsafe_allow_html=True)

# ---------------- MATRIX ----------------
components.html("""
<canvas id="matrix"></canvas>
<style>
canvas {
    position: fixed;
    top: 0;
    left: 0;
    z-index: -1;
    pointer-events: none;
}
</style>
<script>
const canvas = document.getElementById("matrix");
const ctx = canvas.getContext("2d");
function resize(){
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resize();
window.onresize = resize;

const letters = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ#$%^&*";
const fontSize = 14;
const columns = Math.floor(window.innerWidth / fontSize);
const drops = Array(columns).fill(1);

function draw(){
    ctx.fillStyle = "rgba(0,0,0,0.05)";
    ctx.fillRect(0,0,canvas.width,canvas.height);

    ctx.fillStyle = "#00ff00";
    ctx.font = fontSize + "px monospace";

    for(let i=0;i<drops.length;i++){
        const text = letters[Math.floor(Math.random()*letters.length)];
        ctx.fillText(text, i*fontSize, drops[i]*fontSize);

        if(drops[i]*fontSize > canvas.height && Math.random() > 0.975){
            drops[i] = 0;
        }
        drops[i]++;
    }
}
setInterval(draw, 35);
</script>
""", height=0)

# ---------------- DATA ----------------
@st.cache_data
def generate_data():
    rows = 120000
    return pd.DataFrame({
        "Year": np.random.randint(2016, 2026, rows),
        "Country": np.random.choice(["India","USA","China","Germany","Russia","UK","France","Japan"], rows),
        "Attack Type": np.random.choice(["Malware","Phishing","Ransomware","DDoS"], rows),
        "Severity": np.random.choice(["Low","Medium","High","Critical"], rows, p=[0.2,0.4,0.3,0.1])
    })

df = generate_data()

# ---------------- LIVE MAP FUNCTION ----------------
def fetch_live_attacks():
    url = "https://otx.alienvault.com/api/v1/indicators/IPv4/recent"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()

        coords = []
        for item in data.get("results", [])[:200]:
            lat = item.get("latitude")
            lon = item.get("longitude")

            if lat and lon:
                coords.append({"lat": lat, "lon": lon})

        return pd.DataFrame(coords)

    except:
        return pd.DataFrame(columns=["lat","lon"])

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚡ Filters")

country = st.sidebar.selectbox("Country", ["All"] + sorted(df["Country"].unique()))
attack_type = st.sidebar.selectbox("Attack Type", ["All"] + sorted(df["Attack Type"].unique()))

# ---------------- FILTER ----------------
filtered_df = df.copy()

if country != "All":
    filtered_df = filtered_df[filtered_df["Country"] == country]

if attack_type != "All":
    filtered_df = filtered_df[filtered_df["Attack Type"] == attack_type]

# ---------------- TITLE ----------------
st.title("🛡️ Cyber Threat Trends Dashboard [2016–2025]")

# ---------------- KPI ----------------
c1, c2, c3 = st.columns(3)

c1.markdown(f'<div class="card"><h3>Total Attacks</h3><h2>{len(filtered_df):,}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card"><h3>Attack Types</h3><h2>{filtered_df["Attack Type"].nunique()}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card"><h3>Countries</h3><h2>{filtered_df["Country"].nunique()}</h2></div>', unsafe_allow_html=True)

# ---------------- CHARTS ----------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Attack Distribution")
    st.bar_chart(filtered_df["Attack Type"].value_counts())

with col2:
    st.subheader("🌍 Live Threat Map")

    live_map = fetch_live_attacks()

    if not live_map.empty:
        st.map(live_map)
    else:
        st.warning("⚠️ Live data unavailable")

# ---------------- RAW DATA ----------------
st.subheader("📦 Raw Data")
st.dataframe(filtered_df.head(1000), use_container_width=True)
