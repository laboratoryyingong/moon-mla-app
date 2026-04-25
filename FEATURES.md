# MLA Report 3 — 功能说明

## 两种使用方式

### 1. 本地 Web App（推荐）

```bash
pip install -r requirements.txt
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501`

### 2. 命令行 CLI

```bash
python fetch_report3.py
python fetch_report3.py --from 2020-01-01 --to 2024-12-31
python fetch_report3.py --category "Cattle (Excl. Calves)" Lambs
python fetch_report3.py --output my_data.csv
```

---

## Web App 功能（app.py）

| 功能 | 说明 |
|------|------|
| 日期选择器 | 图形化选择 From / To 日期，默认近 5 年 |
| 分类多选 | 下拉多选，留空表示抓取全部 9 个品类 |
| 实时进度条 | 显示当前页 / 总页数、已抓行数、elapsed、ETA |
| Rate limit 提示 | 触发 429/503 时界面显示警告并自动退避 |
| 汇总指标 | 抓取完成后展示总行数、品类数、日期范围 |
| 分类柱状图 | 按品类汇总 value_amt，可视化对比 |
| 数据表格 | 全量数据预览，支持排序和过滤 |
| 一键下载 CSV | Download CSV 按钮，直接保存到本地 |
| Advanced 设置 | 折叠面板，可修改 User-Agent 中的联系邮箱 |

---

## CLI 新增输出信息（fetch_report3.py）

| 输出项 | 示例 |
|--------|------|
| 运行头部 | 日期范围、品类、输出文件、开始时间 |
| 进度条 | `[███░░░░░░░░░░░░░░░░░░░░░░] 12%` |
| 每页详情 | `Page 2/8  100/800 rows  2.1s/page  delay=1.5s  elapsed=6s  ETA 18s` |
| 等待提示 | `Waiting 1.5s before page 3 ...` |
| Rate limit | `⚠  Rate limited (HTTP 429) — backing off to 3.0s` |
| 抓取汇总 | `Fetch complete: 800 rows in 28s  (28.6 rows/s,  8 page(s))` |
| 总运行时间 | `Total runtime: 29s` |

---

## 支持的品类

```
Total Red Meat / Calves / Cattle (Excl. Calves) / Cows And Heifers
Bulls, Bullocks And Steers / Sheep / Lambs / Chickens / Pigs
```

---

## 文件结构

```
moon-mla-app/
├── app.py                          # Streamlit Web App
├── fetch_report3.py                # 核心抓取逻辑 + CLI 入口
├── requirements.txt                # streamlit, pandas
└── report3_slaughter_production.csv  # 默认输出文件
```
