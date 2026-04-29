# Hello World AI Agent

一个用来练手的最小 LangChain Agent 项目。

## 文件

`hello_agent.py`
最小可运行示例，包含模型调用、工具定义和 Agent 执行。

`requirements.txt`
项目依赖。

## 安装

```bash
pip install -r requirements.txt
```

## 配置

这个项目现在默认从环境变量读取配置，不再把 API Key 写死在代码里。

### 1. 官方 OpenAI

`cmd.exe`

```bat
set OPENAI_API_KEY=你的官方 OpenAI Key
set OPENAI_MODEL=gpt-4o-mini
```

`PowerShell`

```powershell
$env:OPENAI_API_KEY="你的官方 OpenAI Key"
$env:OPENAI_MODEL="gpt-4o-mini"
```

### 2. OpenAI 兼容平台

如果你用的不是官方 OpenAI，而是某个兼容 OpenAI 接口的平台，还需要配置：

```bat
set OPENAI_BASE_URL=https://你的服务商地址/v1
set OPENAI_MODEL=服务商提供的模型名
```

## 运行

```bash
python hello_agent.py
```

## 你刚才那个 401 的原因

`invalid_api_key` 表示当前请求发到了某个接口，但这个接口不认可你提供的 key。

你原来的代码有两个问题：

1. 把 key 直接写死在了代码里。
2. 使用了 `ChatOpenAI(...)`，但没有给 `base_url`，所以它会默认请求官方 OpenAI。

这意味着：

- 如果你填的是官方 OpenAI key，就应该直接可用。
- 如果你填的是第三方平台 key，只填 `OPENAI_API_KEY` 不够，还必须同时配 `OPENAI_BASE_URL` 和正确的模型名。

## 后续适合继续练的方向

1. 增加更多工具，比如网页搜索、文件读写、天气查询。
2. 给 Agent 增加对话记忆。
3. 把一次性脚本改成命令行交互模式。
4. 换成你实际想练的 OpenAI 兼容模型平台。
