import random
import streamlit as st
from docx import Document
from gtts import gTTS
import io
import base64
import re
import time
from datetime import datetime
import zipfile
import tempfile
import os

# ====================== IMPORTANT FOR STREAMLIT CLOUD ======================
# Use relative path for Streamlit Cloud
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Path to your document - use relative path for Streamlit Cloud
DOC_PATH = os.path.join(current_dir, "Law Preparation.docx")

# If file doesn't exist in current directory, try to find it
if not os.path.exists(DOC_PATH):
    # Try to find it in the parent directory or other common locations
    possible_paths = [
        DOC_PATH,
        "Law Preparation.docx",
        "./Law Preparation.docx",
        "../Law Preparation.docx",
        os.path.join(os.getcwd(), "Law Preparation.docx")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            DOC_PATH = path
            break
    else:
        st.error(f"❌ Document not found. Please ensure 'Law Preparation.docx' is in the repository.")
        st.stop()
# ==========================================================================

# Session state initialization
if "cards" not in st.session_state:
    try:
        st.session_state.cards = load_flashcards(DOC_PATH)
    except Exception as e:
        st.error(f"Error loading flashcards: {e}")
        st.session_state.cards = []
        
if "order" not in st.session_state and st.session_state.cards:
    st.session_state.order = list(range(len(st.session_state.cards)))
    random.shuffle(st.session_state.order)
if "index" not in st.session_state:
    st.session_state.index = 0
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# Voice control session state
if 'audio_playing' not in st.session_state:
    st.session_state.audio_playing = None
if 'stop_requested' not in st.session_state:
    st.session_state.stop_requested = False

# Quiz session state
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}
if 'quiz_feedback' not in st.session_state:
    st.session_state.quiz_feedback = {}
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'quiz_cards' not in st.session_state:
    st.session_state.quiz_cards = []
if 'quiz_type' not in st.session_state:
    st.session_state.quiz_type = "Question to Answer"

def load_flashcards(doc_path):
    """
    Reads the Word document and extracts Q&A pairs.
    Expected format:
    Q: Question text
    A: Answer text
    (Blank lines allowed between cards)
    """
    try:
        document = Document(doc_path)
        cards = []
        question = None

        for para in document.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            if text.startswith("Q:"):
                question = text[2:].strip()
            elif text.startswith("A:") and question:
                answer = text[2:].strip()
                cards.append((question, answer))
                question = None
        
        if not cards:
            st.warning("⚠️ No flashcards found in the document. Please check the format.")
            st.info("Expected format: 'Q: Your question' followed by 'A: Your answer' on separate lines.")
        
        return cards
    except Exception as e:
        st.error(f"Error reading document: {e}")
        return []

# 🚫 Remove emojis from text using regex
def remove_emojis(text):
    """Remove all emojis from text using regex"""
    if not text:
        return ""
    # Unicode ranges for emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002500-\U00002BEF"  # Chinese characters and others
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # dingbats
        "\u3030"
        "]+", 
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

# 🔊 Generate audio file from text (without emojis)
def text_to_speech(text, lang="en"):
    """Convert text to speech and return audio bytes"""
    try:
        if not text:
            return None
            
        # Remove emojis from text before converting to speech
        clean_text = remove_emojis(text)
        
        # Clean up extra spaces that might be left after removing emojis
        clean_text = ' '.join(clean_text.split())
        
        # If the text becomes empty after removing emojis, use a fallback
        if not clean_text.strip():
            if lang == "en":
                clean_text = "No text available"
            else:
                clean_text = "لا يوجد نص"
        
        # ================= IMPORTANT FOR STREAMLIT CLOUD =================
        # gTTS requires internet connection, which Streamlit Cloud has
        # But we need to handle potential timeout issues
        tts = gTTS(text=clean_text, lang=lang, slow=False, timeout=10)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes.getvalue()
    except Exception as e:
        st.error(f"Error generating audio: {e}")
        st.info("Note: Audio generation requires internet connection. Please try again.")
        return None

# ⏹️ Stop audio function
def stop_audio():
    """Stop currently playing audio"""
    st.session_state.stop_requested = True
    st.session_state.audio_playing = None

# 🔊 Generate combined audio file (Question followed by Answer)
def generate_combined_audio(question_text, answer_text):
    """Generate audio with Question first, then Answer"""
    try:
        # Generate Question audio
        question_audio = text_to_speech(question_text, lang="en")
        
        # Generate Answer audio
        answer_audio = text_to_speech(answer_text, lang="en")
        
        if question_audio and answer_audio:
            # Combine the audio bytes (simple concatenation)
            combined_bytes = question_audio + answer_audio
            return combined_bytes
        else:
            return None
    except Exception as e:
        st.error(f"Error generating combined audio: {e}")
        return None

# 🎴 Display flashcards with voiceover
def show_flashcards():
    st.title("📚 LLB Preparation Flashcards with Voiceover")
    
    # Show document info
    with st.expander("📄 Document Information", expanded=False):
        st.write(f"**Document:** Law Preparation.docx")
        st.write(f"**Total Cards:** {len(st.session_state.cards)}")
        if st.session_state.cards:
            st.write(f"**Sample Question:** {st.session_state.cards[0][0][:50]}...")
    
    # Global stop button in sidebar
    with st.sidebar:
        if st.session_state.audio_playing:
            st.warning(f"🔊 Currently playing audio")
            if st.button("⏹️ Stop All Audio", type="primary", use_container_width=True):
                stop_audio()
                st.rerun()
        else:
            st.info("No audio currently playing")
    
    if not st.session_state.cards:
        st.warning("No flashcards found. Ensure your document uses Q:/A: lines.")
        st.info("""
        **Expected format:**
        ```
        Q: What is the definition of law?
        A: Law is a system of rules created and enforced through social or governmental institutions.
        
        Q: What is common law?
        A: Common law is law developed by judges through decisions of courts.
        ```
        """)
    else:
        # Current card
        idx = st.session_state.order[st.session_state.index]
        question, answer = st.session_state.cards[idx]
        
        st.subheader(f"Q: {question}")
        
        # Question voice controls
        current_audio_id = f"card_{idx}_question"
        is_playing = st.session_state.audio_playing == current_audio_id
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("🔊 Play Question", key="play_question", disabled=is_playing):
                with st.spinner("Generating audio..."):
                    audio_bytes = text_to_speech(question, lang="en")
                    if audio_bytes:
                        st.session_state[f"audio_{current_audio_id}"] = audio_bytes
                        st.session_state.audio_playing = current_audio_id
                        st.session_state.stop_requested = False
                        st.rerun()
        
        with col2:
            if is_playing:
                if st.button("⏹️ Stop", key="stop_question", type="secondary"):
                    stop_audio()
                    st.rerun()
        
        with col3:
            # Download question audio button
            if st.button("⬇️ Question Audio", key=f"dl_q_{idx}"):
                with st.spinner("Generating download..."):
                    audio_bytes = text_to_speech(question, lang="en")
                    if audio_bytes:
                        filename = f"question_{idx+1}.mp3"
                        b64 = base64.b64encode(audio_bytes).decode()
                        href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}" style="text-decoration:none;">'
                        st.markdown(f'{href}<button style="display:none;" id="download_q_{idx}">Download</button></a>', unsafe_allow_html=True)
                        st.markdown(f'<script>document.getElementById("download_q_{idx}").click();</script>', unsafe_allow_html=True)
                        st.success(f"Download started: {filename}")
        
        # Show looping audio player if this audio is playing
        if is_playing and not st.session_state.stop_requested:
            audio_bytes = st.session_state.get(f"audio_{current_audio_id}")
            if audio_bytes:
                # Create looping audio player
                audio_html = f"""
                <audio autoplay loop style="display:none;">
                <source src="data:audio/mp3;base64,{base64.b64encode(audio_bytes).decode()}" type="audio/mp3">
                Your browser does not support the audio element.
                </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
                st.success("🔁 Playing question audio on loop...")
        
        if st.session_state.show_answer:
            st.markdown(f"""<div style='color:red; font-size:30px; padding:20px; border-left:5px solid #4CAF50; background-color:#f9f9f9; border-radius:5px; margin:10px 0;'><strong>A:</strong><br>{answer}</div>""", unsafe_allow_html=True)
            
            # Answer voice controls
            current_audio_id_answer = f"card_{idx}_answer"
            is_playing_answer = st.session_state.audio_playing == current_audio_id_answer
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("🔊 Play Answer", key="play_answer", disabled=is_playing_answer):
                    with st.spinner("Generating audio..."):
                        audio_bytes = text_to_speech(answer, lang="en")
                        if audio_bytes:
                            st.session_state[f"audio_{current_audio_id_answer}"] = audio_bytes
                            st.session_state.audio_playing = current_audio_id_answer
                            st.session_state.stop_requested = False
                            st.rerun()
            
            with col2:
                if is_playing_answer:
                    if st.button("⏹️ Stop", key="stop_answer", type="secondary"):
                        stop_audio()
                        st.rerun()
            
            with col3:
                # Download answer audio button
                if st.button("⬇️ Answer Audio", key=f"dl_a_{idx}"):
                    with st.spinner("Generating download..."):
                        audio_bytes = text_to_speech(answer, lang="en")
                        if audio_bytes:
                            filename = f"answer_{idx+1}.mp3"
                            b64 = base64.b64encode(audio_bytes).decode()
                            href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}" style="text-decoration:none;">'
                            st.markdown(f'{href}<button style="display:none;" id="download_a_{idx}">Download</button></a>', unsafe_allow_html=True)
                            st.markdown(f'<script>document.getElementById("download_a_{idx}").click();</script>', unsafe_allow_html=True)
                            st.success(f"Download started: {filename}")
            
            # Download combined audio button
            st.markdown("---")
            if st.button("⬇️ Combined Q&A Audio", key=f"dl_combined_{idx}", type="primary"):
                with st.spinner("Generating combined audio..."):
                    combined_audio = generate_combined_audio(question, answer)
                    if combined_audio:
                        filename = f"flashcard_{idx+1}_question_answer.mp3"
                        b64 = base64.b64encode(combined_audio).decode()
                        href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}" style="text-decoration:none;">'
                        st.markdown(f'{href}<button style="display:none;" id="download_combined_{idx}">Download</button></a>', unsafe_allow_html=True)
                        st.markdown(f'<script>document.getElementById("download_combined_{idx}").click();</script>', unsafe_allow_html=True)
                        st.success(f"Download started: {filename}")
            
            # Show looping audio player if answer audio is playing
            if is_playing_answer and not st.session_state.stop_requested:
                audio_bytes = st.session_state.get(f"audio_{current_audio_id_answer}")
                if audio_bytes:
                    # Create looping audio player
                    audio_html = f"""
                    <audio autoplay loop style="display:none;">
                    <source src="data:audio/mp3;base64,{base64.b64encode(audio_bytes).decode()}" type="audio/mp3">
                    Your browser does not support the audio element.
                    </audio>
                    """
                    st.markdown(audio_html, unsafe_allow_html=True)
                    st.success("🔁 Playing answer audio on loop...")
        
        # Handlers
        def handle_show_answer():
            st.session_state.show_answer = True
        
        def handle_next_card():
            st.session_state.index = (st.session_state.index + 1) % len(st.session_state.order)
            st.session_state.show_answer = False
            # Stop any playing audio when moving to next card
            st.session_state.audio_playing = None
            st.session_state.stop_requested = False
        
        col1, col2 = st.columns(2)
        col1.button("Show Answer", on_click=handle_show_answer)
        col2.button("Next Card", on_click=handle_next_card)
        
        # Optional controls
        with st.expander("⚙️ Card Settings"):
            if st.button("Shuffle Deck"):
                random.shuffle(st.session_state.order)
                st.session_state.index = 0
                st.session_state.show_answer = False
                # Stop any playing audio when shuffling
                st.session_state.audio_playing = None
                st.session_state.stop_requested = False
                st.success("Deck shuffled!")
            
            st.write(f"**Card {st.session_state.index + 1} of {len(st.session_state.order)}**")
            
            # Navigation
            st.markdown("---")
            st.write("**Quick Navigation:**")
            nav_col1, nav_col2, nav_col3 = st.columns(3)
            with nav_col1:
                if st.button("⏮️ First"):
                    st.session_state.index = 0
                    st.session_state.show_answer = False
                    st.session_state.audio_playing = None
                    st.rerun()
            with nav_col2:
                if st.button("⏪ Previous"):
                    st.session_state.index = (st.session_state.index - 1) % len(st.session_state.order)
                    st.session_state.show_answer = False
                    st.session_state.audio_playing = None
                    st.rerun()
            with nav_col3:
                if st.button("⏩ Next"):
                    st.session_state.index = (st.session_state.index + 1) % len(st.session_state.order)
                    st.session_state.show_answer = False
                    st.session_state.audio_playing = None
                    st.rerun()

# 📝 Quiz functionality
def show_quiz():
    st.title("📝 LLB Preparation Quiz")
    
    if not st.session_state.quiz_started:
        st.write("Test your knowledge with this interactive quiz!")
        st.write(f"Total flashcards available: {len(st.session_state.cards)}")
        
        num_questions = st.slider(
            "Number of questions:",
            min_value=3,
            max_value=min(20, len(st.session_state.cards)),
            value=min(10, len(st.session_state.cards))
        )
        
        if st.button("🚀 Start Quiz", type="primary"):
            if len(st.session_state.cards) < 4:
                st.error("Need at least 4 flashcards to create a quiz with options.")
                return
            
            st.session_state.quiz_started = True
            st.session_state.quiz_completed = False
            st.session_state.quiz_answers = {}
            st.session_state.quiz_feedback = {}
            st.session_state.current_question_index = 0
            
            # Select random flashcards for the quiz
            if len(st.session_state.cards) <= num_questions:
                quiz_cards = st.session_state.cards.copy()
            else:
                quiz_cards = random.sample(st.session_state.cards, num_questions)
            
            st.session_state.quiz_cards = quiz_cards
            st.session_state.quiz_type = "Question to Answer"
            st.rerun()
    
    else:
        quiz_cards = st.session_state.quiz_cards
        current_index = st.session_state.current_question_index
        
        if not st.session_state.quiz_completed:
            # Show progress at the top
            col1, col2 = st.columns([1, 1])
            with col1:
                st.metric("Questions", f"{current_index + 1}/{len(quiz_cards)}")
            with col2:
                percentage = ((current_index) / len(quiz_cards)) * 100 if quiz_cards else 0
                st.metric("Progress", f"{percentage:.0f}%")
            
            st.markdown("---")
            
            if current_index < len(quiz_cards):
                question, answer = quiz_cards[current_index]
                question_num = current_index + 1
                
                st.subheader(f"Question {question_num} of {len(quiz_cards)}")
                
                st.markdown(f'<h3 style="color:#FF0000;">{question}</h3>', unsafe_allow_html=True)
                st.write(f"Select the correct answer:")
                
                # Check if answer already submitted for this question
                if current_index in st.session_state.quiz_answers:
                    # Show feedback for already answered question
                    selected_answer = st.session_state.quiz_answers[current_index]
                    
                    # Show correct answer
                    st.info(f"**Correct answer:** {answer}")
                    
                    # Next Question button
                    if st.button("➡️ Next Question", key=f"next_{current_index}", type="primary"):
                        if current_index + 1 < len(quiz_cards):
                            st.session_state.current_question_index = current_index + 1
                        else:
                            st.session_state.quiz_completed = True
                        st.rerun()
                
                else:
                    # Not answered yet - show options for selection
                    options = [answer]
                    other_cards = [card for card in st.session_state.cards if card != (question, answer)]
                    
                    if len(other_cards) >= 3:
                        # Get answers from other cards as wrong options
                        other_options = random.sample(other_cards, 3)
                        options.extend([opt[1] for opt in other_options])  # Get answers
                    else:
                        # Generic wrong answers if not enough cards
                        options.extend([
                            "Not applicable in this context",
                            "This is an incorrect interpretation",
                            "The opposite is true"
                        ])
                    
                    random.shuffle(options)
                    
                    # Use a unique key for the radio button
                    radio_key = f"quiz_radio_{current_index}"
                    selected_answer = st.radio(
                        f"Choose your answer:",
                        options,
                        key=radio_key,
                        index=None  # No default selection
                    )
                    
                    # Submit button
                    if selected_answer:
                        # Store the answer
                        st.session_state.quiz_answers[current_index] = selected_answer
                        
                        # Show immediate feedback
                        if selected_answer == answer:
                            st.success("✅ Correct!")
                            st.balloons()
                        else:
                            st.error("❌ Incorrect")
                        
                        # Show correct answer
                        st.info(f"**Correct answer:** {answer}")
                        
                        # Auto-proceed after 2 seconds
                        time.sleep(2)
                        if current_index + 1 < len(quiz_cards):
                            st.session_state.current_question_index = current_index + 1
                        else:
                            st.session_state.quiz_completed = True
                        st.rerun()
                    
                    # Skip button
                    if st.button("⏭️ Skip Question", key=f"skip_{current_index}", type="secondary"):
                        # Mark as skipped
                        st.session_state.quiz_answers[current_index] = "SKIPPED"
                        # Move to next question
                        if current_index + 1 < len(quiz_cards):
                            st.session_state.current_question_index = current_index + 1
                        else:
                            st.session_state.quiz_completed = True
                        st.rerun()
            
            else:
                # All questions answered
                st.session_state.quiz_completed = True
                st.rerun()
        
        else:
            # Quiz completed - show simple summary
            st.balloons()
            st.success("🎉 Quiz Completed!")
            
            # Calculate score
            total_questions = len(quiz_cards)
            correct_answers = 0
            for i in range(total_questions):
                user_answer = st.session_state.quiz_answers.get(i, "")
                correct_answer = quiz_cards[i][1]  # Get answer from (question, answer) tuple
                if user_answer == correct_answer:
                    correct_answers += 1
            
            # Display score
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Questions", total_questions)
            with col2:
                st.metric("Correct Answers", correct_answers)
            with col3:
                percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
                st.metric("Score", f"{percentage:.1f}%")
            
            # Performance message
            if percentage >= 80:
                st.success("🏆 Excellent! You're mastering the material!")
            elif percentage >= 60:
                st.info("👍 Good job! Solid understanding!")
            elif percentage >= 40:
                st.warning("📚 Keep practicing! You're getting there!")
            else:
                st.error("💪 Review the material and try again!")
            
            # Restart options
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Retry Quiz", use_container_width=True):
                    # Reset for same quiz
                    st.session_state.quiz_started = True
                    st.session_state.quiz_completed = False
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_feedback = {}
                    st.session_state.current_question_index = 0
                    st.rerun()
            with col2:
                if st.button("📝 New Quiz", use_container_width=True, type="primary"):
                    # Go back to start
                    st.session_state.quiz_started = False
                    st.session_state.quiz_completed = False
                    st.session_state.current_question_index = 0
                    st.rerun()

# 📥 Bulk download functionality (simplified for Streamlit Cloud)
def show_bulk_download():
    st.title("📥 Bulk Audio Download")
    st.write("Generate and download audio files for your flashcards")
    
    st.warning("⚠️ Note: Bulk download generates audio on-demand and may take time for large sets.")
    
    download_type = st.selectbox(
        "Select download type:",
        ["Question only", "Answer only", "Question then Answer"]
    )
    
    # Limit for Streamlit Cloud (timeouts)
    max_cards = min(20, len(st.session_state.cards))
    
    if st.button("🛠️ Generate Download Package", type="primary"):
        if len(st.session_state.cards) > 20:
            st.warning(f"Generating audio for first 20 cards only (out of {len(st.session_state.cards)}) for performance.")
        
        with st.spinner(f"Generating audio files (this may take a minute)..."):
            try:
                # Create temporary directory for files
                with tempfile.TemporaryDirectory() as tmpdir:
                    zip_filename = f"llb_flashcards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                    zip_path = os.path.join(tmpdir, zip_filename)
                    
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        processed = 0
                        progress_bar = st.progress(0)
                        
                        for i, (question, answer) in enumerate(st.session_state.cards[:max_cards]):
                            # Update progress
                            progress = (i + 1) / max_cards
                            progress_bar.progress(progress)
                            
                            # Clean text for filename
                            clean_question = re.sub(r'[^\w\s-]', '', question)[:30]
                            
                            # Generate audio based on type
                            if download_type == "Question only":
                                audio_bytes = text_to_speech(question, lang="en")
                                if audio_bytes:
                                    filename = f"question_{i+1:02d}.mp3"
                                    zipf.writestr(filename, audio_bytes)
                                    processed += 1
                            
                            elif download_type == "Answer only":
                                audio_bytes = text_to_speech(answer, lang="en")
                                if audio_bytes:
                                    filename = f"answer_{i+1:02d}.mp3"
                                    zipf.writestr(filename, audio_bytes)
                                    processed += 1
                            
                            elif download_type == "Question then Answer":
                                audio_bytes = generate_combined_audio(question, answer)
                                if audio_bytes:
                                    filename = f"flashcard_{i+1:02d}_qa.mp3"
                                    zipf.writestr(filename, audio_bytes)
                                    processed += 1
                        
                        progress_bar.empty()
                    
                    # Read the zip file
                    with open(zip_path, 'rb') as f:
                        zip_data = f.read()
                    
                    # Provide download link
                    b64_zip = base64.b64encode(zip_data).decode()
                    href = f'<a href="data:application/zip;base64,{b64_zip}" download="{zip_filename}" style="text-decoration:none;">'
                    st.markdown(f'{href}<button style="background-color:#2196F3; color:white; padding:10px 20px; border:none; border-radius:5px; font-size:16px; cursor:pointer;">⬇️ Download Audio Files ({processed} files)</button></a>', unsafe_allow_html=True)
                    
                    st.success(f"✅ Generated {processed} audio files!")
                    st.info("The zip file contains audio files in MP3 format.")
                    
            except Exception as e:
                st.error(f"Error generating download package: {e}")
                st.info("This might be due to timeout or memory limits on Streamlit Cloud.")

# ⚙️ Settings tab
def show_settings():
    st.subheader("⚙️ Application Settings")
    
    if st.session_state.cards:
        st.success(f"✅ Loaded {len(st.session_state.cards)} flashcards")
    else:
        st.error("❌ No flashcards loaded")
    
    # Display document info
    with st.expander("📄 Document Information"):
        st.write(f"**Document Path:** {DOC_PATH}")
        st.write(f"**File Exists:** {'✅ Yes' if os.path.exists(DOC_PATH) else '❌ No'}")
        if st.session_state.cards:
            st.write(f"**Sample Cards:**")
            for i, (question, answer) in enumerate(st.session_state.cards[:3]):
                st.write(f"{i+1}. **Q:** {question[:50]}...")
                st.write(f"   **A:** {answer[:50]}...")
                st.write("---")
    
    # Reset button
    if st.button("🔄 Reset Application State"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # About section
    with st.expander("ℹ️ About This App"):
        st.write("""
        **LLB Preparation Flashcards with Voiceover**
        
        This app helps you study for LLB exams using:
        - Interactive flashcards with voice support
        - Quiz mode for self-testing
        - Audio generation for auditory learning
        - Bulk download of study materials
        
        **Features:**
        - 📚 Flashcards with Q&A format
        - 🔊 Text-to-speech for questions and answers
        - 🔁 Looping audio with stop controls
        - 📝 Interactive quiz with scoring
        - 📥 Bulk audio download
        - ⚙️ Easy document loading
        
        **Requirements:**
        - Word document with Q: and A: format
        - Internet connection for audio generation
        - Modern web browser
        """)

# 🚀 Run the app
def main():
    # Set page config
    st.set_page_config(
        page_title="LLB Preparation Flashcards",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Sidebar info
    with st.sidebar:
        st.title("📚 LLB Prep")
        st.markdown("---")
        st.info("Study LLB materials with interactive flashcards and voice support")
        
        if st.session_state.cards:
            st.success(f"**{len(st.session_state.cards)} cards loaded**")
        else:
            st.warning("No cards loaded")
        
        st.markdown("---")
        st.caption("Made with ❤️ for LLB students")
    
    # Create tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs(["🎴 Flashcards", "📝 Quiz", "📥 Bulk Download", "⚙️ Settings"])
    
    with tab1:
        show_flashcards()
    
    with tab2:
        show_quiz()
    
    with tab3:
        show_bulk_download()
    
    with tab4:
        show_settings()

if __name__ == "__main__":
    main()