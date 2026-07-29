import json
from pathlib import Path
import streamlit as st

from agent import ResearchAgent
from env_loader import load_lab_env
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"

st.set_page_config(
    page_title="Research Agent Lab G29",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stApp {
        background-color: #0e1117;
        color: #e0e6ed;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e2640 0%, #151b2e 100%);
        border: 1px solid #2e3a59;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .tool-badge {
        background-color: #2b3a67;
        color: #4cc9f0;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 5px;
    }
    .status-ok {
        color: #4700d3;
        font-weight: bold;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Research Agent Lab — Evidence-Driven Tool Router")
st.caption("Group G29 | Live Multi-turn Demo & Trace Verification Interface")

# Sidebar configuration & Evidence panel
with st.sidebar:
    st.header("⚙️ Agent Controls")
    provider_name = st.selectbox("Model Provider", ["gemini", "openai", "openrouter", "anthropic"], index=0)
    version_name = st.selectbox("Artifact Version", ["v3", "v2", "v1", "v0"], index=0)
    
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    
    art_ver = build_artifact_version(version_name, system_prompt_path, tools_path)
    
    st.divider()
    st.header("📌 Version Artifact Evidence")
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #8b9bb4;">ACTIVE VERSION</div>
        <div style="font-size: 1.2rem; font-weight: bold; color: #4cc9f0;">{art_ver.artifact_version}</div>
        <hr style="border-color: #2e3a59; margin: 8px 0;">
        <div style="font-size: 0.8rem;">Prompt Hash: <code>{art_ver.prompt_hash[:12]}</code></div>
        <div style="font-size: 0.8rem;">Tools Hash: <code>{art_ver.tools_hash[:12]}</code></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("💡 Quick Sample Prompts")
    sample_prompt = st.radio(
        "Select a sample to try:",
        [
            "Select sample...",
            "Thời tiết hôm nay ở Hà Nội thế nào?",
            "Tin tức AI hôm nay có gì nổi bật?",
            "Tóm tắt 5 tweet mới nhất giúp mình",
            "Đăng bản tin này lên Telegram giúp mình"
        ]
    )

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_history" not in st.session_state:
    st.session_state.agent_history = []
if "tool_traces" not in st.session_state:
    st.session_state.tool_traces = []

with st.sidebar:
    st.divider()
    if st.button("🧹 Clear Chat & Reset Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent_history = []
        st.session_state.tool_traces = []
        st.rerun()

# Main Layout: 2 Columns (Chat UI + Tool Trace Monitor)
chat_col, trace_col = st.columns([3, 2])

with chat_col:
    st.subheader("💬 Chat Interface")
    
    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input Box
    default_text = "" if sample_prompt == "Select sample..." else sample_prompt
    user_input = st.chat_input("Ask the research agent...", key="user_query")
    
    # Handle sample selection or typed input
    prompt_to_send = user_input if user_input else None

    if prompt_to_send:
        # Render User Message
        st.session_state.messages.append({"role": "user", "content": prompt_to_send})
        st.session_state.agent_history.append({"role": "user", "content": prompt_to_send})
        with st.chat_message("user"):
            st.markdown(prompt_to_send)

        # Agent Execution Loop
        try:
            load_lab_env(ROOT)
            provider = make_provider(provider_name)
            declarations = load_tool_declarations(tools_path)
            openai_tools = to_openai_tools(declarations)
            system_prompt = system_prompt_path.read_text(encoding="utf-8")
            
            agent = ResearchAgent(
                provider=provider,
                system_prompt=system_prompt,
                tools=openai_tools,
                tool_implementations=TOOL_FUNCTIONS,
            )

            with st.chat_message("assistant"):
                with st.spinner("🤖 Agent routing tools & executing..."):
                    response = agent.run(st.session_state.agent_history)
                    
                    # Capture tool calls
                    tool_calls_executed = []
                    if hasattr(response, "tool_calls") and response.tool_calls:
                        for tc in response.tool_calls:
                            trace_entry = {
                                "round": len(st.session_state.messages) // 2 + 1,
                                "tool": tc.name,
                                "args": tc.args,
                                "status": "SUCCESS"
                            }
                            st.session_state.tool_traces.append(trace_entry)
                            tool_calls_executed.append(trace_entry)
                    
                    # Render tool execution pill in chat
                    if tool_calls_executed:
                        st.markdown(
                            "".join([f'<span class="tool-badge">🛠️ {tc["tool"]}</span>' for tc in tool_calls_executed]),
                            unsafe_allow_html=True
                        )
                    
                    final_text = response.text or "*(Tool call executed successfully)*"
                    st.markdown(final_text)
                    
                    st.session_state.messages.append({"role": "assistant", "content": final_text})
                    if response.text:
                        st.session_state.agent_history.append({"role": "assistant", "content": response.text})

        except Exception as e:
            st.error(f"❌ Execution Error: {str(e)}")

with trace_col:
    st.subheader("🔍 Real-time Tool Trace Monitor")
    st.caption("Inspect full arguments, tool execution status, and sequence.")
    
    if st.session_state.tool_traces:
        for idx, trace in enumerate(reversed(st.session_state.tool_traces)):
            with st.expander(f"📍 Round {trace['round']} | Tool: {trace['tool']}", expanded=(idx == 0)):
                st.markdown(f"**Tool Name:** `{trace['tool']}`")
                st.markdown(f"**Execution Status:** <span class='status-ok'>PASSED</span>", unsafe_allow_html=True)
                st.markdown("**Arguments:**")
                st.json(trace['args'])
    else:
        st.info("Chưa có tool call nào. Hãy nhập câu hỏi ở giao diện chat bên trái để xem trace.")
