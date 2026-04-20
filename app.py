import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import pydeck as pdk

st.set_page_config(
    page_title="Cyber Threat Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# ---------------- AUTO REFRESH ----------------
st.autorefresh(interval=1000, key="live_refresh")

# ---------------- STATE ----------------
if "tick" not in st.session_state:
    st.session_state.tick = 0
st.session_state.tick += 1

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
    margin-top: 0rem !important;
}
section.main > div {
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
div[data-baseweb="select"], input {
    animation: blink 1.2s infinite;
}
@keyframes blink {
    0% { box-shadow: 0 0 5px #00ff00; }
    50% { box-shadow: 0 0 20px #00ff00; }
    100% { box-shadow: 0 0 5px #00ff00; }
}
</style>
""", unsafe_allow_html=True)

# ---------------- MATRIX BACKGROUND ----------------
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
""", height=50)

# ---------------- DATA ----------------
@st.cache_data
def generate_data():
    rows = 150000  # increased volume

    countries = [
        "India","USA","China","Germany","Russia","UK","France","Japan",
        "Brazil","Canada","Australia","South Korea","Italy","Spain",
        "Netherlands","Israel","Singapore","UAE","Turkey","South Africa"
    ]

    return pd.DataFrame({
        "Year": np.random.randint(2016, 2026, rows),
        "Country": np.random.choice(countries, rows),
        "Attack Type": np.random.choice(
            ["Malware","Phishing","Ransomware","DDoS"], rows
        ),
        "Severity": np.random.choice(
            ["Low","Medium","High","Critical"],
            rows,
            p=[0.2,0.4,0.3,0.1]
        )
    })

df = generate_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚡ Filters")

country = st.sidebar.selectbox("Country", ["All"] + sorted(df["Country"].unique()))
attack_type = st.sidebar.selectbox("Attack Type", ["All"] + sorted(df["Attack Type"].unique()))
search = st.sidebar.text_input("🔍 Search")

st.sidebar.markdown("## 🌍 Live Attacks")

live = df.groupby("Country").size().reset_index(name="Attacks")
live["Attacks"] += st.session_state.tick * 10
live = live.sort_values("Attacks", ascending=False).head(10)

for _, r in live.iterrows():
    st.sidebar.markdown(f"""
    <div style="border:1px solid #00ff00;padding:6px;margin:4px;border-radius:6px;">
    {r['Country']} → {r['Attacks']}
    </div>
    """, unsafe_allow_html=True)

# ---------------- FILTER ----------------
filtered_df = df.copy()

if country != "All":
    filtered_df = filtered_df[filtered_df["Country"] == country]

if attack_type != "All":
    filtered_df = filtered_df[filtered_df["Attack Type"] == attack_type]

if search:
    filtered_df = filtered_df[
        filtered_df.astype(str).apply(lambda r: r.str.contains(search, case=False).any(), axis=1)
    ]

# ---------------- TITLE ----------------
st.title("🛡️Cyber Threat Trends Dashboard [2016–2025]")

# ---------------- KPI ----------------
c1, c2, c3 = st.columns(3)

c1.markdown(f'<div class="card"><h3>Total Attacks</h3><h2>{len(filtered_df):,}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card"><h3>Attack Types</h3><h2>{filtered_df["Attack Type"].nunique()}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card"><h3>Countries</h3><h2>{filtered_df["Country"].nunique()}</h2></div>', unsafe_allow_html=True)

# ---------------- CHART ----------------
st.subheader("📊 Attack Distribution")
st.bar_chart(filtered_df["Attack Type"].value_counts())

# ---------------- THREAT MAP ----------------
st.subheader("🌍 Threat Map")

map_data = filtered_df.groupby("Country").size().reset_index(name="Attacks")

# 🌍 Expanded global coordinates
country_coords = {
    "India": (20.5937, 78.9629), "USA": (37.0902, -95.7129),
    "China": (35.8617, 104.1954), "Germany": (51.1657, 10.4515),
    "Russia": (61.5240, 105.3188), "UK": (55.3781, -3.4360),
    "France": (46.2276, 2.2137), "Japan": (36.2048, 138.2529),
    "Brazil": (-14.2350, -51.9253), "Canada": (56.1304, -106.3468),
    "Australia": (-25.2744, 133.7751), "South Korea": (35.9078, 127.7669),
    "Italy": (41.8719, 12.5674), "Spain": (40.4637, -3.7492),
    "Netherlands": (52.1326, 5.2913), "Israel": (31.0461, 34.8516),
    "Singapore": (1.3521, 103.8198), "UAE": (23.4241, 53.8478),
    "Turkey": (38.9637, 35.2433), "South Africa": (-30.5595, 22.9375)
}

map_data = map_data[map_data["Country"].isin(country_coords.keys())]

map_data["lat"] = map_data["Country"].map(lambda x: country_coords[x][0])
map_data["lon"] = map_data["Country"].map(lambda x: country_coords[x][1])

# 🔥 Pulse animation
pulse = (np.sin(st.session_state.tick * 0.5) + 1) / 2
radius_scale = 15 + pulse * 25
alpha = int(120 + pulse * 135)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_data,
    get_position='[lon, lat]',
    get_radius=f'Attacks * {radius_scale}',
    get_fill_color=f'[255, 0, 0, {alpha}]',
    pickable=True
)

view_state = pdk.ViewState(
    latitude=20,
    longitude=0,
    zoom=1.3
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        "html": "<b>{Country}</b><br/>Attacks: {Attacks}",
        "style": {"backgroundColor": "black", "color": "#00ff00"}
    }
))

# ---------------- VULNERABILITIES ----------------
st.subheader("🔥 Top Vulnerabilities")

vulns = pd.DataFrame({
    "Year": np.repeat(range(2016,2026), 10),
    "CVE": [f"CVE-{y}-{np.random.randint(1000,9999)}" for y in range(2016,2026) for _ in range(10)],
    "Severity": np.random.choice(["Low","Medium","High","Critical"], 100)
})

st.dataframe(vulns, use_container_width=True)

# ---------------- GROUPS ----------------
st.subheader("👾 Threat Groups")

groups = pd.DataFrame({
    "Name": ["APT28","Lazarus","FIN7","LockBit","REvil","DarkHydra"],
    "Attacks/Year": np.random.randint(200, 1500, 6),
    "Target Country": ["USA","India","UK","Germany","Japan","France"],
    "Type": ["Malware","Ransomware","Phishing","Exploit","Botnet","DDoS"],
    "Severity": ["High","Critical","High","Medium","Critical","High"]
})

st.dataframe(groups, use_container_width=True)

# ---------------- RAW DATA ----------------
st.subheader("📦 Raw Data (Full Access)")
st.markdown(f"**Total Rows:** {len(filtered_df):,}")

rows = st.slider("Rows to display", 100, 5000, 1000)

st.dataframe(filtered_df.head(rows), use_container_width=True, height=500)

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download Full Dataset",
    csv,
    "cyber_threat_data.csv",
    "text/csv"
)
