# src/core.py
from typing import Tuple, Optional, List
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import iqr
import warnings

warnings.filterwarnings("ignore")


def detect_time_column(df: pd.DataFrame) -> Optional[str]:
    """
    尝试自动识别时间列（支持字符串或 datetime 类型）。
    """
    for col in df.columns:
        if df[col].dtype == 'datetime64[ns]':
            return col
        # 尝试解析常见时间格式
        try:
            pd.to_datetime(df[col].iloc[:5], errors='raise')  # 只试前5行加速
            return col
        except (ValueError, TypeError):
            continue
    return None


def detect_numeric_columns(df: pd.DataFrame) -> List[str]:
    """返回数值型列名列表"""
    return df.select_dtypes(include=[np.number]).columns.tolist()


def detect_anomalies(series: pd.Series) -> pd.Series:
    """
    使用 IQR 方法检测异常值。
    
    Returns:
        布尔 Series，True 表示异常点
    """
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR_val = iqr(series.dropna())
    lower_bound = Q1 - 1.5 * IQR_val
    upper_bound = Q3 + 1.5 * IQR_val
    return (series < lower_bound) | (series > upper_bound)


def auto_visualize(filename: str, base_path: str) -> Tuple[str, Optional[str]]:
    """
    自动生成带异常标注的时间序列图。
    
    Args:
        filename: 文件名（如 data.csv）
        base_path: 数据文件夹路径
    
    Returns:
        (消息文本, 图像路径或None)
    """
    file_path = os.path.join(base_path, filename)
    
    # 读取数据
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif filename.endswith('.txt'):
            df = pd.read_csv(file_path, delimiter='\t')
        else:
            return f"❌ 不支持的文件格式：{filename}", None
    except Exception as e:
        return f"❌ 读取文件失败：{e}", None

    if df.empty:
        return "⚠️ 文件为空", None

    # 识别时间列
    time_col = detect_time_column(df)
    if time_col is None:
        return "⚠️ 未找到有效的时间列（需可解析为日期）", None

    # 转换时间列
    try:
        df[time_col] = pd.to_datetime(df[time_col])
    except Exception as e:
        return f"❌ 时间列解析失败：{e}", None

    # 识别数值列
    numeric_cols = detect_numeric_columns(df)
    if not numeric_cols:
        return "⚠️ 未找到数值型列", None

    # 过滤不现实的数值（>200）
    filtered_cols = []
    for col in numeric_cols:
        if df[col].max() <= 200:
            filtered_cols.append(col)
    if not filtered_cols:
        filtered_cols = numeric_cols  # 若全部 >200，仍保留原始列（避免无图）

    # 绘图
    plt.figure(figsize=(12, 6))
    plotted_any = False

    for col in filtered_cols[:3]:  # 最多画3条线，避免混乱
        series = df.set_index(time_col)[col].dropna()
        if len(series) == 0:
            continue

        # 检测异常
        anomalies = detect_anomalies(series)

        # 绘制正常点
        plt.plot(series.index, series.values, label=col, linewidth=1.2)

        # 标注异常点
        if anomalies.any():
            anomaly_series = series[anomalies]
            plt.scatter(anomaly_series.index, anomaly_series.values,
                        color='red', s=30, zorder=5, label=f"{col} 异常点")

        plotted_any = True

    if not plotted_any:
        return "⚠️ 无可绘制的有效数据", None

    plt.title(f"时间序列可视化（含异常检测）\n文件: {filename}", fontsize=14)
    plt.xlabel("时间")
    plt.ylabel("数值")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    # 保存图像
    img_filename = f"图表_{os.path.splitext(filename)[0]}.png"
    img_path = os.path.join(base_path, img_filename)
    plt.savefig(img_path, dpi=150)
    plt.close()

    return f"✅ 图表已生成：{img_filename}", img_path