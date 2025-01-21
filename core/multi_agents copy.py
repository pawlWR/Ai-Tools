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
from .tools import create_product, create_sales_with_items , list_products
from langgraph.prebuilt import create_react_agent
import sqlite3
from typing_extensions import TypedDict

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=100, openai_api_key=os.getenv("OPENAI_KEY"))

def make_system_prompt(suffix: str) -> str:
    return (
        "You are a helpful AI assistant. Provide a response and specify the next agent."
        f"\n{suffix}"
    )

members = ["product_node", "sales_node", "general_node"]
options = members + ["FINISH"]

# system_prompt = (
#     "You are a supervisor tasked with routing conversations. "
#     "If the question is about products, route to 'product_node'. "
#     "If the question is about sales, route to 'sales_node'. "
#     "For general queries or normal conversation, route to 'general_node'. "
#     "When the conversation is complete, respond with 'FINISH'."
# )

class Router(TypedDict):
    """Worker to route to next."""
    next: Literal["product_node", "sales_node", "general_node", "product_sales_node", "FINISH"]

# Add new product_sales sequence handler
def product_sales_node(state: MessagesState) -> Command[Literal["product_node", "sales_node", "__end__"]]:
    # First phase: Create product
    product_response = product_agent.invoke(state)
    
    # Prepare state for sales creation
    sales_state = {
        "messages": state["messages"] + [AIMessage(content=product_response["messages"][-1].content)]
    }
    
    # Second phase: Create sale
    sales_response = sales_agent.invoke(sales_state)
    
    # Return combined result
    return Command(
        goto=END,
        update={
            "messages": state["messages"] + [
                AIMessage(content=product_response["messages"][-1].content),
                AIMessage(content=sales_response["messages"][-1].content)
            ]
        }
    )

# Modify supervisor_node to recognize product-sales sequences
def supervisor_node(state: MessagesState) -> Command[Literal["product_node", "sales_node", "general_node", "product_sales_node", "__end__"]]:
    system_prompt = """You are a supervisor tasked with routing conversations.
    If the input contains both product creation AND sales creation, route to 'product_sales_node'.
    If the question is only about products, route to 'product_node'.
    If the question is only about sales, route to 'sales_node'.
    For general queries or normal conversation, route to 'general_node'.
    When the conversation is complete, respond with 'FINISH'.
    """
    
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
    tools=[create_product,list_products],
    state_modifier=make_system_prompt("For create product if give multiple name then create multiple product ."
                                      "For product list, please return it in an HTML unordered list format."),
                                      checkpointer=False
)

sales_agent = create_react_agent(
    llm,
    tools=[create_sales_with_items],
    state_modifier=make_system_prompt("For create sales if give multiple name then create multiple sales with item ."
                                      "When creating sales, also create sales items if the product exists in the database."),
    checkpointer=False
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
builder.add_node("product_sales_node", product_sales_node)  # Add the new node

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