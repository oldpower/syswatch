### 1. ollama部署

#### 1.1 部署

```bash
sudo apt install curl
curl -fsSL https://ollama.com/install.sh | sh
```
#### 1.2 卸载
- 删除服务
  ```bash
  sudo systemctl stop ollama
  sudo systemctl disable ollama
  sudo rm /etc/systemd/system/ollama.service
  ```

- 删除文件
  ```bash
  sudo rm $(which ollama)
  ```

- 删除模型和用户和组
  ```bash
  sudo rm -r /usr/share/ollama
  sudo userdel ollama
  sudo groupdel ollama
  ```

#### 1.3 重启ollama（方式1）

```bash
# 找到端口，kill掉进程
lsof -i :11434

# 启动ollama
export OLLAMA_HOST=0.0.0.0:11434
nohup /usr/bin/ollama serve &

```

#### 1.4 重启ollama（方式2）
```bash
pass
```

#### 1.5 ollama使用

| 命令 |	作用 |
| - | - |
|ollama serve|启动ollama|
|ollama create|从模型文件创建模型|
|ollama show|显示模型信息|
|ollama run|运行模型|
|ollama pull|从注册表中拉取模型|
|ollama push|将模型推送到注册表|
|ollama list|列出模型|
|ollama ps|列出运行的模型|
|ollama cp|复制模型|
|ollama rm|删除模型|
|ollama help|获取有关任何命令的帮助信息|


### 2. 推理速度

#### 2.1 qwen2:0.5b
```bash
ollama run --verbose qwen2:0.5b
>>> 解释一下量子计算.
0.5b
total duration:       3.375091889s
load duration:        13.914629ms
prompt eval count:    13 token(s)
prompt eval duration: 46.841523ms
prompt eval rate:     277.53 tokens/s
eval count:           235 token(s)
eval duration:        3.313491866s
eval rate:            70.92 tokens/s
```
#### 2.2 qwen2:1.5b

```bash
ollama run --verbose qwen2:1.5b
>>> 解释一下量子计算.
total duration:       9.304656237s
load duration:        13.415656ms
prompt eval count:    13 token(s)
prompt eval duration: 140.391535ms
prompt eval rate:     92.60 tokens/s
eval count:           285 token(s)
eval duration:        9.149579532s
eval rate:            31.15 tokens/s
````
