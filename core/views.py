from django.shortcuts import render
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing_extensions import TypedDict, Annotated
from langgraph.graph import StateGraph, END, add_messages,START
from .models import Product, Checkpoint
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from .utils  import DjangoSaver
from django.http import HttpResponse
from .tool import *
from langchain_google_genai import ChatGoogleGenerativeAI
# Load environment variables
load_dotenv()


# Define State
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Tool to create product
# llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=100, openai_api_key=os.getenv("OPENAI_KEY"))
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=100,
    google_api_key=os.getenv("GEMINI_KEY"),
)
tools = [create_product,list_products,update_product,delete_product,bulk_create_products,bulk_delete_products,create_sales,update_sales,delete_sales,create_sales_item,update_sales_item,delete_sales_item,list_sales,list_sales_detailed]
llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)

def should_continue(state: State):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END


# Invoke model and get AI response
def call_model(state: State) -> State:
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}



# Build the state graph (Corrected order)
graph_builder = StateGraph(State)
graph_builder.add_node("agent", call_model)   # Agent node THEN
graph_builder.add_node("tools", tool_node)  # Tools node
graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges("agent", should_continue, ["tools", END])
graph_builder.add_edge("tools", "agent")

# Set up memory saving
django_saver = DjangoSaver()
graph = graph_builder.compile(checkpointer=django_saver)

# View handling user input
def test2(request):
    messages = []
    responses = []

    if request.method == "POST":
        user_input = request.POST.get('user_input', '')
        messages.append(HumanMessage(content=user_input))

        current_state = {"messages": messages}
        config = {"configurable": {"thread_id": 2}}

        # Invoke the graph
        next_state = graph.invoke(current_state, config=config)
        
        # Extract the AI response
        ai_response = next_state["messages"][-1]
        print(ai_response, 'AI Response ***************************************')

        if isinstance(ai_response, AIMessage):
            messages.append(ai_response)
            responses = [ai_response.content]

    return render(request, 'test2.html', {'responses': responses})




def test_check(request):
    checkpoint = Checkpoint.objects.all()
    for c in checkpoint:
        print(c.metadata,'-----------------------------------')
    return HttpResponse(f"Checkpoint: {checkpoint.checkpoint}<br>Metadata: {checkpoint.metadata}")
