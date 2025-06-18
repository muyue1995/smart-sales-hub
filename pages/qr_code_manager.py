import streamlit as st
import pandas as pd
import pyqrcode
import io
from PIL import Image, ImageDraw
import os
import numpy as np

from utils.google_sheets import read_sheet_as_df, write_df_to_sheet

SHEET_ID = "1RZPckQc6x8pD3kVLN58FpVqsb985ILH-z4q5h9R7oRU"
LOGO_PATH = "Image/logo.png"  # Logo 图片路径

st.title("📎 QR Code 管理")
st.markdown("此功能能从 Google Sheet 实时读取 SKU 对应 URL，用于生成 QR Code 并管理跳转链接。")

# 圆角函数
def add_rounded_corners(image, radius):
    circle = Image.new("L", (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
    alpha = Image.new("L", image.size, 255)

    w, h = image.size
    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
    alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))

    image.putalpha(alpha)
    return image

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

        # 搜索并选择 SKU
        st.markdown("### 🔍 搜索 SKU 并生成 QR Code")
        keyword = st.text_input("输入 SKU 关键词搜索")
        filtered_df = df[df["sku"].str.contains(keyword, case=False, na=False)] if keyword else df

        selected_sku = st.selectbox("请选择 SKU", filtered_df["sku"].unique())
        selected_url = df[df["sku"] == selected_sku]["url"].values[0]

        # ✅ 生成 QR Code 并固定大小为 400x400
        qr = pyqrcode.create(selected_url)
        buffer = io.BytesIO()
        qr.png(buffer, scale=10)
        buffer.seek(0)
        qr_img = Image.open(buffer).convert("RGBA")
        qr_img = qr_img.resize((400, 400), Image.LANCZOS)

        # ✅ 替换黑色为灰色 #494D4D
        data = np.array(qr_img)
        r, g, b, a = data.T
        black_areas = (r == 0) & (g == 0) & (b == 0)
        data[..., :-1][black_areas.T] = (73, 77, 77)
        qr_img = Image.fromarray(data)

        # ✅ 加圆角（半径为图像宽度 20%）
        qr_img = add_rounded_corners(qr_img, radius=int(400 * 0.2))

        # ✅ 嵌入 Logo
        if os.path.exists(LOGO_PATH):
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo_size = int(400 * 0.20)
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            pos = ((400 - logo_size) // 2, (400 - logo_size) // 2)
            qr_img.paste(logo, pos, mask=logo)
        else:
            st.warning("⚠️ 未找到 logo 图像，已生成普通二维码。")

        # 显示和下载二维码
        output_buffer = io.BytesIO()
        qr_img.save(output_buffer, format="PNG")
        output_buffer.seek(0)

        st.image(output_buffer.getvalue(), caption=f"SKU: {selected_sku}")
        st.download_button(
            label="⬇️ 下载 QR Code PNG",
            data=output_buffer.getvalue(),
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

        # 删除 SKU
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
