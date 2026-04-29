"""
Hello World AI Agent

Configure before running:

cmd.exe:
    set OPENAI_API_KEY=your_key
    set OPENAI_MODEL=gpt-4o-mini

PowerShell:
    $env:OPENAI_API_KEY="your_key"
    $env:OPENAI_MODEL="gpt-4o-mini"

If you use an OpenAI-compatible provider instead of the official OpenAI API,
also set OPENAI_BASE_URL and the provider's model name.
"""

from __future__ import annotations

import json
import os
from datetime import datetime

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_core.outputs import ChatResult
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from openai import AuthenticationError


def get_current_time() -> str:
    """Return the current local time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate(expression: str) -> str:
    """Evaluate a basic arithmetic expression."""
    allowed_chars = set("0123456789+-*/().% ")
    if not expression or any(char not in allowed_chars for char in expression):
        return "Only basic arithmetic is allowed, for example: (25 + 15) * 2"

    try:
        result = eval(expression, {"__builtins__": {}}, {})
    except Exception as exc:  # noqa: BLE001
        return f"Calculation error: {exc}"

    return f"{expression} = {result}"


TOOLS = [
    Tool(
        name="get_current_time",
        func=lambda _: get_current_time(),
        description="Return the current local time in YYYY-MM-DD HH:MM:SS format.",
    ),
    Tool(
        name="calculate",
        func=calculate,
        description="Evaluate a basic arithmetic expression such as 2+3*5 or (25+15)*2.",
    ),
]


class CompatibleChatOpenAI(ChatOpenAI):
    """Tolerate some OpenAI-compatible providers that return JSON strings."""

    def _create_chat_result(self, response, generation_info=None) -> ChatResult:
        if isinstance(response, bytes):
            response = response.decode("utf-8", errors="replace")

        if isinstance(response, str):
            try:
                response = json.loads(response)
            except json.JSONDecodeError as exc:
                preview = response[:300].replace("\n", " ")
                raise ValueError(
                    "The provider did not return a standard OpenAI JSON response. "
                    "Check OPENAI_BASE_URL. It should usually be the API root ending in /v1, "
                    "not the full /chat/completions endpoint. "
                    f"Response preview: {preview}"
                ) from exc

        return super()._create_chat_result(response, generation_info)


def build_prompt() -> PromptTemplate:
    template = """Answer the user's question as best you can.
You have access to the following tools:

{tools}

Follow this format exactly:

Question: the user's input question
Thought: think about what to do next
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (the Thought/Action/Action Input/Observation steps can repeat)
Thought: I now know the final answer
Final Answer: answer the user in Chinese

Question: {input}
Thought:{agent_scratchpad}"""
    return PromptTemplate.from_template(template)


def build_llm() -> CompatibleChatOpenAI:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Missing OPENAI_API_KEY.\n"
            "cmd.exe: set OPENAI_API_KEY=your_key\n"
            "PowerShell: $env:OPENAI_API_KEY=\"your_key\"\n"
            "If you use an OpenAI-compatible provider, also set OPENAI_BASE_URL and OPENAI_MODEL."
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    base_url = os.getenv("OPENAI_BASE_URL", "").strip()

    kwargs = {
        "api_key": api_key,
        "model": model,
        "temperature": 0,
    }
    if base_url:
        kwargs["base_url"] = base_url
        # Many OpenAI-compatible providers do not handle LangChain's streaming path well.
        kwargs["disable_streaming"] = True

    return CompatibleChatOpenAI(**kwargs)


def create_agent() -> AgentExecutor:
    prompt = build_prompt()
    llm = build_llm()
    use_compat_mode = bool(os.getenv("OPENAI_BASE_URL", "").strip())
    agent = create_react_agent(
        llm,
        TOOLS,
        prompt,
        stop_sequence=not use_compat_mode,
    )
    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
    )


def main() -> None:
    print("=" * 50)
    print("Hello World AI Agent started")
    print("=" * 50)
    current_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    current_base_url = os.getenv("OPENAI_BASE_URL", "").strip() or "(official OpenAI)"
    print(f"Model: {current_model}")
    print(f"Base URL: {current_base_url}")

    agent = create_agent()
    test_questions = [
        "你好，你是 Agent 吗？",
        "现在几点了？",
        "帮我算一下 (25 + 15) * 2 等于多少？",
    ]

    for question in test_questions:
        print(f"\nUser: {question}")
        print("-" * 40)
        result = agent.invoke({"input": question})
        print(f"\nAgent: {result['output']}")

    print("\n" + "=" * 50)
    print("Demo finished")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(f"\nConfiguration error:\n{exc}")
    except AuthenticationError as exc:
        print("\nAuthentication failed.")
        print("The current OPENAI_API_KEY is invalid, or it does not match OPENAI_BASE_URL.")
        print("If you use the official OpenAI API, set only OPENAI_API_KEY.")
        print("If you use an OpenAI-compatible provider, set OPENAI_API_KEY, OPENAI_BASE_URL, and OPENAI_MODEL together.")
        print(f"Original error: {exc}")
    except Exception as exc:  # noqa: BLE001
        print(f"\nRequest failed: {type(exc).__name__}: {exc}")
