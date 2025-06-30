import requests
import json
import time
from multiprocessing import Pool
from openai import OpenAI

def unstreamfunc(modelname):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": modelname,
            "prompt": "简单解释一下量子计算.",
            "stream": False
        }
    )
    # print(response.json()["response"])
    timeconsuming(response.json())

def stream_completion(model_name):
    """
    调用 vLLM 的流式 Completion 接口，并统计 token 生成速度。
    
    参数:
        model_name (str): 模型名称
        prompt_text (str): 输入的提示词
        max_tokens (int): 最多生成 token 数
    """
    client = OpenAI(base_url="http://192.168.103.203:11435/v1", api_key="token-abc123")
    start_time = time.time()
    total_tokens = 0
    prompt_text = "详细介绍一下量子计算."
    stream = client.completions.create(
        model=model_name,
        prompt=prompt_text,
        stream=True,
        max_tokens=2048
    )

    try:
        for chunk in stream:
            text = chunk.choices[0].text
            tokens = len(text.split())  # 粗略估计 token 数（可替换为 tokenizer）
            total_tokens += tokens

            elapsed_time = time.time() - start_time
            speed = total_tokens / elapsed_time if elapsed_time > 0 else 0
            # print(text, end="", flush=True)
            # print(f"\r[实时速度: {speed:.2f} Tokens/秒]", end="")
            # time.sleep(0.1)

        total_time = time.time() - start_time
        avg_speed = total_tokens / total_time if total_time > 0 else 0
        # print("\n\n=== 生成结束 ===")
        # print(f"总生成 Token 数: {total_tokens}")
        # print(f"总耗时: {total_time:.2f} 秒")
        print(f"平均速度: {avg_speed:.2f} Tokens/秒")

    except Exception as e:
        print("\n[错误] 流式读取过程中发生异常:", str(e))


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
    modelnames = ["Qwen/Qwen3-1.7B","Qwen/Qwen3-1.7B-FP8",
                  "Qwen/Qwen3-4B","Qwen/Qwen3-4B-AWQ",
                  "Qwen/Qwen3-8B","Qwen/Qwen3-8B-AWQ",
                  "Qwen/Qwen3-14B","Qwen/Qwen3-14B-AWQ",
                  "qwen3:4b"  ,"qwen3:4b-fp16"  ,
                  "qwen3:8b",
                  "qwen3:14b"]

    modelname = modelnames[5]
    # stream_completion(modelname)
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
        pool.map(stream_completion, [modelname]*num_processes)
