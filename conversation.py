import json

from openai_api import chat_completion_request
from utils import database_schema_string, execute_function_call

tools = [
    {
        "type": "function",
        "function": {
            "name": "ask_database",
            "description": "Use this function to answer user questions about music. Input should be a fully formed SQL query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": f"""
                                SQL query extracting info to answer the user's question.
                                SQL should be written using this database schema:
                                {database_schema_string}
                                The query should be returned in plain text, not in JSON.
                                """,
                    }
                },
                "required": ["query"],
            },
        }
    }
]


def format_chat_history(chat_history: list[list]) -> list[list]:
    formated_chat_history = []

    for ch in chat_history:
        formated_chat_history.append({
            'role': 'user',
            'content': ch[0]
        })
        if ch[1] == None:
            pass
        else:
            formated_chat_history.append({
                'role': 'assistant',
                'content': ch[1]
            })

    return formated_chat_history


def handle_chat_completion(chat_history: list[list]) -> list[list]:

    query = chat_history[-1][0]

    formated_chat_history = format_chat_history(chat_history)

    chat_response = chat_completion_request(formated_chat_history, tools)
    assistant_message = chat_response["choices"][0]['message']

    if assistant_message['content'] == None:
        '''Call SQL and generate the response.
        '''
        if assistant_message["tool_calls"][0]["function"]["name"] == "ask_database":
            query = json.loads(
                assistant_message["tool_calls"][0]["function"]["arguments"])["query"]
            print(query)
            response = execute_function_call(query)
        if response == '':
            response += 'Empty response'
        print(response)
    else:
        response = assistant_message['content']
        print(response)

    chat_history[-1][1] = response

    return chat_history


def handle_user_query(message: str, chat_history: list[tuple]) -> tuple:
    chat_history += [[message, None]]
    return '', chat_history
