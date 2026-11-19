from ollama import chat
from .tools import TOOLS_REGISTRY
from .config import (
  OLLAMA_MODEL
)
tools = []
for tool in TOOLS_REGISTRY.values():
  tools.append(tool["schema"])

class LlamaChat:
  def get_response(self, messages):
    mess_copy = messages.copy()
    response = chat(
        model=OLLAMA_MODEL,
        messages=mess_copy,
        tools=tools
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
    result = entry["handler"](**arguments)
    mess_copy.append({"role": "tool", "content": result})
    response = chat(
        model=OLLAMA_MODEL,
        messages=mess_copy,
    )

    return response.message.content
