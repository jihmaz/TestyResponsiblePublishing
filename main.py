import openai
import os
import sys
from replit import db
import time
from aiogram import Bot, Dispatcher, executor, types

openai.api_key = os.environ['OPENAI_API_KEY']
if openai.api_key == "":
  sys.stderr.write("""
  You haven't set up your API key yet.

  If you don't have an API key yet, visit:

  https://platform.openai.com/signup

  1. Make an account or sign in
  2. Click "View API Keys" from the top right menu.
  3. Click "Create new secret key"

  Then, open the Secrets Tool and add OPENAI_API_KEY as a secret.
  """)
  exit(1)

from openai import OpenAI

client = OpenAI()
doctors = client.files.create(file=open("Doctors.pdf", "rb"),
                              purpose="assistants")


#Create a message to send a message to the assistant and obtain the response
def send_message(message, thread_id):
  thread_message = client.beta.threads.messages.create(thread_id,
                                                       role="user",
                                                       content=message)
  #3- create a run for the thread
  run = client.beta.threads.runs.create(thread_id=thread.id,
                                        assistant_id=db["assistant_id"])
  re_run = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                             run_id=run.id)

  while re_run.status != "completed":
    time.sleep(0.5)
    print(re_run.status)
    re_run = client.beta.threads.runs.retrieve(thread_id=thread.id,
                                               run_id=run.id)
  run_steps = client.beta.threads.runs.steps.list(thread_id=thread.id,
                                                  run_id=run.id)

  message_id = run_steps.data[0].step_details.message_creation.message_id
  message = client.beta.threads.messages.retrieve(
      message_id=message_id,
      thread_id=thread_id,
  )
  print(message.content[0].text.value)
  message_content = message.content[0].text.value
  return message_content


if __name__ == "__main__":
  #if the assistant is not already created, creat one
  if 'assistant_id' not in db:
    my_assistant = client.beta.assistants.create(
        instructions=
        "You will answer user questions using the files uploaded, or create and run python code to answer if needed",
        name="Math Tutor",
        tools=[{
            "type": "code_interpreter"
        }, {
            "type": "retrieval"
        }],
        model="gpt-3.5-turbo-1106",
        file_ids=[doctors.id])
    #store the assitant id in the db
    db["assistant_id"] = my_assistant.id

  #1 - create a new thread
  thread = client.beta.threads.create()

  #retrieving the assistant id
  my_assistant = client.beta.assistants.retrieve(db["assistant_id"])

  #2- create a message and add it to the created thread
  thread_message = client.beta.threads.messages.create(thread.id,
                                                       role="user",
                                                       content="Hi")
  print(thread_message)

  user_msg = None
  while user_msg != "(exit)":
    user_msg = input("You: ")
    if user_msg == "(exit)":
      print("Thank you, hope to see you soon!")
      sys.exit()
      break
    #4- send the message to the assistant
    assistant_msg = send_message(user_msg, thread.id)
    print("Assistant: ", assistant_msg)
