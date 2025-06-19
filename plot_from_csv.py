import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

CSV_FILENAME = "./log/system_monitor_log.csv"

def plot_data():
    if not os.path.exists(CSV_FILENAME):
        print(f"找不到文件 {CSV_FILENAME}")
        return

    df = pd.read_csv(CSV_FILENAME)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    # 自动识别 GPU 数量
    gpu_load_cols = [col for col in df.columns if 'Load' in col]
    gpu_mem_cols = [col for col in df.columns if 'Memory' in col and 'GPU' in col]
    num_gpus = min(len(gpu_load_cols), len(gpu_mem_cols))
    num_gpus= 1

    # 创建子图（每个 GPU 占两个子图，加上 CPU 和 MEM）
    fig, axes = plt.subplots(2 + 2 * num_gpus, 1, figsize=(14, 6 + num_gpus * 3), sharex=True)
    fig.suptitle("System Usage Over Time", fontsize=16)

    # 子图 1: CPU 使用率
    axes[0].plot(df['Timestamp'], df['CPU (%)'], color='tab:blue')
    axes[0].set_ylabel("CPU (%)")
    axes[0].grid(True)

    # 子图 2: 内存使用率
    axes[1].plot(df['Timestamp'], df['Memory (%)'], color='tab:orange')
    axes[1].set_ylabel("Memory (%)")
    axes[1].grid(True)

    # 动态添加每个 GPU 的数据
    for i in range(num_gpus):
        load_col = gpu_load_cols[i]
        mem_col = gpu_mem_cols[i]

        # GPU 负载
        axes[2 + i * 2].plot(df['Timestamp'], df[load_col], color='tab:green')
        axes[2 + i * 2].set_ylabel(f"{load_col}\n(%)", rotation=0, labelpad=40)
        axes[2 + i * 2].grid(True)

        # GPU 显存使用
        axes[3 + i * 2].plot(df['Timestamp'], df[mem_col], color='tab:red')
        axes[3 + i * 2].set_ylabel(f"{mem_col}\n(MB)", rotation=0, labelpad=40)
        axes[3 + i * 2].grid(True)

    # 设置 x 轴和布局
    plt.xlabel("Time")
    plt.xticks(rotation=45)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    # plt.savefig("./assets/system_usage_plot.png", dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 1:
        filename = args[0]
        if filename.lower().endswith('.csv'):
            CSV_FILENAME = filename
            print(f"📁csv文件路径:{CSV_FILENAME}")
        else:
            print(f"🔔未输入有效的csv文件名称，参考示例：python monitor_to_csv.py ./log/syswatch.csv")
            sys.exit(1)
    else:
        print(f"🔔未输入有效的csv文件名称，默认文件路径:{CSV_FILENAME}")
    plot_data()
