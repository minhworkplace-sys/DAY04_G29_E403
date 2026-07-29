import streamlit as st
import json
from pathlib import Path
import re

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from chat import run_model_tool_loop, trim_history

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
load_lab_env(ROOT)

# Cài đặt giao diện Wide giống trong ảnh
st.set_page_config(page_title="G29 Research Assistant", page_icon="🤖", layout="wide")

# Hiển thị tên Chatbot ở giữa màn hình chính
st.title("🤖 G29 Research Assistant")
st.caption("Trợ lý AI thông minh chuyên nghiên cứu tin tức và thị trường tài chính - Phát triển bởi Nhóm G29")

# ================= SIDEBAR SETTINGS =================
with st.sidebar:
    st.title("⚙️ Agent Settings")
    provider_val = st.selectbox("Provider", ["openrouter", "gemini", "openai", "anthropic"], index=1)
    
    # Nút chuyển đổi nhanh giữa v0 (Ngốc) và v3 (Thông minh) để demo
    version_val = st.selectbox("🧠 Độ thông minh của AI", ["v3 (Bản nâng cấp - Thông minh)", "v0 (Bản gốc - Ngây ngô)"], index=0)
    if "v3" in version_val:
        system_prompt_path = "artifacts/system_prompt_v3.md"
    else:
        system_prompt_path = "artifacts/system_prompt_v0.md"
        
    # Ẩn các mục không cần thiết cho gọn UI
    tools_path = "artifacts/tools.yaml"
    model_override = ""
    
    
    history_window = 5
    max_tool_rounds = 4

    if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# ================= INIT SESSION STATE =================
if "history" not in st.session_state:
    st.session_state.history = []

if "provider_name" not in st.session_state or st.session_state.provider_name != provider_val:
    st.session_state.provider_name = provider_val
    st.session_state.provider = make_provider(provider_val)

# Set model
if model_override:
    st.session_state.provider.default_model = model_override
elif provider_val == "gemini":
    st.session_state.provider.default_model = "gemini-3.5-flash" # Quay lại dùng gemini-3.5-flash mặc định

# Reload tools and prompt dynamically based on sidebar
try:
    tool_declarations = load_tool_declarations(ROOT / tools_path)
    st.session_state.tools = to_openai_tools(tool_declarations)
except Exception as e:
    st.sidebar.error(f"Lỗi tải Tools: {e}")
    st.session_state.tools = []

try:
    st.session_state.system_prompt = (ROOT / system_prompt_path).read_text(encoding="utf-8")
except Exception as e:
    st.sidebar.error(f"Lỗi tải System Prompt: {e}")
    st.session_state.system_prompt = ""

# ================= CHAT INTERFACE =================
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # (Đã ẩn) Không hiển thị chi tiết tool đã gọi trên UI nữa
        # if "tool_events" in msg and msg["tool_events"]:
        #     with st.expander("🛠️ Xem chi tiết các Tool đã gọi"):
        #         st.json(msg["tool_events"])

if user_input := st.chat_input("Nhập câu hỏi hoặc yêu cầu..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Run agent
    with st.chat_message("assistant"):
        with st.spinner("Đang suy nghĩ và xử lý..."):
            messages = [
                {"role": "system", "content": st.session_state.system_prompt},
                *trim_history(st.session_state.history, history_window),
                {"role": "user", "content": user_input},
            ]
            
            try:
                result = run_model_tool_loop(
                    provider=st.session_state.provider,
                    messages=messages,
                    tools=st.session_state.tools,
                    model=None,
                    max_tool_rounds=max_tool_rounds,
                )
                assistant_text = result.get("assistant_text") or ""
                
                # Dọn dẹp các rác text (hallucination) do model bắt chước lịch sử chat
                assistant_text = re.sub(r"I will call the selected tool\(s\)\.?\s*", "", assistant_text)
                assistant_text = re.sub(r"TOOL_CALLS_JSON:.*", "", assistant_text, flags=re.DOTALL)
                assistant_text = re.sub(r"TOOL_RESULTS_JSON:.*", "", assistant_text, flags=re.DOTALL)
                assistant_text = assistant_text.strip()
                
                tool_events = result.get("tool_events", [])
                
                if assistant_text:
                    st.markdown(assistant_text)
                
                # (Đã ẩn) Không hiển thị chi tiết tool đã gọi trên UI nữa
                # if tool_events:
                #     with st.expander("🛠️ Xem chi tiết các Tool đã gọi"):
                #         st.json(tool_events)
                        
                # Update history
                st.session_state.history.append({"role": "user", "content": user_input})
                st.session_state.history.append({
                    "role": "assistant", 
                    "content": assistant_text,
                    "tool_events": tool_events
                })
            except Exception as e:
                st.error(f"Lỗi hệ thống: {str(e)}")
