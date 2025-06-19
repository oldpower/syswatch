import psutil
import GPUtil
import time
import csv
import os
import sys

# CSV 文件名
CSV_FILENAME = "./log/system_monitor_log.csv"
if os.path.exists(CSV_FILENAME):
    os.remove(CSV_FILENAME)
# 获取所有 GPU 当前状态
def get_gpu_data():
    gpus = GPUtil.getGPUs()
    if not gpus:
        return [], []

    gpu_loads = [round(gpu.load * 100, 2) for gpu in gpus]       # GPU 负载 (%)
    gpu_mems = [gpu.memoryUsed for gpu in gpus]                  # 显存使用 (MB)

    return gpu_loads, gpu_mems

# 初始化 CSV 文件
def init_csv(num_gpus=8):
    if not os.path.exists(CSV_FILENAME):
        with open(CSV_FILENAME, mode='w', newline='') as f:
            writer = csv.writer(f)

            # 表头：时间戳 + CPU + MEM + 每个 GPU 的负载和显存
            header = ['Timestamp', 'CPU (%)', 'Memory (%)']
            for i in range(num_gpus):
                header.append(f'GPU{i+1} Load (%)')
            for i in range(num_gpus):
                header.append(f'GPU{i+1} Memory Used (MB)')
            
            writer.writerow(header)

# 写入 CSV 数据
def log_to_csv(timestamp, cpu, mem, gpu_loads, gpu_mems):
    with open(CSV_FILENAME, mode='a', newline='') as f:
        writer = csv.writer(f)
        row = [timestamp, cpu, mem] + list(gpu_loads) + list(gpu_mems)
        writer.writerow(row)

# 主监控函数
def monitor_system(interval=1, num_gpus=8):
    init_csv(num_gpus=num_gpus)
    print("开始监控系统资源使用情况（按 Ctrl+C 停止）...")

    try:
        while True:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=None)

            # 内存使用情况
            mem = psutil.virtual_memory()
            mem_percent = mem.percent

            # GPU 使用情况
            gpu_loads, gpu_mems = get_gpu_data()

            # 如果检测不到 GPU，填充空值
            if len(gpu_loads) < num_gpus:
                missing = num_gpus - len(gpu_loads)
                gpu_loads += [''] * missing
                gpu_mems += [''] * missing

            # 打印日志信息
            log_str = f"[{timestamp}] CPU: {cpu_percent}%, MEM: {mem_percent}%"
            for i in range(num_gpus):
                load = gpu_loads[i] if i < len(gpu_loads) else 'N/A'
                mem_used = gpu_mems[i] if i < len(gpu_mems) else 'N/A'
                log_str += f", GPU{i+1}: Load={load}%, Mem={mem_used} MB"
            print(log_str)

            # 写入 CSV
            log_to_csv(timestamp, cpu_percent, mem_percent, gpu_loads, gpu_mems)

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n监控已停止。CSV 文件保存为:", CSV_FILENAME)

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 1:
        filename = args[0]
        if filename.lower().endswith('.csv'):
            CSV_FILENAME = filename
            print(f"📁csv存放路径:{CSV_FILENAME}")
        else:
            print(f"🔔未输入有效的csv文件名称，参考示例：python monitor_to_csv.py ./log/syswatch.csv")
            sys.exit(1)
    else:
        print(f"🔔未输入有效的csv文件名称，默认存放路径:{CSV_FILENAME}")

    monitor_system(num_gpus=8)
