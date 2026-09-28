"""
UI components and helper widgets for LectureLens Streamlit app.
"""

import socket
import streamlit as st
from lecturelens.backends.detect import detect_hardware


def check_internet_connection(host: str = "8.8.8.8", port: int = 53, timeout: float = 1.0) -> bool:
    """Checks if external internet host is reachable."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except (socket.error, Exception):
        return False


def render_sidebar():
    """Renders sidebar device status, offline indicator, and app settings."""
    st.sidebar.title("⚡ LectureLens Copilot")
    st.sidebar.caption("Qualcomm Snapdragon AI Lab Challenge")

    # Offline Guarantee Status Badge
    is_online = check_internet_connection()
    if not is_online:
        st.sidebar.success("🟢 **OFFLINE MODE**\nRunning 100% locally on-device.")
    else:
        st.sidebar.info("🌐 **ONLINE MODE**\nApp makes ZERO cloud requests.")

    st.sidebar.divider()

    # Device & Backend Status Card
    st.sidebar.subheader("Hardware & Acceleration")
    hardware_report = detect_hardware()

    qnn_status = "⚡ Verified NPU (QNN)" if hardware_report["qnn_available"] else "💻 CPU Fallback"
    foundry_status = "⚡ NPU Model" if hardware_report["foundry_available"] else "💻 CPU Model"

    st.sidebar.markdown(f"""
    - **System:** {hardware_report['machine']} ({hardware_report['cpu_count']} Cores)
    - **STT Backend:** {qnn_status}
    - **LLM Engine:** {foundry_status}
    - **Embeddings:** ONNX CPU
    """)

    st.sidebar.divider()

    # Settings Controls
    st.sidebar.subheader("App Settings")
    chunk_len = st.sidebar.slider("Chunk Window (seconds)", 10, 60, 30)
    language = st.sidebar.selectbox("STT Language", ["en", "auto"], index=0)
    num_quiz = st.sidebar.slider("Quiz Questions Count", 3, 10, 5)
    num_cards = st.sidebar.slider("Flashcards Count", 3, 10, 5)

    st.sidebar.divider()

    # Demo Mode Toggle
    demo_mode = st.sidebar.checkbox("🎮 Enable Demo Mode", value=False, help="Load pre-recorded lecture sample for instant offline demo.")

    return {
        "chunk_len": chunk_len,
        "language": language,
        "num_quiz": num_quiz,
        "num_cards": num_cards,
        "demo_mode": demo_mode
    }
