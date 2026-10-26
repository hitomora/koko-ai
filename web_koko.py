import streamlit as st
import json
import os
from koko import client, SYSTEM_PROMPT, tools, available_functions

st.set_page_config(page_title="Коко AI", page_icon="🤖", layout="centered", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stButton>button { background-color: #242730; color: #ffffff; border: 1px solid #444; border-radius: 10px; transition: all 0.3s ease; }
    .stButton>button:hover { background-color: #0e1319; color: #ffffff; border: 1px solid #555; transform: translateY(-2px); }
    [data-testid="stSidebar"] .stButton>button { background-color: #0e1319; color: #ffffff; border: 1px solid #242730; border-radius: 10px; text-align: left; justify-content: flex-start; transition: all 0.3s ease; padding-left: 10px; margin-bottom: 5px; }
    [data-testid="stSidebar"] .stButton>button:hover { background-color: #0e1319; color: #ffffff; border: 1px solid #ffffff; padding-left: 15px; }
    [data-testid="stSidebar"] .stButton>button[kind="primary"] { background-color: #0e1319; color: #ffffff; border: 1px solid #242730; border-left: 3px solid #ffffff; font-weight: bold; padding-left: 15px; }
    [data-testid="stChatInput"]:focus-within { border-color: #ffffff !important; box-shadow: 0 0 0 1px #ffffff !important; }
    [data-testid="stChatInput"] > div:focus-within { border-color: #ffffff !important; box-shadow: 0 0 0 1px #ffffff !important; }
    [data-testid="stChatInput"] button { background-color: #0e1319 !important; border: 1px solid #444 !important; }
    [data-testid="stChatInput"] button svg { fill: #ffffff !important; color: #ffffff !important; }
    [data-testid="stChatInput"] button:hover { background-color: #242730 !important; border: 1px solid #666 !important; }
    [data-testid="stChatMessage"] { background-color: transparent !important; padding: 10px 0 !important; border: none !important; }
    [data-testid="stChatMessage"] .stMarkdown p { font-size: 16px !important; line-height: 1.6 !important; }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) .stMarkdown { background-color: #2b313d; color: #ffffff; padding: 12px 18px; border-radius: 18px 18px 18px 0px; margin-left: 5px; max-width: 85%; text-align: left; }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) .stMarkdown { background-color: #1a2027; color: #e0e0e0; padding: 12px 18px; border-radius: 18px 18px 18px 0px; margin-left: 5px; max-width: 85%; text-align: left; }
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

HISTORY_FILE = "chats_history.json"

def save_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.chats, f, ensure_ascii=False, indent=4)

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                loaded_chats = json.load(f)
                if loaded_chats and isinstance(loaded_chats, dict):
                    st.session_state.chats = loaded_chats
                    st.session_state.current_chat = list(loaded_chats.keys())[0]
                    return
        except Exception:
            pass
    st.session_state.chats = {"Чат 1": [{"role": "system", "content": SYSTEM_PROMPT}]}
    st.session_state.current_chat = "Чат 1"

if "chats" not in st.session_state:
    load_history()

with st.sidebar:
    if os.path.exists("koko_avatar.png"):
        st.image("koko_avatar.png", width=90) 
    else:
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=70)
        
    st.markdown("<h2 style='margin-top: -10px;'>Чаты с Коко</h2>", unsafe_allow_html=True)
    
    if st.button("➕ Новый чат", use_container_width=True):
        new_chat_name = f"Чат {len(st.session_state.chats) + 1}"
        st.session_state.chats[new_chat_name] = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.session_state.current_chat = new_chat_name
        save_history()
        st.rerun()

    st.write("Ваши диалоги:")
    
    for chat_name in list(st.session_state.chats.keys()):
        button_type = "primary" if chat_name == st.session_state.current_chat else "secondary"
        
        if st.button(chat_name, key=f"btn_{chat_name}", use_container_width=True, type=button_type):
            st.session_state.current_chat = chat_name
            st.rerun()

    st.markdown("---")
    
    if len(st.session_state.chats) > 1:
        if st.button("🗑️ Удалить текущий чат", use_container_width=True):
            del st.session_state.chats[st.session_state.current_chat]
            st.session_state.current_chat = list(st.session_state.chats.keys())[0]
            save_history()
            st.rerun()
    
    st.caption("Модель: deepseek-v4-flash-0731")

if os.path.exists("koko_avatar.png"):
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image("koko_avatar.png", width=70)
    with col2:
        st.title("Коко AI")
else:
    st.title("🤖 Коко AI")

st.caption("Ваш персональный ассистент (Математика + Поиск)")

current_messages = st.session_state.chats[st.session_state.current_chat]

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("💡 Что ты умеешь?", use_container_width=True):
        st.session_state.quick_prompt = "Коко, расскажи кратко, что ты умеешь?"
with col2:
    if st.button("🧮 Посчитать", use_container_width=True):
        st.session_state.quick_prompt = "Коко, посчитай 15% от 2500"
with col3:
    if st.button("🌐 Найти в сети", use_container_width=True):
        st.session_state.quick_prompt = "Коко, найди последние новости технологий"

for msg in current_messages:
    if msg["role"] != "system" and msg["role"] != "tool":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

prompt = None
if "quick_prompt" in st.session_state and st.session_state.quick_prompt:
    prompt = st.session_state.quick_prompt
    st.session_state.quick_prompt = None
else:
    prompt = st.chat_input("Спросите Коко...")

if prompt:
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    save_history()

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            response = client.chat.completions.create(
                model="deepseek-v4-flash-0731",
                messages=current_messages,
                tools=tools,
                tool_choice="auto"
            )
            response_message = response.choices[0].message
            current_messages.append(response_message.model_dump(exclude_none=True))

            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    function_to_call = available_functions.get(function_name)
                    
                    if function_to_call:
                        function_response = function_to_call(**function_args)
                    else:
                        function_response = "Ошибка: Инструмент не найден"
                    
                    current_messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response)
                    })
                
                stream_response = client.chat.completions.create(
                    model="deepseek-v4-flash-0731",
                    messages=current_messages,
                    stream=True
                )
                
                for chunk in stream_response:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                current_messages.append({"role": "assistant", "content": full_response})
                
            else:
                message_placeholder.markdown(response_message.content)
                current_messages.append({"role": "assistant", "content": response_message.content})
            
            save_history()
                
        except Exception as e:
            st.error(f"Ошибка: {e}")