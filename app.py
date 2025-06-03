# app.py
import streamlit as st

st.set_page_config(
    page_title="智能销售分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 样式部分
st.markdown("""
    <style>
        .main-title {
            text-align: center;
            padding: 20px 0 10px 0;
            color: #2E86AB;
            font-size: 36px;
            font-weight: bold;
        }
        .subtitle {
            text-align: center;
            font-size: 18px;
            color: #555;
            margin-bottom: 30px;
        }
        .card {
            max-width: 1000px;
            margin: auto;
            padding: 25px;
            border: 1px solid #dee2e6;
            border-radius: 12px;
            background-color: #F8F9FA;
            transition: 0.3s;
            margin-bottom: 25px;
        }
        .card:hover {
            background-color: #EDF4FA;
            border-color: #B0D9F5;
        }
        .card h3 {
            margin-bottom: 10px;
        }
        hr {
            margin-top: 10px;
            margin-bottom: 40px;
        }
    </style>
""", unsafe_allow_html=True)

# 页面头部
st.markdown("<div class='main-title'>Myhomeware 智能销售分析平台</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>为销售、管理层、助理打造的轻量AI驱动工具</div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# 四个功能区域单独一排
st.markdown("""
    <div class='card'>
        <h3>📊 客户分析</h3>
        <p>上传客户数据，查看客户分级、标签、建议等</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class='card'>
        <h3>🔥 SKU热度分析</h3>
        <p>上传销售记录，统计SKU销售数量，按时间段输出Top5</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class='card'>
        <h3>🔗 QR Code 管理</h3>
        <p>生成和管理 SKU 对应的二维码，可用于展厅标识和扫码追踪</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class='card'>
        <h3>🟢 销售状态追踪</h3>
        <p>展示销售当前状态（Online / Busy）并可快速更新前台可见</p>
    </div>
""", unsafe_allow_html=True)
