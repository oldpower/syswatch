import requests
import json
import time
from multiprocessing import Pool

def unstreamfunc(modelname):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": modelname,
            "prompt": "解释一下量子计算.",
            "stream": False
        }
    )
    # print(response.json()["response"])
    timeconsuming(response.json())

def streamfunc(modelname):

    start_time = time.time()  # 记录开始时间
    total_tokens = 0          # 累计生成的 Token 数

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": modelname,
            "messages": [
                {"role": "user", "content": "介绍一下量子计算."},
            ],
            "stream": True
        },
        stream=True
    )

    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode('utf-8'))
            # print(data)
            # print(data.get("message", {}).get("content", ""), end="", flush=True)

            # 累计 Token 数量（eval_count 是当前分块的 Token 数）
            if "eval_count" in data:
                total_tokens += data["eval_count"]
                elapsed_time = time.time() - start_time
                current_speed = total_tokens / elapsed_time  # 实时速度
                print(f"[实时速度: {current_speed:.2f} Tokens/秒]", end="\r")  # 动态显示

    # 最终统计
    total_time = time.time() - start_time
    print()
    # print(f"\n\n=== 生成结束 ===")
    # print(f"总生成 Token 数: {total_tokens}")
    # print(f"总耗时: {total_time:.2f} 秒")
    print(f"生成平均速度: {total_tokens / total_time:.2f} Tokens/秒")

def timeconsuming(response):
    # 提取关键字段
    eval_count = response["eval_count"]
    eval_duration_ns = response["eval_duration"]
    prompt_eval_count = response["prompt_eval_count"]
    prompt_duration_ns = response["prompt_eval_duration"]

    # 计算速度
    gen_speed = eval_count / (eval_duration_ns * 1e-9)
    prompt_speed = prompt_eval_count / (prompt_duration_ns * 1e-9)

    print(f"🛸生成平均速度: {gen_speed:.2f} Tokens/秒")
    # print(f"Prompt 处理速度: {prompt_speed:.2f} Tokens/秒")

# streamfunc()

if __name__ == "__main__":
    modelnames = ["qwen2:0.5b","qwen3:0.6b","qwen3:1.7b"]

    modelname = modelnames[2]
    print(f"🚀modelname is {modelname}")
    # print("👇非流:")
    # unstreamfunc(modelname=modelname)
    # print()
    # print("👇流式:")
    # streamfunc(modelname=modelname)

    num_processes = 4 
    print(f"num_processes is {num_processes}")
    with Pool(processes=num_processes) as pool:
        # 使用相同的模型名创建参数列表
        pool.map(streamfunc, [modelname]*num_processes)
