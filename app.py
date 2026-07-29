from __future__ import annotations

import json
import sys
from datetime import datetime
from glob import glob
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parent
STARTER_DIR = ROOT / "starter_v0"
if str(STARTER_DIR) not in sys.path:
    sys.path.insert(0, str(STARTER_DIR))

from chat import run_model_tool_loop  # type: ignore
from env_loader import load_lab_env  # type: ignore
from providers import make_provider  # type: ignore
from tools import load_tool_declarations, to_model_tools  # type: ignore


ARTIFACTS_DIR = STARTER_DIR / "artifacts"
TRANSCRIPTS_DIR = STARTER_DIR / "transcripts"
load_lab_env(STARTER_DIR)


def load_system_prompt() -> str:
    return (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")


def load_tools_config() -> list[dict[str, object]]:
    return load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")


def load_transcript_files() -> list[str]:
    return sorted(glob(str(TRANSCRIPTS_DIR / "*.transcript.json")), reverse=True)


st.set_page_config(
    page_title="AI Research Agent Evaluator",
    page_icon="🤖",
    layout="wide",
)

st.markdown(
    """
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .stCard {
        background-color: #1E232A;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363D;
        margin-bottom: 10px;
    }
    .tool-badge {
        background-color: #1F6FEB;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-family: monospace;
        font-weight: bold;
    }
    .status-success { color: #3FB950; font-weight: bold; }
    .status-error { color: #F85149; font-weight: bold; }
</style>
""",
    unsafe_allow_html=True,
)


st.sidebar.title("🛠️ Agent Control Center")

version = st.sidebar.selectbox(
    "Artifact Version",
    options=["v0", "v1", "v2", "v3"],
    index=0,
    help="Chọn phiên bản Prompt/Tools để so sánh hiệu năng.",
)

provider = st.sidebar.selectbox(
    "Model Provider",
    options=["gemini", "openrouter", "anthropic", "openai"],
    index=0,
)

model_override = st.sidebar.text_input("Model Override", value="", help="Để trống để dùng default model của provider.")

st.sidebar.markdown("---")

try:
    system_prompt = load_system_prompt()
    tools_config = load_tools_config()
    st.sidebar.success(f"✅ Loaded Version: **{version}**")
    st.sidebar.caption(f"🔧 Loaded Tools Count: {len(tools_config)}")
except Exception as exc:
    st.sidebar.error(f"❌ Error loading artifacts: {exc}")
    system_prompt = ""
    tools_config = []

st.sidebar.markdown("---")
st.sidebar.info("💡 Tunnel Status: Sẵn sàng chia sẻ demo qua Cloudflare Tunnel.")

st.title("🤖 AI Research Agent Evaluator")
st.caption(f"Active Version: **{version}** | Provider: **{provider}**")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_rounds" not in st.session_state:
    st.session_state.last_rounds = []
if "last_transcript_path" not in st.session_state:
    st.session_state.last_transcript_path = None

col_chat, col_trace = st.columns([5, 5])

with col_chat:
    st.subheader("💬 Live Chat")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("Nhập request nghiên cứu..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Agent đang suy luận và thực thi tools..."):
                try:
                    provider_impl = make_provider(provider)
                    tools = to_model_tools(tools_config)
                    response = run_model_tool_loop(
                        provider=provider_impl,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            *st.session_state.messages,
                        ],
                        tools=tools,
                        model=model_override or None,
                        max_tool_rounds=4,
                    )

                    final_response = response.get("assistant_text", "")
                    rounds = response.get("rounds", [])

                    st.markdown(final_response)
                    st.session_state.messages.append({"role": "assistant", "content": final_response})
                    st.session_state.last_rounds = rounds

                    transcript = {
                        "created_at": datetime.now().isoformat(timespec="seconds"),
                        "provider": provider,
                        "version": version,
                        "model": model_override or getattr(provider_impl, "default_model", None),
                        "messages": st.session_state.messages,
                        "rounds": rounds,
                        "assistant_text": final_response,
                        "status": response.get("status"),
                    }
                    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
                    transcript_path = TRANSCRIPTS_DIR / f"{datetime.now().strftime('%Y%m%dT%H%M%S%f')}.transcript.json"
                    transcript_path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")
                    st.session_state.last_transcript_path = str(transcript_path)

                    st.toast("Thực thi thành công!", icon="✅")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Lỗi thực thi: {exc}")

with col_trace:
    st.subheader("🔍 Tool Execution Trace & Artifacts")

    if not st.session_state.last_rounds:
        st.info("Chưa có Tool Execution Trace nào. Hãy gửi một request ở khung chat bên trái!")
    else:
        st.write(f"**Tổng số rounds thực thi:** `{len(st.session_state.last_rounds)}`")
        for idx, round_data in enumerate(st.session_state.last_rounds, 1):
            title = round_data.get("tool_calls", [{}])[0].get("name", "Tool Event") if round_data.get("tool_calls") else "Tool Event"
            with st.expander(f"📍 Round {idx}: {title}", expanded=True):
                st.write("**Assistant text:**")
                st.write(round_data.get("assistant_text") or "")
                st.write("**Tool Calls:**")
                st.json(round_data.get("tool_calls", []))
                st.write("**Tool Results:**")
                st.json(round_data.get("tool_results", []))

    st.markdown("---")
    st.subheader("📂 Saved Transcripts")
    transcript_files = load_transcript_files()
    if transcript_files:
        selected_file = st.selectbox("Xem nhanh file log transcript gần đây:", transcript_files[:5])
        if selected_file:
            with open(selected_file, "r", encoding="utf-8") as f:
                st.json(json.load(f))
    else:
        st.caption("Chưa có file transcript nào được lưu trong thư mục `starter_v0/transcripts/`.")

