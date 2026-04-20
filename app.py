import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
st.set_page_config(
    page_title="Cyber Threat Dashboard",
    page_icon="🛡️",
    layout="wide"
)
if "tick" not in st.session_state:
    st.session_state.tick = 0
st.session_state.tick += 1
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #000000 !important;
    color: #00ff00 !important;
    font-family: "Courier New", monospace !important;
}
/* REMOVE TOP GAP COMPLETELY */
.block-container {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}

/* Also remove extra spacing from main */
section.main > div {
    padding-top: 0rem !important;
}
/* REMOVE TOP GAP COMPLETELY closed */
/* REMOVE TOP SPACE FROM SIDEBAR (FILTER AREA ONLY) */
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
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
@st.cache_data
def generate_data():
    rows = 120000

    years = np.random.randint(2016, 2026, rows)
    countries = np.random.choice(
        ["India","USA","China","Germany","Russia","UK","France","Japan"], rows
    )
    attacks = np.random.choice(
        ["Malware","Phishing","Ransomware","DDoS"], rows
    )
    severity = np.random.choice(
        ["Low","Medium","High","Critical"],
        rows,
        p=[0.2,0.4,0.3,0.1]
    )

    return pd.DataFrame({
        "Year": years,
        "Country": countries,
        "Attack Type": attacks,
        "Severity": severity
    })

df = generate_data()
st.sidebar.title("⚡ Filters")
country = st.sidebar.selectbox("Country", ["All"] + sorted(df["Country"].unique()))
attack_type = st.sidebar.selectbox("Attack Type", ["All"] + sorted(df["Attack Type"].unique()))
search = st.sidebar.text_input("🔍 Search")
st.sidebar.markdown("## 🌍 Live Attacks")
live = df.groupby("Country").size().reset_index(name="Attacks")
live["Attacks"] += st.session_state.tick * 10
live = live.sort_values("Attacks", ascending=False).head(6)
for _, r in live.iterrows():
    st.sidebar.markdown(f"""
    <div style="border:1px solid #00ff00;padding:6px;margin:4px;border-radius:6px;">
    {r['Country']} → {r['Attacks']}
    </div>
    """, unsafe_allow_html=True)
filtered_df = df.copy()
if country != "All":
    filtered_df = filtered_df[filtered_df["Country"] == country]
if attack_type != "All":
    filtered_df = filtered_df[filtered_df["Attack Type"] == attack_type]
if search:
    filtered_df = filtered_df[
        filtered_df.astype(str).apply(lambda r: r.str.contains(search, case=False).any(), axis=1)
    ]
st.title("🛡️Cyber Threat Trends Dashboard [2016–2025]")
c1, c2, c3 = st.columns(3)
c1.markdown(f'<div class="card"><h3>Total Attacks</h3><h2>{len(filtered_df):,}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card"><h3>Attack Types</h3><h2>{filtered_df["Attack Type"].nunique()}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card"><h3>Countries</h3><h2>{filtered_df["Country"].nunique()}</h2></div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.subheader("📊 Attack Distribution")
    st.bar_chart(filtered_df["Attack Type"].value_counts())
with col2:
    st.subheader("🌍 Threat Map")
    map_df = pd.DataFrame({
        "lat": np.random.uniform(-60, 70, 800),
        "lon": np.random.uniform(-180, 180, 800)
    })
    st.map(map_df)
st.subheader("🔥 Top Vulnerabilities")
vulns = pd.DataFrame({
    "Year": np.repeat(range(2016,2026), 10),
    "CVE": [f"CVE-{y}-{np.random.randint(1000,9999)}" for y in range(2016,2026) for _ in range(10)],
    "Severity": np.random.choice(["Low","Medium","High","Critical"], 100)
})
st.dataframe(vulns, use_container_width=True)
st.subheader("👾 Threat Groups")
groups = pd.DataFrame({
    "Name": ["APT28","Lazarus","FIN7","LockBit","REvil","DarkHydra"],
    "Attacks/Year": np.random.randint(200, 1500, 6),
    "Target Country": ["USA","India","UK","Germany","Japan","France"],
    "Type": ["Malware","Ransomware","Phishing","Exploit","Botnet","DDoS"],
    "Severity": ["High","Critical","High","Medium","Critical","High"]
})
st.dataframe(groups, use_container_width=True)
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
