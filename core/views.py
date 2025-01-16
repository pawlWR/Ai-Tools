from django.shortcuts import render
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing_extensions import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from .models import Product
import sqlite3
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver

# Load environment variables
load_dotenv()

# Define State
class State(TypedDict):
    messages: Annotated[list[BaseMessage], "append"]

# Tool to create product
@tool
def create_product(name: str, price: float) -> str:
    """Create a Product with the given name and price."""
    print('calling this toools,-----------------------------------------------------------')
    product = Product(name=name, price=price)
    product.save()
    return f"Product '{product.name}' created successfully."

# State transition logic


# Chatbot logic
llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=100, openai_api_key=os.getenv("OPENAI_KEY"),)
tools = [create_product]
llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)

def should_continue(state: State):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END


# Invoke model and get AI response
def call_model(state: State):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}



# def chatbot(state: State):
#     # response = llm.invoke(state["messages"])
#     response = llm_with_tools.invoke(state["messages"])
#     return {"messages": state["messages"] + [response]}

# Initialize LLM and tools


# Build the state graph (Corrected order)
graph_builder = StateGraph(State)
# graph_builder.add_node("chatbot", chatbot)  # Chatbot node FIRST
graph_builder.add_node("agent", call_model)   # Agent node THEN
graph_builder.add_node("tools", tool_node)  # Tools node
graph_builder.set_entry_point("agent")   # Set entry AFTER adding nodes
graph_builder.add_conditional_edges("agent", should_continue, ["tools", END])
graph_builder.add_edge("tools", "agent")

# Set up SQLite memory saving
conn = sqlite3.connect("database.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)
graph = graph_builder.compile(checkpointer=memory)

# View handling user input
def test2(request):
    messages = []

    if request.method == "POST":
        user_input = request.POST.get('user_input', '')
        messages.append(HumanMessage(content=user_input))

        current_state = {"messages": messages}
        config = {"configurable": {"thread_id": 2}}

        next_state = graph.invoke(current_state, config=config)
        ai_response = next_state["messages"][-1]

        if isinstance(ai_response, AIMessage):
            messages.append(ai_response)

        responses = [ai_response.content] if isinstance(ai_response, AIMessage) else []
    else:
        responses = []

    return render(request, 'test2.html', {'responses': responses})
