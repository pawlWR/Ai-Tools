from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import HumanMessage, AIMessage
from django.shortcuts import render
from .utils import DjangoSaver
from langgraph.checkpoint.sqlite import SqliteSaver
import os
from dotenv import load_dotenv
from langgraph.types import Command
from typing import Literal
from .tools import create_product, create_sales_with_items
from langgraph.prebuilt import create_react_agent
import sqlite3
from typing_extensions import TypedDict
load_dotenv()

# Initialize the language model with OpenAI API key
llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=100, openai_api_key=os.getenv("OPENAI_KEY"))

def make_system_prompt(suffix: str) -> str:
    return (
        "You are a helpful AI assistant. Provide a response and specify the next agent."
        f"\n{suffix}"
    )

members = ["product_node", "sales_node"]
# Add FINISH as an option for task completion
options = members + ["FINISH"]

system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    f" following workers: {members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH."
)

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: Literal["product_node", "sales_node"]

def supervisor_node(state: MessagesState) -> Command[Literal["product_node", "sales_node", "__end__"]]:
    messages = [
        {"role": "system", "content": system_prompt},
    ] + state["messages"]
    response = llm.with_structured_output(Router).invoke(messages)
    goto = response["next"]
    print(f"Next Worker: {goto}")
    if goto == "FINISH":
        goto = END
    return Command(goto=goto)

# Define product agent with specific tools and system prompt
product_agent = create_react_agent(
    llm,
    tools=[create_product],
    state_modifier=make_system_prompt("For product list, please return it in an HTML unordered list format.")
)

# Define sales agent with specific tools and system prompt
sales_agent = create_react_agent(
    llm,
    tools=[create_sales_with_items],
    state_modifier=make_system_prompt("When creating sales, also create sales items if the product exists in the database.")
)

# Define nodes for product and sales agents
def product_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    response = product_agent.invoke(state)
    return Command(goto="supervisor",  update={
            "messages": [
                HumanMessage(content=response["messages"][-1].content)
            ]
        },)

def sales_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    response = sales_agent.invoke(state)
    return Command(goto="supervisor", update={
            "messages": [
                HumanMessage(content=response["messages"][-1].content)
            ]
        },)

# Build the state graph connecting all nodes
builder = StateGraph(MessagesState)
builder.add_edge(START, "supervisor")  # Start with supervisor node
builder.add_node("supervisor", supervisor_node)  # Add supervisor node
builder.add_node("product_node", product_node)  # Add product node (correct name)
builder.add_node("sales_node", sales_node)  # Add sales node (correct name)

# Define edges between nodes


conn = sqlite3.connect("db1.sqlite3", check_same_thread=False)
memory = SqliteSaver(conn)
compiled_supervisor = builder.compile(checkpointer=memory)

def test2(request):
    messages = []
    responses = []

    if request.method == "POST":
        user_input = request.POST.get('user_input', '')
        messages.append(HumanMessage(content=user_input))
        config = {"configurable": {"thread_id": 2}, "recursion_limit": 20}
        current_state = {"messages": messages}
        next_state = compiled_supervisor.invoke(current_state, config=config)

        # Accessing AIMessage correctly
        ai_response = next_state["messages"][-1]


        messages.append(ai_response)
        responses.append(ai_response.content)  # Store the AI response content
    return render(request, 'test2.html', {'responses': responses})