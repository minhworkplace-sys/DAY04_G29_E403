import streamlit as st
from agent import ResearchAgent
from env_loader import load_lab_env
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import build_artifact_version
from pathlib import Path
import json

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"

st.set_page_config(page_title="Research Agent Lab v2", layout="wide")

st.title("🤖 Research Agent Lab UI")
st.caption("Group G29 - Interactive Research Agent Demo")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    provider_name = st.selectbox("Provider", ["gemini", "openai", "openrouter", "anthropic"], index=0)
    version_name = st.selectbox("Version", ["v3", "v2", "v1", "v0"], index=0)
    
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    
    art_ver = build_artifact_version(version_name, system_prompt_path, tools_path)
    st.info(f"**Artifact Version:** `{art_ver.artifact_version}`")
    st.text(f"Prompt Hash: {art_ver.prompt_hash[:12]}")
    st.text(f"Tools Hash: {art_ver.tools_hash[:12]}")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_history" not in st.session_state:
    st.session_state.agent_history = []
if "tool_traces" not in st.session_state:
    st.session_state.tool_traces = []

# Clear chat button
if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.messages = []
    st.session_state.agent_history = []
    st.session_state.tool_traces = []
    st.rerun()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if user_input := st.chat_input("Nhập yêu cầu nghiên cứu của bạn..."):
    # Render user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.agent_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Initialize Provider & Agent
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
            with st.spinner("Agent đang xử lý..."):
                response = agent.run(st.session_state.agent_history)
                
                # Check for tool calls / traces
                if hasattr(response, "tool_calls") and response.tool_calls:
                    st.write("🛠️ **Tool Traces:**")
                    for tc in response.tool_calls:
                        st.json({"tool": tc.name, "args": tc.args})
                        st.session_state.tool_traces.append({"tool": tc.name, "args": tc.args})
                
                final_text = response.text or "*(Agent đã thực thi xong tool call)*"
                st.markdown(final_text)
                
                st.session_state.messages.append({"role": "assistant", "content": final_text})
                if response.text:
                    st.session_state.agent_history.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Lỗi thực thi: {str(e)}")

# Display tool traces log in sidebar
with st.sidebar:
    st.divider()
    st.subheader("📜 Live Tool Traces")
    if st.session_state.tool_traces:
        for idx, trace in enumerate(reversed(st.session_state.tool_traces)):
            with st.expander(f"Trace #{len(st.session_state.tool_traces) - idx}: {trace['tool']}"):
                st.json(trace['args'])
    else:
        st.caption("Chưa có tool call nào.")
