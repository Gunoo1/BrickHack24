import io
import os
from errno import ECHILD
import re
import streamlit as st
from langchain_core.messages import AIMessage
import speech_recognition as sr
from flask import Flask, render_template, request, jsonify, send_from_directory, abort
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from pydub import AudioSegment
from prompt import INSTRUCTIONS
from typing import Annotated, TypedDict
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.prebuilt import tools_condition
from tools import TOOLS
from environ import secrets
from io import BytesIO

import av
import asyncio
from st_audiorec import st_audiorec
import matplotlib.pyplot as plt

def render_latex(formula, fontsize=12, dpi=300):
    """Renders LaTeX formula into Streamlit."""
    fig = plt.figure()
    text = fig.text(0, 0, '%s' % formula, fontsize=fontsize)
    fig.savefig(BytesIO(), dpi=dpi)  # triggers rendering

    bbox = text.get_window_extent()
    width, height = bbox.size / float(dpi) + 0.05
    fig.set_size_inches((width, height))

    dy = (bbox.ymin / float(dpi)) / height
    text.set_position((0, -dy))

    buffer = BytesIO()
    fig.savefig(buffer, dpi=dpi, format='jpg')
    plt.close(fig)

    st.image(buffer)

#Define your own environment secrets



secrets()

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: MessagesState, config: RunnableConfig):

        while True:

            state = {**state}
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                    not result.content
                    or isinstance(result.content, list)
                    and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}



tool_node = ToolNode(TOOLS)


llm = ChatOpenAI(model="gpt-4o", temperature=.7, api_key = os.environ["OPENAI_API_KEY"])

model = INSTRUCTIONS | llm.bind_tools(TOOLS)

workflow = StateGraph(MessagesState)
workflow.add_node("agent", Assistant(model))
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    tools_condition,
)
workflow.add_edge("tools", "agent")

agent = workflow.compile()
printed_messages = set()


st.markdown("""
    <style>


    /* Target the text input area */
    div[data-testid="stChatInput"] textarea {
        border: 2px solid #888888 !important; /* Grey border for input */
        border-radius: 10px !important;
        outline: none !important; /* Remove focus outline */
        background-color: #1e1e1e; /* Optional: Dark background */
        color: white; /* Text color */
    }

    /* Style the send button */
    div[data-testid="stChatInput"] button {
        border: 2px solid #888888 !important; /* Grey border */
        background-color: #888888 !important; /* Grey background */
        color: black !important; /* Text color */
        border-radius: 50% !important; /* Circular button */
    }

    /* Remove any residual red borders */
    * {
        border-color: #888888 !important;
    }
    </style>
""", unsafe_allow_html=True)
st.title(" 🧱🧑‍🔬 BrickStein")


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if 'printed_messages' not in st.session_state:
    st.session_state.printed_messages = set()


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def render_block_latex(latex_expr):
    print(f"Block latex expression: {latex_expr}")
    st.latex(latex_expr)
    return ""

def reformat_latex(latex_expr):
    # Render block LaTeX
    print(f"Reformat latex expression: {latex_expr}")
    return f"${latex_expr}$"  # Remove the original LaTeX from markdown output

def render_mixed_content(content):

        # Pattern to detect LaTeX expressions inside \( ... \)
    inline_pattern = r'\\\((.*?)\\\)'
    block_pattern = r'\\\[.(.*?).\\\]'

    # First handle block LaTeX expressions
    content = re.sub(block_pattern, lambda m: reformat_latex(m.group(1)), content, flags=re.DOTALL)

    # Then handle inline LaTeX expressions
    content = re.sub(inline_pattern, lambda m: reformat_latex(m.group(1)), content)
    st.write(content)

recognizer = sr.Recognizer()
wav_audio_data = st_audiorec()

if wav_audio_data is not None:
    audio_file = io.BytesIO(wav_audio_data)
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)

    #st.audio(wav_audio_data, format='audio/wav')
    text = recognizer.recognize_google(audio_data)
    if text:
        st.session_state.messages.append({"role": "user", "content": text})

        # Display user message in chat message container
        with st.chat_message("user"):
            render_mixed_content(r"{}".format(text))

        # Prepare the messages for the assistant model
        messages = st.session_state.messages

        try:
            # Construct messages for the assistant model
            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]

            # Invoke the assistant model
            final_state = agent.invoke({"messages": messages})

            # Extract the assistant's response from final_state
            assistant_response = final_state.get("messages")

            if assistant_response:
                # Get the latest AI message
                if isinstance(assistant_response, list):
                    assistant_response = assistant_response[-1]  # Get the last message

                # Check if the response is an AIMessage
                if isinstance(assistant_response, AIMessage):
                    msg_repr = assistant_response.content  # Access the content of the AIMessage

                    # Append only the content to the session state
                    st.session_state.messages.append({"role": "assistant", "content": msg_repr})

                else:
                    msg_repr = "No valid AI message found."
            else:
                msg_repr = "No messages received."

            # Truncate if necessary
            if len(msg_repr) > 2000:
                msg_repr = msg_repr[:2000] + " ... (truncated)"

            with st.chat_message("assistant"):
                render_mixed_content(r"{}".format(msg_repr))


        except Exception as e:
            st.write(f"Error invoking the model: {e}")
st.markdown("""
    <style>
    .sticky-button-container {
        position: fixed;
        bottom: 20px;
        width: 100%;
        background-color: rgba(255, 255, 255, 0.8);
        padding: 10px;
        box-shadow: 0px -2px 5px rgba(0,0,0,0.1);
        text-align: center;
        z-index: 9999;
    }
    </style>
""", unsafe_allow_html=True)
st.markdown('<div class="sticky-button-container">', unsafe_allow_html=True)

if st.button("📸 Take Screenshot"):
    st.session_state.messages.append({"role": "user", "content": "Take a screenshot of the users screen and use tool take_screenshot"})
    st.write("📸✨Screenshot taken successfully!")
    try:
        # Construct messages for the assistant model
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        # Invoke the assistant model
        final_state = agent.invoke({"messages": messages})

        # Extract the assistant's response from final_state
        assistant_response = final_state.get("messages")
        if assistant_response:
            # Get the latest AI message
            if isinstance(assistant_response, list):
                assistant_response = assistant_response[-1]  # Get the last message

            # Check if the response is an AIMessage
            if isinstance(assistant_response, AIMessage):
                msg_repr = assistant_response.content  # Access the content of the AIMessage
                # Append only the content to the session state
                st.session_state.messages.append({"role": "assistant", "content": msg_repr})
            else:
                msg_repr = "No valid AI message found."
        else:
            msg_repr = "No messages received."

        # Truncate if necessary
        if len(msg_repr) > 2000:
            msg_repr = msg_repr[:2000] + " ... (truncated)"

        with st.chat_message("assistant"):
            print(msg_repr)
            render_mixed_content(r"{}".format(msg_repr))


    except Exception as e:
        st.write(f"Error invoking the model: {e}")


# Accept user input
if prompt := st.chat_input("Enter input"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        render_mixed_content(r"{}".format(prompt))

    # Prepare the messages for the assistant model
    messages = st.session_state.messages

    try:
        # Construct messages for the assistant model
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        # Invoke the assistant model
        final_state = agent.invoke({"messages": messages})

        # Extract the assistant's response from final_state
        assistant_response = final_state.get("messages")

        if assistant_response:
            # Get the latest AI message
            if isinstance(assistant_response, list):
                assistant_response = assistant_response[-1]  # Get the last message

            # Check if the response is an AIMessage
            if isinstance(assistant_response, AIMessage):
                msg_repr = assistant_response.content  # Access the content of the AIMessage
                # Append only the content to the session state
                st.session_state.messages.append({"role": "assistant", "content": msg_repr})
            else:
                msg_repr = "No valid AI message found."
        else:
            msg_repr = "No messages received."

        # Truncate if necessary
        if len(msg_repr) > 2000:
            msg_repr = msg_repr[:2000] + " ... (truncated)"

        with st.chat_message("assistant"):
            print(msg_repr)
            render_mixed_content(r"{}".format(msg_repr))


    except Exception as e:
        st.write(f"Error invoking the model: {e}")

