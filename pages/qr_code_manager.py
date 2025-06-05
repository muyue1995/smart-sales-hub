import streamlit as st
import pandas as pd
import pyqrcode
import io
from PIL import Image
import os

from utils.google_sheets import read_sheet_as_df, write_df_to_sheet

SHEET_ID = "1RZPckQc6x8pD3kVLN58FpVqsb985ILH-z4q5h9R7oRU"
LOGO_PATH = "Image/logo.png"  # 修改为你的 logo 文件名（已上传的 PNG）

st.title("📎 QR Code 管理")
st.markdown("此功能能从 Google Sheet 实时读取 SKU 对应 URL，用于生成 QR Code 并管理跳转链接。")

# 读取数据
try:
    df = read_sheet_as_df(SHEET_ID)
    if "sku" not in df.columns or "url" not in df.columns:
        st.error("❌ Google Sheet 必须包含 'sku' 和 'url' 两列。")
    else:
        # 添加新 SKU 和 URL
        st.markdown("### ➕ 添加新 SKU 到 Google Sheet")
        with st.form("add_form", clear_on_submit=True):
            new_sku = st.text_input("输入新 SKU")
            new_url = st.text_input("输入新 URL")
            submitted = st.form_submit_button("📤 添加 SKU")
            if submitted:
                if new_sku in df["sku"].values:
                    st.warning("⚠️ 此 SKU 已存在，请直接修改。")
                else:
                    new_row = pd.DataFrame([[new_sku, new_url]], columns=["sku", "url"])
                    df = pd.concat([df, new_row], ignore_index=True)
                    write_df_to_sheet(SHEET_ID, df)
                    st.success("✅ 新 SKU 已添加！请从下方选择查看二维码。")
                    st.rerun()

        # 搜索 SKU
        st.markdown("### 🔍 搜索 SKU 并生成 QR Code")
        keyword = st.text_input("输入 SKU 关键词搜索")
        filtered_df = df[df["sku"].str.contains(keyword, case=False, na=False)] if keyword else df

        selected_sku = st.selectbox("请选择 SKU", filtered_df["sku"].unique())
        selected_url = df[df["sku"] == selected_sku]["url"].values[0]

        # 生成二维码
        qr = pyqrcode.create(selected_url)
        buffer = io.BytesIO()
        qr.png(buffer, scale=10)
        buffer.seek(0)
        qr_img = Image.open(buffer).convert("RGBA")

        # 嵌入 Logo 图像
        if os.path.exists(LOGO_PATH):
            logo = Image.open(LOGO_PATH).convert("RGBA")

            qr_width, qr_height = qr_img.size
            logo_size = int(qr_width * 0.25)
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)

            qr_img.paste(logo, pos, mask=logo)

            buffer = io.BytesIO()
            qr_img.save(buffer, format="PNG")
            buffer.seek(0)
        else:
            st.warning("⚠️ 未找到 logo 图像，已生成普通二维码。")

        st.image(buffer.getvalue(), caption=f"SKU: {selected_sku}")
        st.download_button(
            label="⬇️ 下载 QR Code PNG",
            data=buffer.getvalue(),
            file_name=f"{selected_sku}_qrcode.png",
            mime="image/png"
        )

        # 修改 URL
        st.markdown("### ✏️ 修改跳转链接")
        new_url = st.text_input("输入新的跳转链接", value=selected_url)
        if st.button("🔄 更新链接"):
            df.loc[df["sku"] == selected_sku, "url"] = new_url
            write_df_to_sheet(SHEET_ID, df)
            st.success("✅ 链接已更新并同步至 Google Sheet")
            st.rerun()

        if st.button("🗑 删除当前 SKU"):
            df = df[df["sku"] != selected_sku]
            write_df_to_sheet(SHEET_ID, df)
            st.success(f"✅ SKU {selected_sku} 已成功删除")
            st.rerun()

        # 展示所有 SKU 数据
        with st.expander("📋 展示所有 SKU 数据（点击展开）"):
            st.dataframe(df)

except Exception as e:
    st.error(f"❌ 无法连接 Google Sheet：{e}")
