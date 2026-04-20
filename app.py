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
    background-color: #000000 !important;
    color: #00ff00 !important;
    font-family: "Courier New", monospace !important;
}

/* REMOVE WHITE FLASH */
body::before {
    content: "";
    position: fixed;
    inset: 0;
    background: black;
    z-index: -9999;
}

/* HIDE STREAMLIT UI */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* CARD */
.card {
    background: rgba(0,255,0,0.05);
    border: 1px solid #00ff00;
    padding: 16px;
    border-radius: 12px;
    text-align: center;
    animation: pulseGlow 1.6s infinite;
}

/* GLOW ANIMATION */
@keyframes pulseGlow {
    0% { box-shadow: 0 0 5px #00ff00; }
    50% { box-shadow: 0 0 25px #00ff00; }
    100% { box-shadow: 0 0 5px #00ff00; }
}

/* TEXT GLOW */
h1, h2, h3 {
    text-shadow: 0 0 10px #00ff00;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: black !important;
    border-right: 2px solid #00ff00;
}

/* BLINK FILTER */
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
""", height=0)

# ---------------- DATA GENERATION (CACHED, LARGE) ----------------
@st.cache_data
def generate_data():
    years = list(range(2016, 2026))
    countries = ["India", "USA", "China", "Germany", "Russia", "UK", "France", "Japan"]
    attack_types = ["Malware", "Phishing", "Ransomware", "DDoS"]
    severity_levels = ["Low", "Medium", "High", "Critical"]

    data = []

    for y in years:
        # GUARANTEED LARGE DATA (20k+ total)
        attacks_per_year = random.randint(2500, 4000)

        for _ in range(attacks_per_year):
            data.append({
                "Year": y,
                "Country": random.choice(countries),
                "Attack Type": random.choice(attack_types),
                "Severity": random.choices(
                    severity_levels,
                    weights=[0.2, 0.4, 0.3, 0.1]
                )[0]
            })

    return pd.DataFrame(data)

df = generate_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚡ Filters")

country = st.sidebar.selectbox("Country", ["All"] + sorted(df["Country"].unique()))
attack_type = st.sidebar.selectbox("Attack Type", ["All"] + sorted(df["Attack Type"].unique()))
search = st.sidebar.text_input("🔍 Search")

# ---------------- LIVE ATTACK PANEL ----------------
st.sidebar.markdown("## 🌍 Live Attacks")

live_df = df.groupby("Country").size().reset_index(name="Attacks")
live_df["Attacks"] += st.session_state.tick * 5
live_df = live_df.sort_values("Attacks", ascending=False).head(6)

for _, r in live_df.iterrows():
    st.sidebar.markdown(f"""
    <div style="
        border:1px solid #00ff00;
        padding:6px;
        margin:5px 0;
        border-radius:6px;
        background:rgba(0,255,0,0.05);
    ">
    {r['Country']} → {r['Attacks']}
    </div>
    """, unsafe_allow_html=True)

# ---------------- FILTER DATA ----------------
filtered_df = df.copy()

if country != "All":
    filtered_df = filtered_df[filtered_df["Country"] == country]

if attack_type != "All":
    filtered_df = filtered_df[filtered_df["Attack Type"] == attack_type]

if search:
    filtered_df = filtered_df[
        filtered_df.astype(str).apply(
            lambda r: r.str.contains(search, case=False).any(), axis=1
        )
    ]

# ---------------- TITLE ----------------
st.title("🛡️ Cyber Threat Trends Dashboard [ 2016 - 2025 ] ")

# ---------------- KPI ----------------
c1, c2, c3 = st.columns(3)

c1.markdown(f'<div class="card"><h3>Total Attacks</h3><h2>{len(filtered_df)}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card"><h3>Attack Types</h3><h2>{filtered_df["Attack Type"].nunique()}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card"><h3>Countries</h3><h2>{filtered_df["Country"].nunique()}</h2></div>', unsafe_allow_html=True)

# ---------------- CHARTS ----------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Attack Distribution")
    st.bar_chart(filtered_df["Attack Type"].value_counts())

with col2:
    st.subheader("🌍 Threat Map")
    map_df = pd.DataFrame({
        "lat": np.random.uniform(-60, 70, 500),
        "lon": np.random.uniform(-180, 180, 500)
    })
    st.map(map_df)

# ---------------- VULNERABILITIES ----------------
st.subheader("🔥 Top Vulnerabilities (2016–2025)")

years = list(range(2016, 2026))
vulns = pd.DataFrame({
    "Year": np.repeat(years, 5),
    "CVE": [f"CVE-{y}-{random.randint(1000,9999)}" for y in years for _ in range(5)],
    "Severity": random.choices(["Low","Medium","High","Critical"], k=50)
})

st.dataframe(vulns, use_container_width=True)

# ---------------- THREAT GROUPS ----------------
st.subheader("👾 Active Threat Groups")

groups = pd.DataFrame({
    "Name": ["APT28","Lazarus","FIN7","LockBit","REvil","DarkHydra"],
    "Attacks/Year": np.random.randint(200, 1000, 6),
    "Target Country": ["USA","India","UK","Germany","Japan","France"],
    "Type": ["Malware","Ransomware","Phishing","Exploit","Botnet","DDoS"],
    "Severity": ["High","Critical","High","Medium","Critical","High"]
})

st.dataframe(groups, use_container_width=True)

# ---------------- RAW DATA ----------------
st.subheader("📦 Raw Data (FULL DATASET)")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=500
)
