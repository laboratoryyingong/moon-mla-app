#!/bin/bash
# 切换到脚本所在目录
cd "$(dirname "$0")"

echo "正在检查依赖..."
python3 -m pip install -r requirements.txt -q

echo "正在启动 MLA Report 3 App..."
streamlit run app.py
