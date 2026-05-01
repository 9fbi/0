import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
st.set_page_config(
    page_title="CTEM Serverless Dashboard",
    page_icon="🛡️",
    layout="wide"
)
if "tick" not in st.session_state:
    st.session_state.tick = 0
st.session_state.tick += 1
st.markdown("""
<style>
html, body {
    background-color: #000000 !important;
    color: #00ff00 !important;
    font-family: "Courier New", monospace !important;
}
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
</style>
""", unsafe_allow_html=True)
components.html("""
<canvas id="matrix"></canvas>
<script>
const canvas = document.getElementById("matrix");
const ctx = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
const letters = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const fontSize = 14;
const columns = canvas.width / fontSize;
const drops = Array(Math.floor(columns)).fill(1);
function draw(){
    ctx.fillStyle = "rgba(0,0,0,0.05)";
    ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.fillStyle = "#00ff00";
    ctx.font = fontSize + "px monospace";
    for(let i=0;i<drops.length;i++){
        const text = letters[Math.floor(Math.random()*letters.length)];
        ctx.fillText(text, i*fontSize, drops[i]*fontSize);
        if(drops[i]*fontSize > canvas.height && Math.random()>0.975){
            drops[i]=0;
        }
        drops[i]++;
    }
}
setInterval(draw, 35);
</script>
""", height=100)
@st.cache_data
def generate_ctem_data():
    rows = 5000
    return pd.DataFrame({
        "Function": [f"lambda_{i}" for i in range(rows)],
        "Service": np.random.choice(["Lambda","API Gateway","S3"], rows),
        "Exposure": np.random.choice([
            "Public API","Overprivileged IAM","Open S3","No Auth","Env Leak"
        ], rows),
        "Severity": np.random.choice(
            ["Low","Medium","High","Critical"], rows, p=[0.2,0.4,0.3,0.1]
        ),
        "IAM_Risk": np.random.randint(1, 10, rows),
        "Public_Access": np.random.choice([0,1], rows),
        "Last_Triggered": np.random.randint(1, 30, rows)
    })

df = generate_ctem_data()
def calculate_risk(df):
    severity_map = {"Low":1, "Medium":2, "High":3, "Critical":4}
    df["Severity_Score"] = df["Severity"].map(severity_map)

    df["Risk_Score"] = (
        df["Severity_Score"] * 2 +
        df["IAM_Risk"] * 1.5 +
        df["Public_Access"] * 3
    )
    return df

df = calculate_risk(df)
st.sidebar.title("⚡ CTEM Filters")
service = st.sidebar.selectbox("Service", ["All"] + sorted(df["Service"].unique()))
exposure = st.sidebar.selectbox("Exposure", ["All"] + sorted(df["Exposure"].unique()))
severity = st.sidebar.selectbox("Severity", ["All"] + sorted(df["Severity"].unique()))
search = st.sidebar.text_input("🔍 Search Function")
filtered_df = df.copy()
if service != "All":
    filtered_df = filtered_df[filtered_df["Service"] == service]
if exposure != "All":
    filtered_df = filtered_df[filtered_df["Exposure"] == exposure]
if severity != "All":
    filtered_df = filtered_df[filtered_df["Severity"] == severity]
if search:
    filtered_df = filtered_df[filtered_df["Function"].str.contains(search, case=False)]
st.title("🛡️ CTEM Dashboard for Serverless Environment")
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="card"><h3>Total Assets</h3><h2>{len(filtered_df)}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card"><h3>Exposure Types</h3><h2>{filtered_df["Exposure"].nunique()}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card"><h3>Services</h3><h2>{filtered_df["Service"].nunique()}</h2></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="card"><h3>Avg Risk</h3><h2>{filtered_df["Risk_Score"].mean():.2f}</h2></div>', unsafe_allow_html=True)
st.subheader("🔍 Exposure Discovery")
st.bar_chart(filtered_df["Exposure"].value_counts())
st.subheader("🔥 Risk Prioritization")
top_risk = filtered_df.sort_values("Risk_Score", ascending=False).head(10)
st.dataframe(top_risk[["Function","Service","Exposure","Risk_Score"]], use_container_width=True)
st.subheader("🧪 Exploitability Simulation")
filtered_df["Exploitability"] = filtered_df["Risk_Score"] * np.random.uniform(0.5, 1.5, len(filtered_df))
st.line_chart(filtered_df["Exploitability"].head(100))
st.subheader("🧩 Service Exposure Distribution")
st.bar_chart(filtered_df["Service"].value_counts())
def recommendation(row):
    if row["Exposure"] == "Public API":
        return "Enable authentication"
    elif row["Exposure"] == "Overprivileged IAM":
        return "Apply least privilege"
    elif row["Exposure"] == "Open S3":
        return "Restrict bucket access"
    elif row["Exposure"] == "No Auth":
        return "Add authorization layer"
    else:
        return "Secure environment variables"
filtered_df["Fix"] = filtered_df.apply(recommendation, axis=1)
st.subheader("🛠️ Recommended Fixes")
st.dataframe(filtered_df[["Function","Exposure","Fix"]].head(20), use_container_width=True)
st.subheader("📦 Asset Data")
rows = st.slider("Rows to display", 100, 2000, 500)
st.dataframe(filtered_df.head(rows), use_container_width=True)
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇ Download Dataset",
    csv,
    "ctem_serverless_data.csv",
    "text/csv"
)
