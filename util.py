import psutil
import GPUtil
import time
import csv
import os
import matplotlib.pyplot as plt
from collections import deque
import threading
from matplotlib.animation import FuncAnimation

# ================== 配置参数 ==================
CSV_FILENAME = "system_monitor_log.csv"
MAX_HISTORY = 50  # 最多保存的历史数据点数
UPDATE_INTERVAL = 2  # 单位：秒

# 初始化历史数据队列
history_len = MAX_HISTORY

cpu_history = deque(maxlen=history_len)
mem_history = deque(maxlen=history_len)
gpu_load_history = deque(maxlen=history_len)
gpu_mem_history = deque(maxlen=history_len)
time_history = deque(maxlen=history_len)

# ================== 数据记录到 CSV ==================
def init_csv():
    if not os.path.exists(CSV_FILENAME):
        with open(CSV_FILENAME, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'CPU (%)', 'Memory (%)', 'GPU Load (%)', 'GPU Memory Used (MB)'])

def log_to_csv(timestamp, cpu, mem, gpu_load, gpu_mem):
    with open(CSV_FILENAME, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, cpu, mem, gpu_load, gpu_mem])

# ================== 绘图函数 ==================
def update_plot():
    plt.cla()
    plt.title("System Usage Over Time")
    plt.xlabel("Time")
    plt.grid(True)

    if len(cpu_history) > 0:
        plt.plot(time_history, cpu_history, label="CPU (%)", marker='o')
    if len(mem_history) > 0:
        plt.plot(time_history, mem_history, label="Memory (%)", marker='s')
    if len(gpu_load_history) > 0:
        plt.plot(time_history, gpu_load_history, label="GPU Load (%)", marker='^')
    if len(gpu_mem_history) > 0:
        plt.plot(time_history, gpu_mem_history, label="GPU Mem (MB)", marker='x')

    plt.legend()
    plt.tight_layout()

# ================== 实时绘图 ==================
def real_time_plot():
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.ion()  # 启用交互模式，避免阻塞主线程

    def update(frame):
        ax.clear()
        ax.set_title("System Usage Over Time")
        ax.set_xlabel("Time")
        ax.grid(True)

        has_data = False

        if len(cpu_history) > 0:
            ax.plot(time_history, cpu_history, label="CPU (%)", marker='o')
            has_data = True
        if len(mem_history) > 0:
            ax.plot(time_history, mem_history, label="Memory (%)", marker='s')
            has_data = True
        if len(gpu_load_history) > 0 and gpu_load_history[-1] is not None:
            ax.plot(time_history, gpu_load_history, label="GPU Load (%)", marker='^')
            has_data = True
        if len(gpu_mem_history) > 0 and gpu_mem_history[-1] is not None:
            ax.plot(time_history, gpu_mem_history, label="GPU Mem (MB)", marker='x')
            has_data = True

        if has_data:
            ax.legend()

    ani = FuncAnimation(fig, update, interval=UPDATE_INTERVAL * 1000, cache_frame_data=False)
    plt.show(block=False)  # 不阻塞主线程

# ================== 系统监控主函数 ==================
def monitor_system():
    init_csv()
    # real_time_plot()

    try:
        while True:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=None)

            # 内存使用情况
            mem = psutil.virtual_memory()
            mem_percent = mem.percent

            # GPU 使用情况
            gpus = GPUtil.getGPUs()
            if gpus:
                for gpu in gpus:
                    gpu_load = gpu.load * 100
                    gpu_mem_used = gpu.memoryUsed
                    print(f"[{timestamp}] CPU: {cpu_percent}%, MEM: {mem_percent}%, GPU Load: {gpu_load:.1f}%, GPU Mem: {gpu_mem_used} MB")

                    # 添加到历史数据
                    cpu_history.append(cpu_percent)
                    mem_history.append(mem_percent)
                    gpu_load_history.append(gpu_load)
                    gpu_mem_history.append(gpu_mem_used)
                    time_history.append(timestamp[-5:])  # 只保留分钟和秒部分

                    # 记录到 CSV
                    log_to_csv(timestamp, cpu_percent, mem_percent, gpu_load, gpu_mem_used)
            else:
                print(f"[{timestamp}] CPU: {cpu_percent}%, MEM: {mem_percent}%, GPU: N/A")

                # 添加到历史数据（GPU为空）
                cpu_history.append(cpu_percent)
                mem_history.append(mem_percent)
                gpu_load_history.append(None)
                gpu_mem_history.append(None)
                time_history.append(timestamp[-5:])

                # 记录到 CSV（GPU为空）
                log_to_csv(timestamp, cpu_percent, mem_percent, '', '')

            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:
        print("\n监控已停止，绘图将继续显示。关闭窗口以退出程序。")
        plt.ioff()
        plt.show()

if __name__ == "__main__":
    monitor_system()