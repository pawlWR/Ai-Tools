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
from langgraph.checkpoint.memory import MemorySaver
from .tool import *
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from django.http import StreamingHttpResponse
import json
# Load environment variables
load_dotenv()


# Define State
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Tool to create product
# llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=100, openai_api_key=os.getenv("OPENAI_KEY"))
# llm = ChatGoogleGenerativeAI(
#     model="gemini-1.5-flash",
#     temperature=0,
#     max_tokens=100,
#     google_api_key=os.getenv("GEMINI_KEY"),
# )

llm =ChatGroq(
    model="llama3-8b-8192",
    temperature=0,
    max_tokens=100,
    max_retries=2,
    groq_api_key=os.getenv("GROQ_KEY"),
)

tools = [create_product,list_products,update_product,delete_product,
        bulk_create_products,bulk_delete_products,
        create_sales,update_sales,delete_sales,create_sales_item,
        update_sales_item,delete_sales_item,list_sales,list_sales_detailed]
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
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=django_saver)

# View handling user input


def test2(request):
    if request.method == "GET" and 'user_input' in request.GET:
        user_input = request.GET.get('user_input', '')
        messages = [HumanMessage(content=user_input)]
        current_state = {"messages": messages}
        config = {"configurable": {"thread_id": 2}}

        def generate():
            for chunk in graph.stream(current_state, config=config):
                if "agent" in chunk and "messages" in chunk["agent"]:
                    messages = chunk["agent"]["messages"]
                    for message in messages:
                        if isinstance(message, AIMessage):
                            yield f"data: {json.dumps({'response': message.content})}\n\n"
            yield "data: {\"response\": \"\"}\n\n"  # Send empty response to close connection

        return StreamingHttpResponse(generate(), content_type='text/event-stream')
    return render(request, 'test2.html')

