from pydantic import BaseModel
from enum import Enum
from ollama import chat
from servers_manager import build_group
from contextlib import AsyncExitStack
import asyncio

class Roles(Enum):
    SYS = 'system'
    USER = 'user'
    ASS = 'assistant'
    TOOL = 'tool'


class Message(BaseModel):
    role: Roles
    content: str


async def main():

    async with AsyncExitStack() as stack:
        group, tools = await build_group(stack)
        print(f"Loaded tools: {list(group.tools)}")

        messages = []
        while True:
            user_text = input("you> ").strip()
            if user_text in ("/quit", "/exit"):
                break

            messages.append({"role": "user", "content": user_text})

            for _ in range(8):                      # лимит внутреннего цикла
                resp = chat(model="qwen2.5:7b", messages=messages, tools=tools)
                messages.append(resp.message.model_dump())

                if not resp.message.tool_calls:
                    print(f"agent> {resp.message.content}")
                    break

                for call in resp.message.tool_calls:
                    try:
                        result = await group.call_tool(
                            call.function.name, call.function.arguments,
                        )
                        content = "\n".join(
                            b.text for b in result.content if b.type == "text"
                        )
                    except Exception as e:
                        content = f"ERROR: {type(e).__name__}: {e}"

                    messages.append({
                        "role": "tool",
                        "tool_name": call.function.name,
                        "content": content,
                    })
            else:
                print("agent> [превышен лимит вызовов инструментов]")
            # print('='*64)
            # print(*messages, sep='\n', end='\n\n')


if __name__ == '__main__':
    asyncio.run(main())
