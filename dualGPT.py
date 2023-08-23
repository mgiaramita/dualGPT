import argparse
import configparser
import openai
import os


MODEL = "gpt-3.5-turbo"
EXIT_STR = "EXIT"

LOGO = """
      _             _  ____ ____ _____ 
   __| |_   _  __ _| |/ ___|  _ \_   _|
  / _` | | | |/ _` | | |  _| |_) || |  
 | (_| | |_| | (_| | | |_| |  __/ | |  
  \__,_|\__,_|\__,_|_|\____|_|    |_|  
                                       
"""

tokens_input = 0
tokens_output = 0


def print_tokens():
    print(f"Tokens In: {tokens_input}, Tokens Out: {tokens_output}\n")


def gen_chat_rsp(message, message_history, role="user", model=MODEL):
    global tokens_input, tokens_output

    # Generate response to message + history
    message_history.append({"role": role, "content": f"{message}"})
    try:
        completion = openai.ChatCompletion.create(model=model, messages=message_history)
        reply = completion.choices[0].message.content

        # Keep track of usage ($$$)
        tokens_input = completion.usage.prompt_tokens
        tokens_output = completion.usage.completion_tokens
    except Exception as e:
        # Response failed, give default (error) response
        reply = "An Error occurred. Please try again."

    # Update message history
    message_history.append({"role": "assistant", "content": f"{reply}"})

    return reply


def run_chat_gpt(model):
    message_history1 = [
        {
            "role": "user",
            "content": "Respond to all questions efficiently and as accurately as possible. You are in a conversaton with a user and another GPT model like yourself. As you converse with the user the other model will look at the answers you are giving and it will add to the conversation. You will see these resopnses in the history as you continue to talk. Feel free to address things said by the other model and to offer corrections to anthing said as needed to maintain the most accurate responses possible.",
        },
        {"role": "assistant", "content": "OK"},
    ]
    message_history2 = [
        {
            "role": "user",
            "content": "You will be taking part in a conversation between a user and another GPT model like yourself. You will be presented with a question or statement from the user and a response from the other model. Your job is to respond as part of the conversation, adding onto the response and giving more content or context as needed. Check for incorrect data in the initial response and offer corrections to the statements.",
        },
        {"role": "assistant", "content": "OK"},
    ]

    print("Chat with two ChatGPTs at the same time.")
    print("Ask anything.")
    while True:
        prompt = input("> ")
        if prompt == EXIT_STR:
            break

        # Send prompt to m1
        rsp_m1 = gen_chat_rsp(prompt, message_history1, model=model)
        print(f"\n :: M1 :: {rsp_m1}")
        print_tokens()

        # Send prompt and m1 answer over to m2 for follow up
        prompt2 = f"{prompt}. {rsp_m1}"
        rsp_m2 = gen_chat_rsp(prompt2, message_history2, model=model)
        print(f"\n :: M2 :: {rsp_m2}")
        print_tokens()

        # Add conversation with m2 into m1's history
        message_history1.extend(message_history2[-2:])


def main():
    # Load dev key, init openai
    config = configparser.ConfigParser()
    config.read("config.ini")
    openai.api_key = config["DEFAULT"]["API_KEY"]

    # Set up and read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", default=MODEL)
    args = parser.parse_args()
    print(f"M: {args.model}")

    print(LOGO)
    run_chat_gpt(args.model)


if __name__ == "__main__":
    main()
