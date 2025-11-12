# 🤖 Data Analyzer Agent — AI-Powered Exploratory Data Analysis Tool

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)]()

An intelligent desktop application that automates exploratory data analysis (EDA) with AI-generated insights, anomaly detection, and time-series visualization — all in one click.

https://github.com/yourname/data-analyzer-agent/assets/123456789/chart_preview.png

##  Features

-  Batch analyze all CSV/Excel/TXT files in a folder
-  Auto-detect time & numeric columns, plot multi-series time series with **anomaly highlighting**
-  Generate professional Chinese analysis reports using **Qwen-Max (Tongyi Qianwen)**
-  Detect constant/equidistant columns and filter unrealistic values (>200)
-  Provide actionable suggestions (e.g., "missing data >10%", "trend is bullish")
-  Real-time chart preview in GUI

##  Tech Stack

- **AI**: DashScope API + Qwen-Max
- **ML**: Scikit-learn (linear regression), SciPy (IQR outlier detection)
- **Data**: Pandas, NumPy
- **Vis**: Matplotlib, Seaborn
- **GUI**: Tkinter, Pillow
- **Deployment**: Docker-ready, environment-variable managed

## Quick Start

1. Clone the repo:
   ```bash
   git clone https://github.com/yourname/data-analyzer-agent.git
   cd data-analyzer-agent
