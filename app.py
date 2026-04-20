import streamlit as st
import pandas as pd
import numpy as np
import random
import streamlit.components.v1 as components

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Cyber Threat Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# ---------------- STATE (LIVE FEEL) ----------------
if "tick" not in st.session_state:
    st.session_state.tick = 0
st.session_state.tick += 1

# ---------------- DARK CYBER THEME ----------------
st.markdown("""
<style>

/* GLOBAL */
html, body, [class*="css"] {
    background-color: black !important;
    color: #00ff00 !important;
    font-family: "Courier New", monospace !important;
}

/* HIDE STREAMLIT UI */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ---------------- BLINKING CARDS ---------------- */
.card {
    background: rgba(0,255,0,0.08);
    border: 1px solid #00ff00;
    padding: 14px;
    border-radius: 10px;
    text-align: center;

    animation: pulseGlow 1.5s infinite;
}

@keyframes pulseGlow {
    0% {
        box-shadow: 0 0 5px #00ff00;
        transform: scale(1);
    }
    50% {
        box-shadow: 0 0 25px #00ff00;
        transform: scale(1.03);
    }
    100% {
        box-shadow: 0 0 5px #00ff00;
        transform: scale(1);
    }
}

/* TEXT GLOW */
.card h2, .card h3 {
    color: #00ff00;
    text-shadow: 0 0 10px #00ff00;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: black !important;
    border-right: 1px solid #00ff00;
}

/* BLINK FILTER */
div[data-baseweb="select"] {
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
const columns = Math.floor(canvas.width / fontSize);
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

# ---------------- DATA (2016–2025) ----------------
years = list(range(2016, 2026))

data = []

for y in years:
    # large volume per year
    attacks_per_year = random.randint(2000, 5000)

    for _ in range(attacks_per_year):
        data.append({
            "Year": y,
            "Country": random.choice(["India", "USA", "China", "Germany", "Russia"]),
            "Attack Type": random.choice(["Malware", "Phishing", "Ransomware", "DDoS"]),
            "Severity": random.choice(["Low", "Medium", "High", "Critical"])
        })

df = pd.DataFrame(data)

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚡ Filters")

country = st.sidebar.selectbox("Country", ["All"] + sorted(df["Country"].unique()))
attack_type = st.sidebar.selectbox("Attack Type", ["All"] + sorted(df["Attack Type"].unique()))
search = st.sidebar.text_input("🔍 Search")

# ---------------- LIVE ATTACK PANEL ----------------
st.sidebar.markdown("## 🌍 Live Attacks")

live = pd.DataFrame({
    "Country": ["India", "USA", "China", "Germany", "Russia"]
})

live["Attacks"] = [
    random.randint(80, 200) + st.session_state.tick,
    random.randint(90, 220) + st.session_state.tick,
    random.randint(70, 180) + st.session_state.tick,
    random.randint(60, 160) + st.session_state.tick,
    random.randint(100, 240) + st.session_state.tick,
]

live = live.sort_values("Attacks", ascending=False)

for _, r in live.iterrows():
    st.sidebar.markdown(f"""
    <div style="
        border:1px solid #00ff00;
        padding:6px;
        margin:5px 0;
        border-radius:6px;
        background:rgba(0,255,0,0.05);
        font-family:monospace;
    ">
    {r['Country']} → {r['Attacks']}
    </div>
    """, unsafe_allow_html=True)

st.sidebar.caption("🔄 Live cyber feed")

# ---------------- FILTER DATA ----------------
if country != "All":
    df = df[df["Country"] == country]

if attack_type != "All":
    df = df[df["Attack Type"] == attack_type]

if search:
    df = df[df.astype(str).apply(lambda r: r.str.contains(search, case=False).any(), axis=1)]

# ---------------- TITLE ----------------
st.title("🛡️ Cyber Threat Trends Dashboard")

# ---------------- KPI CARDS ----------------
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f'<div class="card"><h3>Total Attacks</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)

with c2:
    st.markdown(f'<div class="card"><h3>Attack Types</h3><h2>{df["Attack Type"].nunique()}</h2></div>', unsafe_allow_html=True)

with c3:
    st.markdown(f'<div class="card"><h3>Countries</h3><h2>{df["Country"].nunique()}</h2></div>', unsafe_allow_html=True)

# ---------------- CHARTS ----------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Attack Distribution")
    st.bar_chart(df["Attack Type"].value_counts())

with c2:
    st.subheader("🌍 Threat Map")
    map_df = pd.DataFrame({
        "lat": np.random.uniform(10, 60, 120),
        "lon": np.random.uniform(60, 120, 120)
    })
    st.map(map_df)

# ---------------- VULNERABILITIES ----------------
st.subheader("🔥 Top Vulnerabilities (2016–2025)")

vulns = pd.DataFrame({
    "Year": years,
    "CVE": [f"CVE-{y}-{random.randint(1000,9999)}" for y in years],
    "Severity": random.choices(["Low", "Medium", "High", "Critical"], k=len(years))
})

st.dataframe(vulns, use_container_width=True)

# ---------------- THREAT GROUPS ----------------
st.subheader("👾 Active Threat Groups")

groups = pd.DataFrame({
    "Name": ["APT28", "Lazarus", "FIN7", "LockBit", "REvil"],
    "Attacks/Year": np.random.randint(100, 600, 5),
    "Target Country": ["USA", "India", "UK", "Germany", "Japan"],
    "Type": ["Malware", "Ransomware", "Phishing", "Exploit", "Botnet"],
    "Severity": ["High", "Critical", "High", "Medium", "Critical"]
})

st.dataframe(groups, use_container_width=True)

# ---------------- RAW DATA ----------------
st.subheader("📦 Raw Data (Live View)")
st.dataframe(df.tail(30), use_container_width=True)