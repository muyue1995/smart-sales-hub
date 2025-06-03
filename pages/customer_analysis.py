# pages/customer_analysis.py
import streamlit as st

st.header("📊 客户分析模块（开发中）")

uploaded_file = st.file_uploader("📎 上传客户 CSV 文件", type=["csv"])

if uploaded_file:
    try:
        import pandas as pd
        df = pd.read_csv(uploaded_file)
        st.success("✅ 上传成功！预览前10行：")
        st.dataframe(df.head(10))
    except Exception as e:
        st.error(f"❌ 出错：{e}")