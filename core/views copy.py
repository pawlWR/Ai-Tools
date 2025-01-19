# def test(request):
#     if 'thread_id' not in request.session:
#         thread = Thread.objects.create(title="Chat Session")
#         request.session['thread_id'] = thread.id

#     thread_id = request.session['thread_id']
#     thread = Thread.objects.get(id=thread_id)

#     if request.method == "POST":
#         user_input = request.POST.get('user_input', '')

#         # Load messages from session, converting dicts to messages
#         message_dicts = request.session.get(f"messages_{thread_id}", [])
#         messages = [dict_to_message(msg) for msg in message_dicts]

#         messages.append(HumanMessage(content=user_input))
#         current_state = {"messages": messages}

#         next_state = graph.invoke(current_state)
#         ai_response = next_state["messages"][-1]

#         if isinstance(ai_response, AIMessage):
#             ThreadMessage.objects.create(thread=thread, content=user_input, response=ai_response.content)

#         # Convert messages to dicts before saving to session
#         message_dicts = [message_to_dict(msg) for msg in next_state["messages"]]
#         request.session[f"messages_{thread_id}"] = message_dicts

#         responses = [ai_response.content] if isinstance(ai_response, AIMessage) else []
#     else:
#         # Load messages for initial GET request, converting dicts to messages
#         message_dicts = request.session.get(f"messages_{thread_id}", [])
#         messages = [dict_to_message(msg) for msg in message_dicts]
#         responses = [msg.content for msg in messages if isinstance(msg, AIMessage)]

#     thread_messages = ThreadMessage.objects.filter(thread=thread)
#     return render(request, 'test.html', {'responses': responses, 'thread_messages': thread_messages})