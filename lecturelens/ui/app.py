"""
LectureLens Streamlit Web UI Application.
"""

import os
import sys
import time
from pathlib import Path
import streamlit as st
import numpy as np

# Ensure project root in sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from lecturelens.ui.components import render_sidebar
from lecturelens.pipeline.session import run_full_pipeline, LectureSession
from lecturelens.pipeline.qa import ask_lecture
from lecturelens.storage.store import list_sessions, delete_session, export_markdown, load_session
from lecturelens.storage.exports import export_anki_csv, export_srt, export_plain_transcript, export_study_sheet
from lecturelens.pipeline.search import SearchIndex
from lecturelens.audio.recorder import MicRecorder
from lecturelens.backends.base import BackendUnavailable
from lecturelens.config import config

st.set_page_config(
    page_title="LectureLens - Offline Snapdragon Lecture Copilot",
    page_icon="🎓",
    layout="wide"
)

# Glassmorphism & Visual Styling
st.markdown("""
<style>
    /* Dark Glassmorphism Styling */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    }
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.75) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stMetric {
        background: rgba(30, 41, 59, 0.6) !important;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
    }
    div[data-testid="stExpander"] {
        background: rgba(30, 41, 59, 0.4) !important;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="tab-list"] {
        gap: 8px;
    }
    button[data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 8px 16px !important;
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        transition: all 0.2s ease !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: rgba(99, 102, 241, 0.25) !important;
        border-color: rgba(129, 140, 248, 0.6) !important;
        color: #a5b4fc !important;
    }
</style>
""", unsafe_allow_html=True)

# Page Header
st.title("🎓 LectureLens")
st.caption("Fully Offline Lecture Copilot Accelerated for Snapdragon X Series Laptops")

# Render Sidebar & Get Settings
settings = render_sidebar()

# Initialize Session State Variables
if "current_session" not in st.session_state or st.session_state.current_session is None:
    available_sessions = list_sessions()
    st.session_state.current_session = available_sessions[0] if available_sessions else None
if "recording" not in st.session_state:
    st.session_state.recording = False
if "recorder" not in st.session_state:
    st.session_state.recorder = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

# Navigation Tabs
tab_record, tab_notes, tab_quiz, tab_flashcards, tab_search, tab_ask, tab_perf, tab_history = st.tabs(
    ["🎙️ Record / Upload", "📝 Notes & Summary", "❓ Interactive Quiz", "🎴 Flashcards", "🔍 Semantic Search", "💬 Ask Your Lecture", "📊 Performance", "📁 History"]
)

# --- TAB 1: RECORD / UPLOAD ---
with tab_record:
    st.subheader("Lecture Input & Live Transcription")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 🎙️ Live Microphone Stream")
        lecture_title = st.text_input("Lecture Title", value="Snapdragon Architecture Lecture")

        mic_col1, mic_col2 = st.columns([1, 1])
        with mic_col1:
            if not st.session_state.recording:
                if st.button("🔴 Start Recording", type="primary", use_container_width=True):
                    try:
                        rec = MicRecorder(sample_rate=config.sample_rate)
                        rec.start()
                        st.session_state.recorder = rec
                        st.session_state.recording = True
                        st.rerun()
                    except Exception as err:
                        st.error(f"Could not access microphone: {err}")
            else:
                if st.button("⏹️ Stop Recording & Process", type="secondary", use_container_width=True):
                    rec = st.session_state.recorder
                    if rec:
                        audio_data = rec.stop()
                        st.session_state.recording = False
                        st.session_state.recorder = None

                        if len(audio_data) > 0:
                            with st.spinner("Processing live lecture session on-device..."):
                                session = run_full_pipeline(audio_data, title=lecture_title)
                                st.session_state.current_session = session
                                st.success("Pipeline completed!")
                                st.rerun()

        with mic_col2:
            if st.session_state.recording:
                st.warning("🎙️ Recording in progress...")

        st.divider()
        st.markdown("### 📁 Upload Audio File")
        uploaded_file = st.file_uploader("Upload WAV, MP3, or FLAC lecture file", type=["wav", "mp3", "flac"])
        if uploaded_file is not None:
            if st.button("⚡ Process Uploaded File", type="primary", use_container_width=True):
                temp_path = config.data_dir / f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                progress_bar = st.progress(0.0)
                status_text = st.empty()

                def update_ui_progress(msg, frac):
                    status_text.text(msg)
                    progress_bar.progress(frac)

                with st.spinner("Running full offline pipeline..."):
                    session = run_full_pipeline(temp_path, title=uploaded_file.name, progress_callback=update_ui_progress)
                    st.session_state.current_session = session
                    st.success("Audio processed successfully!")

                if temp_path.exists():
                    temp_path.unlink()

        # Demo mode instant load
        if settings["demo_mode"]:
            st.warning("⚠️ **DEMO MODE ACTIVE** — pre-recorded sample data. Not live inference.")
            st.info("🎮 Demo Mode: Toggle off in sidebar for real microphone capture.")

    with col2:
        st.markdown("### 📜 Real-time Transcript Output")
        curr_session = st.session_state.current_session
        if curr_session:
            st.success(f"**Loaded Session:** {curr_session.metadata.title} (ID: {curr_session.metadata.id[:8]})")
            st.metric("Audio Duration", f"{curr_session.metadata.audio_duration_seconds:.1f} s")
            st.text_area("Full Transcript", value=curr_session.transcript, height=350)
        else:
            st.info("No active lecture loaded yet. Record live audio, upload a file, or toggle Demo Mode in the sidebar.")

# --- TAB 2: NOTES & SUMMARY ---
with tab_notes:
    st.subheader("Lecture Summary & Executive Notes")
    curr_session = st.session_state.current_session
    if not curr_session:
        st.info("Please process a lecture session first under the Record/Upload tab.")
    else:
        st.markdown(f"### 📌 {curr_session.metadata.title}")

        # Metrics Strip
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("STT Backend", f"{curr_session.metadata.stt_backend.get('device', 'CPU')}")
        col_m2.metric("STT RTF", f"{curr_session.timing_metrics.get('stt_rtf', 0.0):.4f}")
        col_m3.metric("LLM Backend", f"{curr_session.metadata.llm_backend.get('device', 'CPU')}")
        col_m4.metric("LLM Speed", f"{curr_session.metadata.llm_backend.get('tokens_per_second', 0.0):.1f} tok/s")

        st.divider()

        col_n1, col_n2 = st.columns([1, 1])

        with col_n1:
            st.markdown("#### 💡 Executive Summary")
            for bullet in curr_session.summary:
                st.markdown(f"• {bullet}")

            st.markdown("#### 🔄 Revision Paragraph")
            st.info(curr_session.revision_paragraph)

        with col_n2:
            st.markdown("#### 🔑 Essential Key Terms")
            for term in curr_session.key_terms:
                with st.expander(f"**{term.term}**"):
                    st.write(term.definition)

# --- TAB 3: INTERACTIVE QUIZ ---
with tab_quiz:
    st.subheader("Interactive Multiple Choice Quiz")
    curr_session = st.session_state.current_session
    if not curr_session or not curr_session.quiz:
        st.info("No quiz questions available for the current lecture.")
    else:
        score = 0
        total_q = len(curr_session.quiz)

        for idx, q in enumerate(curr_session.quiz):
            st.markdown(f"##### Q{idx + 1}. {q.question}")
            user_choice = st.radio(
                f"Options for Q{idx + 1}",
                options=q.options,
                key=f"q_{idx}",
                label_visibility="collapsed"
            )

            check_btn = st.button(f"Check Answer Q{idx + 1}", key=f"btn_q_{idx}")
            if check_btn or f"q_{idx}" in st.session_state.quiz_answers:
                st.session_state.quiz_answers[f"q_{idx}"] = user_choice
                chosen_idx = q.options.index(user_choice) if user_choice in q.options else -1

                if chosen_idx == q.correct_index:
                    st.success(f"✅ Correct! {q.explanation}")
                    score += 1
                else:
                    st.error(f"❌ Incorrect. Correct answer: **{q.options[q.correct_index]}**. Explanation: {q.explanation}")
            st.divider()

# --- TAB 4: FLASHCARDS ---
with tab_flashcards:
    st.subheader("Active Recall Study Flashcards")
    curr_session = st.session_state.current_session
    if not curr_session or not curr_session.flashcards:
        st.info("No flashcards available for the current lecture.")
    else:
        cols = st.columns(2)
        for idx, card in enumerate(curr_session.flashcards):
            with cols[idx % 2]:
                with st.expander(f"🃏 **Card {idx + 1}: {card.question}**"):
                    st.markdown(f"**Answer:** {card.answer}")

# --- TAB 5: SEMANTIC SEARCH ---
with tab_search:
    st.subheader("Cross-Lecture Semantic Search")
    query = st.text_input("Search lecture transcripts & notes (e.g. 'NPU architecture', 'quantization')")
    if query:
        search_idx = SearchIndex()
        results = search_idx.search(query, top_k=5)

        if results:
            st.markdown(f"Found {len(results)} relevant matching passages:")
            for score, passage in results:
                st.markdown(f"#### 📖 {passage['session_title']} (Approx {passage['timestamp_sec']}s) — Similarity Score: {score:.3f}")
                st.write(f"> \"{passage['text']}\"")
                st.divider()
        else:
            st.warning("No relevant passages matched your query.")

# --- TAB 6: ASK YOUR LECTURE ---
with tab_ask:
    st.subheader("💬 Ask Your Lecture — Grounded Q&A")
    st.caption("Answers are generated only from your saved lecture transcripts. Citations link back to timestamps.")
    curr_session = st.session_state.current_session
    if not curr_session:
        st.info("Process a lecture first, then ask questions about it.")
    else:
        ask_query = st.text_input("Ask a question about the lecture", placeholder="What did the professor say about NPUs?")
        if ask_query:
            try:
                from lecturelens.backends import get_llm_backend
                llm_backend = get_llm_backend("auto")
                search_idx = SearchIndex()
                with st.spinner("Searching lecture & generating grounded answer..."):
                    qa_result = ask_lecture(ask_query, search_idx, llm_backend, top_k=4)

                st.markdown("### Answer")
                st.write(qa_result["answer"])

                if qa_result["citations"]:
                    st.markdown("#### 📎 Citations")
                    for c in qa_result["citations"]:
                        with st.expander(f"[{c['citation_num']}] {c['session_title']} @ {c['timestamp_sec']}s"):
                            st.write(c["excerpt"])

                st.caption(f"🔍 Retrieval: {qa_result['retrieval_time_sec']:.3f}s | 🧠 Generation: {qa_result['generation_time_sec']:.3f}s")

            except BackendUnavailable as e:
                st.warning(f"LLM backend not available: {e}\n\nStart Ollama with: `ollama serve` then `ollama pull phi3:mini`")

# --- TAB 7: PERFORMANCE BENCHMARKS ---
with tab_perf:
    st.subheader("Measured CPU vs NPU Performance Diagnostics")
    st.markdown("Real measurements from `scripts/benchmark.py`. Simulated rows are auto-excluded.")

    csv_path = Path("benchmarks/results/latest.csv")
    if csv_path.exists():
        try:
            import pandas as pd
            df = pd.read_csv(csv_path)
            st.dataframe(df)
        except Exception as e:
            st.warning(f"Could not load benchmark CSV: {e}")
    else:
        st.info(
            "No benchmark results yet.\n\n"
            "Run: `python scripts/benchmark.py --quick` to generate real measurements.\n\n"
            "Note: STT/LLM benchmarks require model files (run `python scripts/download_models.py`) "
            "and a local LLM (run `ollama pull phi3:mini`)."
        )


# --- TAB 8: HISTORY & EXPORT ---
with tab_history:
    st.subheader("Saved Lecture Sessions")
    sessions = list_sessions()
    if not sessions:
        st.info("No saved sessions in database directory.")
    else:
        for s in sessions:
            col_h1, col_h2, col_h3 = st.columns([3, 2, 2])
            col_h1.write(f"**{s.metadata.title}**\n({s.metadata.id[:8]})")
            col_h2.write(f"📅 {s.metadata.created_at[:10]}")
            col_h3.write(f"⏱️ {s.metadata.audio_duration_seconds:.1f}s")

            btn_cols = st.columns(5)
            with btn_cols[0]:
                if st.button("📖 Open", key=f"open_{s.metadata.id}"):
                    st.session_state.current_session = s
                    st.rerun()
            with btn_cols[1]:
                if st.button("📄 Study Sheet", key=f"study_{s.metadata.id}"):
                    p = export_study_sheet(s)
                    st.success(f"Saved: {p.name}")
            with btn_cols[2]:
                if st.button("🃏 Anki CSV", key=f"anki_{s.metadata.id}"):
                    p = export_anki_csv(s)
                    st.success(f"Saved: {p.name}")
            with btn_cols[3]:
                if st.button("📜 SRT", key=f"srt_{s.metadata.id}"):
                    p = export_srt(s)
                    st.success(f"Saved: {p.name}")
            with btn_cols[4]:
                if st.button("🗑️ Delete", key=f"del_{s.metadata.id}"):
                    delete_session(s.metadata.id)
                    st.rerun()
            st.divider()
