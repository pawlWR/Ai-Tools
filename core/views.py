from django.shortcuts import render
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing_extensions import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from .models import Thread, ThreadMessage
import json

load_dotenv()

class State(TypedDict):
    messages: Annotated[list[BaseMessage], "append"]

graph_builder = StateGraph(State)
llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_KEY"))

def chatbot(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile()

def message_to_dict(message: BaseMessage):
    """Converts a BaseMessage to a dictionary."""
    if isinstance(message, HumanMessage):
        return {"type": "human", "content": message.content}
    elif isinstance(message, AIMessage):
        return {"type": "ai", "content": message.content}
    else:  # Handle other message types if needed
        return {"type": "other", "content": str(message)}

def dict_to_message(message_dict):
    """Converts a dictionary back to a BaseMessage."""
    if message_dict["type"] == "human":
        return HumanMessage(content=message_dict["content"])
    elif message_dict["type"] == "ai":
        return AIMessage(content=message_dict["content"])
    else:
        return BaseMessage(content=message_dict["content"])

def test(request):
    if 'thread_id' not in request.session:
        thread = Thread.objects.create(title="Chat Session")
        request.session['thread_id'] = thread.id

    thread_id = request.session['thread_id']
    thread = Thread.objects.get(id=thread_id)

    if request.method == "POST":
        user_input = request.POST.get('user_input', '')

        # Load messages from session, converting dicts to messages
        message_dicts = request.session.get(f"messages_{thread_id}", [])
        messages = [dict_to_message(msg) for msg in message_dicts]

        messages.append(HumanMessage(content=user_input))
        current_state = {"messages": messages}

        next_state = graph.invoke(current_state)
        ai_response = next_state["messages"][-1]

        if isinstance(ai_response, AIMessage):
            ThreadMessage.objects.create(thread=thread, content=user_input, response=ai_response.content)

        # Convert messages to dicts before saving to session
        message_dicts = [message_to_dict(msg) for msg in next_state["messages"]]
        request.session[f"messages_{thread_id}"] = message_dicts

        responses = [ai_response.content] if isinstance(ai_response, AIMessage) else []
    else:
        # Load messages for initial GET request, converting dicts to messages
        message_dicts = request.session.get(f"messages_{thread_id}", [])
        messages = [dict_to_message(msg) for msg in message_dicts]
        responses = [msg.content for msg in messages if isinstance(msg, AIMessage)]

    thread_messages = ThreadMessage.objects.filter(thread=thread)
    return render(request, 'test.html', {'responses': responses, 'thread_messages': thread_messages})