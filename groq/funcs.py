import csv
import os
from groq import Groq
import json

# Use the Llama3 70b model
MODEL = "llama3-70b-8192"

# Get the Groq API key and create a Groq client
groq_api_key = os.getenv('GROQ_API_KEY')
client = Groq(
  api_key=groq_api_key
)

# NOT BEING CALLED as of 20-Jul-2024
def chat_with_groq(client, prompt, model, response_format):
  completion = client.chat.completions.create(
      model=model,
      messages=[
          {
              "role": "user",
              "content": prompt
          }
      ],
      response_format=response_format
  )

  return completion.choices[0].message.content

def run_conversation(user_prompt):
    # Step 1: send the conversation and available functions to the model
    messages=[
        {
            "role": "system",
            "content": "You are tasked with answer queries about an inventory database for a coffeehouse stored in a CSV file."
        },
        {
            "role": "user",
            "content": user_prompt,
        }
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "read_all",
                "description": "Get the whole inventory file as a CSV file.",
            },
        }
    ]
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=4096
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "read_all": read_all,
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                #team_name=function_args.get("team_name")
                # TODO Write generic way to pass whatever arguments came from Groq
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        #return function_response
        second_response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )  # get a new response from the model where it can see the function response
        return second_response.choices[0].message.content
'''
def readall() -> dict:
    # result maps name to row dict
    result = {}
    with open('inventory.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        #print(reader.fieldnames)
        for row in reader:
            name = row['Description']
            result[name] = row
    return result

def read_item(item_name) -> dict:
    return readall()[item_name]

got = readall()
print(got)

#print(read_item('towel'))
'''

def read_all() -> str:
    """Read the whole inventory file and return it as a string."""
    return open('inventory.csv').read()

#while True:
for _ in range(1):
    #user_prompt = input("Ask: ")
    user_prompt = 'How many towels do we have?'
    if len(user_prompt) == 0:
        break
    print(run_conversation(user_prompt))


