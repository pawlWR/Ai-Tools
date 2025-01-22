from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import HumanMessage, AIMessage
from django.shortcuts import render
from .utils import DjangoSaver
from langgraph.checkpoint.sqlite import SqliteSaver
import os
from dotenv import load_dotenv
from langgraph.types import Command
from typing import Literal, Union
# from .tools import  create_sales_with_items 
from langgraph.prebuilt import create_react_agent
import sqlite3
from typing_extensions import TypedDict
from core.tools.products import *
from core.tools.sales import *
from core.prompts.products import make_product_prompt
from core.prompts.sales import make_system_prompt

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=100, openai_api_key=os.getenv("OPENAI_KEY"))

def make_system_prompt(suffix: str) -> str:
    return (
        "You are a helpful AI assistant. Provide a response and specify the next agent."
        f"\n{suffix}"
    )

members = ["product_node", "sales_node", "general_node"]
options = members + ["FINISH"]

system_prompt = (
    "You are a supervisor tasked with routing conversations. "
    "If the question is about products, route to 'product_node'. "
    "If the question is about sales, route to 'sales_node'. "
    "For general queries or normal conversation, route to 'general_node'. "
    "When the conversation is complete, respond with 'FINISH'."
)

class Router(TypedDict):
    """Worker to route to next."""
    next: Literal["product_node", "sales_node", "general_node", "FINISH"]

def supervisor_node(state: MessagesState) -> Command[Literal["product_node", "sales_node", "general_node", "__end__"]]:
    messages = [
        {"role": "system", "content": system_prompt},
    ] + state["messages"]
    response = llm.with_structured_output(Router).invoke(messages)
    goto = response["next"]
    print(f"Next Worker: {goto}")
    if goto == "FINISH":
        goto = END
    return Command(goto=goto)

# Define general response agent for normal conversation
def general_node(state: MessagesState) -> Command[Literal["__end__"]]:
    messages = state["messages"]
    response = llm.invoke(messages)
    return Command(
        goto=END,
        update={
            "messages": state["messages"] + [AIMessage(content=response.content)]
        }
    )

# Product and sales agents remain the same
product_agent = create_react_agent(
    llm,
    tools = [
        list_products,
        create_product,
        update_product,
        delete_product,
        bulk_create_products,
        bulk_delete_products,
    ],

    state_modifier=make_product_prompt("")
)

sales_agent = create_react_agent(
    llm,
    tools = [
        create_sales,
        update_sales,
        delete_sales,
        create_sales_item,
        update_sales_item,
        delete_sales_item,
        list_sales,
        list_sales_detailed,
    ],

    state_modifier=make_system_prompt("")
)

def product_node(state: MessagesState) -> Command[Literal["__end__"]]:
    response = product_agent.invoke(state)
    return Command(
        goto=END,
        update={
            "messages": state["messages"] + [AIMessage(content=response["messages"][-1].content)]
        }
    )

def sales_node(state: MessagesState) -> Command[Literal["__end__"]]:
    response = sales_agent.invoke(state)
    return Command(
        goto=END,
        update={
            "messages": state["messages"] + [AIMessage(content=response["messages"][-1].content)]
        }
    )

# Build the optimized state graph
builder = StateGraph(MessagesState)

# Add all nodes
builder.add_node("supervisor", supervisor_node)
builder.add_node("product_node", product_node)
builder.add_node("sales_node", sales_node)
builder.add_node("general_node", general_node)

# Define edges
builder.add_edge(START, "supervisor")

# Connect to database
conn = sqlite3.connect("db1.sqlite3", check_same_thread=False)
memory = SqliteSaver(conn)
compiled_supervisor = builder.compile(checkpointer=memory)

def test2(request):
    messages = []
    responses = []

    if request.method == "POST":
        user_input = request.POST.get('user_input', '')
        messages.append(HumanMessage(content=user_input))
        config = {"configurable": {"thread_id": 2}, "recursion_limit": 10}  # Reduced recursion limit
        current_state = {"messages": messages}
        next_state = compiled_supervisor.invoke(current_state, config=config)

        ai_response = next_state["messages"][-1]
        messages.append(ai_response)
        responses.append(ai_response.content)

    return render(request, 'test2.html', {'responses': responses})