from src.chat import LlamaChat
from httpx import ConnectError
from ollama import ResponseError
from .config import SYSTEM_PROMPT, HISTORY_LIMIT
import unittest

def main():
  print("Llama LLM Chat - Type 'exit' to quit.")

  chat = LlamaChat()
  messages = [{"role": "system", "content": SYSTEM_PROMPT}]

  while True:
    user_input = input("\nYou: ")

    if user_input.lower() in ["exit", "quit"]:
      print("\nExiting. Goodbye!")
      break
    
    if user_input.lower() == "/clear":
      messages.clear()
      messages.append({"role": "system", "content": SYSTEM_PROMPT})
      print("\nCleared History")
      continue
    
    try:
      messages.append({"role": "user", "content": user_input})
      response = chat.get_response(messages)
    except ConnectError:
      messages.pop()
      print("There was an error proccessing the message try again")
      continue
    except ResponseError as error:
      messages.pop()
      print(f"{error.status_code}, {error.error}")
      continue
    except ValueError as error:
      messages.pop()
      print(error)
      continue
    else:
      messages.append({"role": "assistant", "content": response})
      print(f"Llama: {response}")
    
    while (len(messages) > HISTORY_LIMIT):
      del messages[1:3]
  

if __name__ == "__main__":
  main()
