import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.markdown("<h2 style='color:#FF5733;'>📦 SKU 热度分析</h2>", unsafe_allow_html=True)

# 上传区
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

week_file = col1.file_uploader("📥 上传一周数据", type="csv", key="week")
month_file = col2.file_uploader("📥 上传一个月数据", type="csv", key="month")
half_file = col3.file_uploader("📥 上传半年数据", type="csv", key="half")
year_file = col4.file_uploader("📥 上传一年数据", type="csv", key="year")

# 缓存上传数据
def cache_csv(uploaded_file, label):
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state[label] = df
            st.toast(f"✅ 成功上传并缓存 {label}")
        except pd.errors.EmptyDataError:
            st.warning(f"⚠️ {label} 文件为空")
        except Exception as e:
            st.error(f"❌ {label} 文件读取失败: {e}")

cache_csv(week_file, "df_week")
cache_csv(month_file, "df_month")
cache_csv(half_file, "df_half")
cache_csv(year_file, "df_year")

def analyze_csv(df, label):
    summary = df.groupby(['sku', 'product'])['quantity'].sum().reset_index()
    summary = summary.sort_values(by='quantity', ascending=False).head(5)
    return summary

analysis_option = st.radio("选择分析方式：", ['📍 单独分析上传的', '📊 一次性汇总分析'])

if analysis_option == '📍 单独分析上传的':
    for label, name in zip(["df_week", "df_month", "df_half", "df_year"],
                           ["📈 一周 Top5", "📈 一个月 Top5", "📈 半年 Top5", "📈 一年 Top5"]):
        if label in st.session_state:
            st.subheader(name)
            df = analyze_csv(st.session_state[label], name)
            st.dataframe(df)

elif analysis_option == '📊 一次性汇总分析':
    if all(k in st.session_state for k in ["df_week", "df_month", "df_half", "df_year"]):
        for label, name in zip(["df_week", "df_month", "df_half", "df_year"],
                               ["一周", "一个月", "半年", "一年"]):
            df = analyze_csv(st.session_state[label], name)
            st.markdown(f"### ⏱️ {name}")
            st.dataframe(df)
    else:
        st.warning("⚠️ 请确保所有数据都已上传并成功读取。")

# 📊 生成趋势表
if st.button("📊 生成趋势汇总表"):
    try:
        df_week = st.session_state["df_week"]
        df_month = st.session_state["df_month"]
        df_half = st.session_state["df_half"]
        df_year = st.session_state["df_year"]

        def summarize(df, label):
            return df.groupby(['sku', 'product'])['quantity'].sum().reset_index().rename(columns={"quantity": label})

        sum_year = summarize(df_year, "year_qty")
        sum_half = summarize(df_half, "half_qty")
        sum_month = summarize(df_month, "month_qty")
        sum_week = summarize(df_week, "week_qty")

        trend_df = sum_year \
            .merge(sum_half, on=['sku', 'product'], how='outer') \
            .merge(sum_month, on=['sku', 'product'], how='outer') \
            .merge(sum_week, on=['sku', 'product'], how='outer') \
            .fillna(0)

        trend_df = trend_df.sort_values(by="year_qty", ascending=False).reset_index(drop=True)
        st.session_state.trend_summary = trend_df

        st.success("✅ 成功生成SKU趋势汇总表")
        st.dataframe(trend_df)

    except KeyError:
        st.error("❌ 有数据未缓存成功，请重新上传四个时间段的CSV。")

# 🧠 AI评分分析
if "trend_summary" in st.session_state:
    trend_df = st.session_state.trend_summary.copy()

    trend_df["week_month_ratio"] = trend_df["week_qty"] / trend_df["month_qty"].replace(0, np.nan)
    trend_df["month_half_ratio"] = trend_df["month_qty"] / trend_df["half_qty"].replace(0, np.nan)
    trend_df["half_year_ratio"] = trend_df["half_qty"] / trend_df["year_qty"].replace(0, np.nan)
    trend_df["year_norm"] = (trend_df["year_qty"] - trend_df["year_qty"].min()) / (trend_df["year_qty"].max() - trend_df["year_qty"].min())

    trend_df["score"] = (
        0.3 * trend_df["week_month_ratio"].fillna(0) +
        0.4 * trend_df["month_half_ratio"].fillna(0) +
        0.2 * trend_df["half_year_ratio"].fillna(0) +
        0.1 * trend_df["year_norm"]
    )

    top5 = trend_df.sort_values(by="score", ascending=False).head(5)

    st.subheader("🔥 AI评分前五 SKU")
    st.dataframe(top5[["sku", "product", "score"]])
    fig = px.bar(top5, x="sku", y="score", color="product", title="AI评分前五SKU排行")
    st.plotly_chart(fig)

# 🔁 刷新
if st.button("🔁 刷新当前页面"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()