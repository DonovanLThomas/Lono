import json

from ollama import chat, generate
from .tools import TOOLS_REGISTRY
from .config import (
  OLLAMA_KEEP_ALIVE,
  OLLAMA_MODEL,
)
tools = []
for tool in TOOLS_REGISTRY.values():
  tools.append(tool["schema"])

class LlamaChat:
  def warm_up(self):
    generate(
      model=OLLAMA_MODEL,
      prompt="",
      keep_alive=OLLAMA_KEEP_ALIVE,
    )

  def get_response(self, messages):
    mess_copy = messages.copy()
    response = chat(
        model=OLLAMA_MODEL,
        messages=mess_copy,
        tools=tools,
        keep_alive=OLLAMA_KEEP_ALIVE,
    )

    if not response.message.tool_calls:
      return response.message.content
    

    
    tools_util = response.message.tool_calls
    if len(tools_util) != 1:
      raise ValueError(
        f"Expected one tool call, received {len(tools_util)}"
      )

    call = tools_util[0]
    entry = TOOLS_REGISTRY.get(call.function.name)

    if entry is None:
      raise ValueError(
        f"Invalid tool request: name={call.function.name!r}"
      )
    
    arguments = dict(call.function.arguments or {})

    mess_copy.append(response.message.model_dump(exclude_none=True))
    try:
      result = entry["handler"](**arguments)
    except (TypeError, ValueError) as error:
      result = json.dumps(
        {
          "status": "error",
          "message": str(error),
        }
      )

    if entry.get("direct_return", False):
      return result

    mess_copy.append({"role": "tool", "content": result})
    response = chat(
        model=OLLAMA_MODEL,
        messages=mess_copy,
        keep_alive=OLLAMA_KEEP_ALIVE,
    )

    return response.message.content
