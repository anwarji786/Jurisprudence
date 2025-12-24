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

# Dictionary for UI translations (no external dependency needed)
UI_TRANSLATIONS = {
    'English': {
        'app_title': "LLB Preparation Flashcards with Voiceover",
        'quiz_title': "LLB Preparation Quiz",
        'bulk_download': "Bulk Audio Download",
        'settings': "Application Settings",
        'flashcards': "Flashcards",
        'quiz': "Quiz",
        'download': "Bulk Download",
        'settings_tab': "Settings",
        'document_info': "Document Information",
        'total_cards': "Total Cards",
        'sample_question': "Sample Question",
        'currently_playing': "Currently playing audio",
        'stop_all_audio': "Stop All Audio",
        'no_audio': "No audio currently playing",
        'no_flashcards': "No flashcards found. Ensure your document uses Q:/A: lines.",
        'expected_format': "Expected format:",
        'format_example': "Q: What is the definition of law?\nA: Law is a system of rules...",
        'play_question': "🔊 Play Question",
        'stop': "⏹️ Stop",
        'question_audio': "⬇️ Question Audio",
        'playing_loop': "🔁 Playing question audio on loop...",
        'show_answer': "Show Answer",
        'next_card': "Next Card",
        'play_answer': "🔊 Play Answer",
        'answer_audio': "⬇️ Answer Audio",
        'combined_qa': "⬇️ Combined Q&A Audio",
        'card_settings': "Card Settings",
        'shuffle_deck': "Shuffle Deck",
        'quick_navigation': "Quick Navigation",
        'first': "⏮️ First",
        'previous': "⏪ Previous",
        'next': "⏩ Next",
        'test_knowledge': "Test your knowledge with this interactive quiz!",
        'cards_available': "Total flashcards available",
        'num_questions': "Number of questions:",
        'start_quiz': "🚀 Start Quiz",
        'questions': "Questions",
        'progress': "Progress",
        'select_answer': "Select the correct answer:",
        'correct_answer': "Correct answer:",
        'next_question': "➡️ Next Question",
        'choose_answer': "Choose your answer:",
        'skip_question': "⏭️ Skip Question",
        'quiz_completed': "🎉 Quiz Completed!",
        'total_questions': "Total Questions",
        'correct_answers': "Correct Answers",
        'score': "Score",
        'excellent': "🏆 Excellent! You're mastering the material!",
        'good_job': "👍 Good job! Solid understanding!",
        'keep_practicing': "📚 Keep practicing! You're getting there!",
        'review_material': "💪 Review the material and try again!",
        'retry_quiz': "🔄 Retry Quiz",
        'new_quiz': "📝 New Quiz",
        'generate_download': "Generate and download audio files for your flashcards",
        'bulk_note': "⚠️ Note: Bulk download generates audio on-demand and may take time for large sets.",
        'select_type': "Select download type:",
        'question_only': "Question only",
        'answer_only': "Answer only",
        'question_then_answer': "Question then Answer",
        'generate_package': "🛠️ Generate Download Package",
        'downloading': "Download Audio Files",
        'generated_files': "Generated audio files!",
        'zip_info': "The zip file contains audio files in MP3 format.",
        'loaded_cards': "Loaded flashcards",
        'no_cards_loaded': "No flashcards loaded",
        'document_path': "Document Path",
        'file_exists': "File Exists",
        'sample_cards': "Sample Cards",
        'reset_state': "🔄 Reset Application State",
        'about_app': "ℹ️ About This App",
        'sidebar_title': "📚 LLB Prep",
        'sidebar_info': "Study LLB materials with interactive flashcards and voice support",
        'cards_loaded': "cards loaded",
        'made_with': "Made with ❤️ for LLB students",
        'language': "🌐 Language",
        'english': "English",
        'hindi': "Hindi",
        'display_mode': "Display Mode",
        'voice_language': "Voice Language",
        'hindi_voice': "Hindi Voice",
        'english_voice': "English Voice",
        'view_translation': "View Hindi Translation",
        'hide_translation': "Hide Hindi Translation",
        'original_text': "Original Text",
        'hindi_translation': "Hindi Translation",
        'listen_hindi': "🔊 Listen in Hindi",
        'listen_english': "🔊 Listen in English",
        'download_hindi': "⬇️ Hindi Audio",
        'download_english': "⬇️ English Audio",
        'combined_bilingual': "⬇️ Combined Bilingual Audio",
        'question_in_hindi': "प्रश्न:",
        'answer_in_hindi': "उत्तर:",
        'translation_loading': "Translating to Hindi...",
        'translation_error': "Translation not available",
        'enter_hindi': "Enter Hindi Translation",
        'manual_translation': "Manual Translation",
        'save_translation': "💾 Save Translation",
        'translation_saved': "✅ Translation saved!",
        'hindi_text_placeholder': "Type Hindi translation here...",
        'switch_to_hindi': "Switch to Hindi",
        'switch_to_english': "Switch to English",
        'current_language': "Current Language",
        'language_switch': "🌐 Language Switch"
    },
    'Hindi': {
        'app_title': "एलएलबी तैयारी फ्लैशकार्ड्स वॉयसओवर के साथ",
        'quiz_title': "एलएलबी तैयारी क्विज",
        'bulk_download': "बल्क ऑडियो डाउनलोड",
        'settings': "एप्लिकेशन सेटिंग्स",
        'flashcards': "फ्लैशकार्ड्स",
        'quiz': "क्विज",
        'download': "बल्क डाउनलोड",
        'settings_tab': "सेटिंग्स",
        'document_info': "दस्तावेज़ जानकारी",
        'total_cards': "कुल कार्ड",
        'sample_question': "नमूना प्रश्न",
        'currently_playing': "वर्तमान में ऑडियो चल रहा है",
        'stop_all_audio': "सभी ऑडियो रोकें",
        'no_audio': "कोई ऑडियो वर्तमान में नहीं चल रहा",
        'no_flashcards': "कोई फ्लैशकार्ड नहीं मिला। सुनिश्चित करें कि आपका दस्तावेज़ Q:/A: लाइन्स का उपयोग करता है।",
        'expected_format': "अपेक्षित प्रारूप:",
        'format_example': "Q: कानून की परिभाषा क्या है?\nA: कानून नियमों की एक प्रणाली है...",
        'play_question': "🔊 प्रश्न सुनें",
        'stop': "⏹️ रोकें",
        'question_audio': "⬇️ प्रश्न ऑडियो",
        'playing_loop': "🔁 प्रश्न ऑडियो लूप पर चल रहा है...",
        'show_answer': "उत्तर दिखाएं",
        'next_card': "अगला कार्ड",
        'play_answer': "🔊 उत्तर सुनें",
        'answer_audio': "⬇️ उत्तर ऑडियो",
        'combined_qa': "⬇️ संयुक्त प्रश्न और उत्तर ऑडियो",
        'card_settings': "कार्ड सेटिंग्स",
        'shuffle_deck': "कार्ड मिलाएं",
        'quick_navigation': "त्वरित नेविगेशन",
        'first': "⏮️ पहला",
        'previous': "⏪ पिछला",
        'next': "⏩ अगला",
        'test_knowledge': "इस इंटरएक्टिव क्विज़ के साथ अपने ज्ञान का परीक्षण करें!",
        'cards_available': "कुल उपलब्ध फ्लैशकार्ड्स",
        'num_questions': "प्रश्नों की संख्या:",
        'start_quiz': "🚀 क्विज़ शुरू करें",
        'questions': "प्रश्न",
        'progress': "प्रगति",
        'select_answer': "सही उत्तर चुनें:",
        'correct_answer': "सही उत्तर:",
        'next_question': "➡️ अगला प्रश्न",
        'choose_answer': "अपना उत्तर चुनें:",
        'skip_question': "⏭️ प्रश्न छोड़ें",
        'quiz_completed': "🎉 क्विज़ पूर्ण हुआ!",
        'total_questions': "कुल प्रश्न",
        'correct_answers': "सही उत्तर",
        'score': "स्कोर",
        'excellent': "🏆 उत्कृष्ट! आप सामग्री में महारत हासिल कर रहे हैं!",
        'good_job': "👍 अच्छा काम! ठोस समझ!",
        'keep_practicing': "📚 अभ्यास जारी रखें! आप लगभग वहाँ हैं!",
        'review_material': "💪 सामग्री की समीक्षा करें और फिर से प्रयास करें!",
        'retry_quiz': "🔄 क्विज़ पुनः प्रयास करें",
        'new_quiz': "📝 नया क्विज़",
        'generate_download': "अपने फ्लैशकार्ड्स के लिए ऑडियो फ़ाइलें जनरेट और डाउनलोड करें",
        'bulk_note': "⚠️ नोट: बल्क डाउनलोड ऑन-डिमांड ऑडियो जनरेट करता है और बड़े सेट के लिए समय ले सकता है।",
        'select_type': "डाउनलोड प्रकार चुनें:",
        'question_only': "केवल प्रश्न",
        'answer_only': "केवल उत्तर",
        'question_then_answer': "प्रश्न फिर उत्तर",
        'generate_package': "🛠️ डाउनलोड पैकेज जनरेट करें",
        'downloading': "ऑडियो फ़ाइलें डाउनलोड करें",
        'generated_files': "ऑडियो फ़ाइलें जनरेट की गईं!",
        'zip_info': "ज़िप फ़ाइल में MP3 प्रारूप में ऑडियो फ़ाइलें हैं।",
        'loaded_cards': "फ्लैशकार्ड्स लोड किए गए",
        'no_cards_loaded': "कोई कार्ड लोड नहीं किया गया",
        'document_path': "दस्तावेज़ पथ",
        'file_exists': "फ़ाइल मौजूद है",
        'sample_cards': "नमूना कार्ड",
        'reset_state': "🔄 एप्लिकेशन स्थिति रीसेट करें",
        'about_app': "ℹ️ इस ऐप के बारे में",
        'sidebar_title': "📚 एलएलबी तैयारी",
        'sidebar_info': "इंटरएक्टिव फ्लैशकार्ड्स और वॉइस सपोर्ट के साथ एलएलबी सामग्री का अध्ययन करें",
        'cards_loaded': "कार्ड लोड किए गए",
        'made_with': "एलएलबी छात्रों के लिए ❤️ के साथ बनाया गया",
        'language': "🌐 भाषा",
        'english': "अंग्रेज़ी",
        'hindi': "हिंदी",
        'display_mode': "डिस्प्ले मोड",
        'voice_language': "वॉयस भाषा",
        'hindi_voice': "हिंदी वॉयस",
        'english_voice': "अंग्रेज़ी वॉयस",
        'view_translation': "हिंदी अनुवाद देखें",
        'hide_translation': "हिंदी अनुवाद छिपाएं",
        'original_text': "मूल पाठ",
        'hindi_translation': "हिंदी अनुवाद",
        'listen_hindi': "🔊 हिंदी में सुनें",
        'listen_english': "🔊 अंग्रेज़ी में सुनें",
        'download_hindi': "⬇️ हिंदी ऑडियो",
        'download_english': "⬇️ अंग्रेज़ी ऑडियो",
        'combined_bilingual': "⬇️ संयुक्त द्विभाषी ऑडियो",
        'question_in_hindi': "प्रश्न:",
        'answer_in_hindi': "उत्तर:",
        'translation_loading': "हिंदी में अनुवाद हो रहा है...",
        'translation_error': "अनुवाद उपलब्ध नहीं है",
        'enter_hindi': "हिंदी अनुवाद दर्ज करें",
        'manual_translation': "मैनुअल अनुवाद",
        'save_translation': "💾 अनुवाद सहेजें",
        'translation_saved': "✅ अनुवाद सहेजा गया!",
        'hindi_text_placeholder': "हिंदी अनुवाद यहाँ टाइप करें...",
        'switch_to_hindi': "हिंदी में स्विच करें",
        'switch_to_english': "अंग्रेज़ी में स्विच करें",
        'current_language': "वर्तमान भाषा",
        'language_switch': "🌐 भाषा स्विच"
    }
}

def t(key):
    """Get translated text for the current language"""
    lang = st.session_state.language
    if lang in UI_TRANSLATIONS and key in UI_TRANSLATIONS[lang]:
        return UI_TRANSLATIONS[lang][key]
    # Fallback to English if translation not found
    return UI_TRANSLATIONS['English'].get(key, key)

def load_bilingual_flashcards(doc_path):
    """
    Reads the Word document and extracts bilingual Q&A pairs.
    Expected format:
    Q: English question
    A: English answer
    Q (हिंदी): Hindi question
    A (हिंदी): Hindi answer
    """
    try:
        document = Document(doc_path)
        cards = []
        english_question = None
        english_answer = None
        hindi_question = None
        hindi_answer = None

        for para in document.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            # Check for English question
            if text.startswith("Q:") and "(हिंदी)" not in text:
                english_question = text[2:].strip()
            # Check for English answer
            elif text.startswith("A:") and "(हिंदी)" not in text and english_question:
                english_answer = text[2:].strip()
            # Check for Hindi question
            elif text.startswith("Q") and "(हिंदी)" in text:
                hindi_question = text.split(":", 1)[1].strip() if ":" in text else text
            # Check for Hindi answer
            elif text.startswith("A") and "(हिंदी)" in text and hindi_question:
                hindi_answer = text.split(":", 1)[1].strip() if ":" in text else text
                
                # If we have both English and Hindi, create a bilingual card
                if english_question and english_answer:
                    cards.append({
                        'english': (english_question, english_answer),
                        'hindi': (hindi_question, hindi_answer) if hindi_question and hindi_answer else (english_question, english_answer)
                    })
                    
                    # Reset for next card
                    english_question = None
                    english_answer = None
                    hindi_question = None
                    hindi_answer = None
        
        # If we have English cards but no Hindi translations, create them with English text
        if not cards and english_question and english_answer:
            cards.append({
                'english': (english_question, english_answer),
                'hindi': (english_question, english_answer)
            })
        
        if not cards:
            st.warning(t('no_flashcards'))
            st.info(f"{t('expected_format')}\n```\n{t('format_example')}\n```")
        
        return cards
    except Exception as e:
        st.error(f"Error reading document: {e}")
        return []

# Session state for language
if 'language' not in st.session_state:
    st.session_state.language = 'English'  # Default language
if 'translations' not in st.session_state:
    st.session_state.translations = {}
if 'show_hindi' not in st.session_state:
    st.session_state.show_hindi = False
if 'manual_translations' not in st.session_state:
    st.session_state.manual_translations = {}

# Session state initialization
if "cards" not in st.session_state:
    try:
        st.session_state.cards = load_bilingual_flashcards(DOC_PATH)
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
            if lang == "en" or lang == "hi":
                clean_text = "No text available"
        
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
def generate_combined_audio(question_text, answer_text, lang="en"):
    """Generate audio with Question first, then Answer"""
    try:
        # Generate Question audio
        question_audio = text_to_speech(question_text, lang=lang)
        
        # Generate Answer audio
        answer_audio = text_to_speech(answer_text, lang=lang)
        
        if question_audio and answer_audio:
            # Combine the audio bytes (simple concatenation)
            combined_bytes = question_audio + answer_audio
            return combined_bytes
        else:
            return None
    except Exception as e:
        st.error(f"Error generating combined audio: {e}")
        return None

# 🔊 Generate bilingual audio (English then Hindi)
def generate_bilingual_audio(english_text, hindi_text):
    """Generate audio with English first, then Hindi"""
    try:
        # Generate English audio
        english_audio = text_to_speech(english_text, lang="en")
        
        # Generate Hindi audio
        hindi_audio = text_to_speech(hindi_text, lang="hi")
        
        if english_audio and hindi_audio:
            # Combine the audio bytes
            combined_bytes = english_audio + hindi_audio
            return combined_bytes
        else:
            return None
    except Exception as e:
        st.error(f"Error generating bilingual audio: {e}")
        return None

# Language switch function
def switch_language():
    """Switch between English and Hindi"""
    if st.session_state.language == 'English':
        st.session_state.language = 'Hindi'
    else:
        st.session_state.language = 'English'
    st.rerun()

# 🎴 Display flashcards with voiceover
def show_flashcards():
    st.title(t('app_title'))
    
    # TOP MENU LANGUAGE SWITCH BUTTONS
    # Create a container at the top for language switch buttons
    with st.container():
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.markdown(f"### {t('current_language')}: **{t('english') if st.session_state.language == 'English' else t('hindi')}**")
        
        with col2:
            st.markdown("### 🌐")
        
        with col3:
            # Create two buttons side by side for language switching
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                if st.button(f"🇺🇸 {t('english')}", 
                           type="primary" if st.session_state.language == 'English' else "secondary",
                           use_container_width=True,
                           key="switch_to_english"):
                    st.session_state.language = 'English'
                    st.rerun()
            
            with btn_col2:
                if st.button(f"🇮🇳 {t('hindi')}", 
                           type="primary" if st.session_state.language == 'Hindi' else "secondary",
                           use_container_width=True,
                           key="switch_to_hindi"):
                    st.session_state.language = 'Hindi'
                    st.rerun()
        
        st.markdown("---")
    
    # Display mode in sidebar (optional)
    with st.sidebar:
        st.markdown("---")
        st.subheader(t('display_mode'))
        
        # Toggle for showing both languages
        if st.session_state.language == 'English':
            st.session_state.show_hindi = st.checkbox(t('view_translation'), value=st.session_state.show_hindi)
        else:
            st.session_state.show_hindi = True
        
        st.markdown("---")
    
    # Show document info
    with st.expander(t('document_info'), expanded=False):
        st.write(f"**{t('document_info')}:** Law Preparation.docx")
        st.write(f"**{t('total_cards')}:** {len(st.session_state.cards)}")
        if st.session_state.cards:
            sample_question = st.session_state.cards[0]['english'][0]
            st.write(f"**{t('sample_question')}:** {sample_question[:50]}...")
    
    # Global stop button in sidebar
    with st.sidebar:
        if st.session_state.audio_playing:
            st.warning(f"🔊 {t('currently_playing')}")
            if st.button(f"⏹️ {t('stop_all_audio')}", type="primary", use_container_width=True):
                stop_audio()
                st.rerun()
        else:
            st.info(t('no_audio'))
    
    if not st.session_state.cards:
        st.warning(t('no_flashcards'))
        st.info(f"**{t('expected_format')}:**\n```\n{t('format_example')}\n```")
    else:
        # Current card
        idx = st.session_state.order[st.session_state.index]
        card = st.session_state.cards[idx]
        
        # Get English and Hindi content
        english_question, english_answer = card['english']
        hindi_question, hindi_answer = card['hindi']
        
        # Display based on language preference
        if st.session_state.language == 'Hindi':
            # Display in Hindi
            st.subheader(f"{t('question_in_hindi')} {hindi_question}")
            
            # Show English translation if enabled
            if st.session_state.show_hindi:
                st.markdown(f"*{t('original_text')}: {english_question}*")
        else:  # English
            # Display in English
            st.subheader(f"Q: {english_question}")
            
            # Show Hindi translation if enabled
            if st.session_state.show_hindi:
                st.markdown(f"*{t('hindi_translation')}: {hindi_question}*")
        
        # Voice controls - English
        current_audio_id = f"card_{idx}_question"
        is_playing = st.session_state.audio_playing == current_audio_id
        
        # Voice controls
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button(t('listen_english'), key="play_question_en", disabled=is_playing):
                with st.spinner("Generating audio..."):
                    audio_bytes = text_to_speech(english_question, lang="en")
                    if audio_bytes:
                        st.session_state[f"audio_{current_audio_id}"] = audio_bytes
                        st.session_state.audio_playing = current_audio_id
                        st.session_state.stop_requested = False
                        st.rerun()
        
        with col2:
            if st.button(t('listen_hindi'), key="play_question_hi", disabled=is_playing):
                with st.spinner("Generating audio..."):
                    audio_bytes = text_to_speech(hindi_question, lang="hi")
                    if audio_bytes:
                        st.session_state[f"audio_{current_audio_id}"] = audio_bytes
                        st.session_state.audio_playing = current_audio_id
                        st.session_state.stop_requested = False
                        st.rerun()
        
        with col3:
            if is_playing:
                if st.button(t('stop'), key="stop_question", type="secondary"):
                    stop_audio()
                    st.rerun()
        
        # Download audio buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t('download_english'), key=f"dl_q_en_{idx}", use_container_width=True):
                with st.spinner("Generating download..."):
                    audio_bytes = text_to_speech(english_question, lang="en")
                    if audio_bytes:
                        filename = f"question_{idx+1}_en.mp3"
                        b64 = base64.b64encode(audio_bytes).decode()
                        href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">'
                        st.markdown(f'{href}<button style="display:none;" id="download_q_en_{idx}">Download</button></a>', unsafe_allow_html=True)
                        st.markdown(f'<script>document.getElementById("download_q_en_{idx}").click();</script>', unsafe_allow_html=True)
                        st.success(f"Download started: {filename}")
        
        with col2:
            if st.button(t('download_hindi'), key=f"dl_q_hi_{idx}", use_container_width=True):
                with st.spinner("Generating download..."):
                    audio_bytes = text_to_speech(hindi_question, lang="hi")
                    if audio_bytes:
                        filename = f"question_{idx+1}_hi.mp3"
                        b64 = base64.b64encode(audio_bytes).decode()
                        href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">'
                        st.markdown(f'{href}<button style="display:none;" id="download_q_hi_{idx}">Download</button></a>', unsafe_allow_html=True)
                        st.markdown(f'<script>document.getElementById("download_q_hi_{idx}").click();</script>', unsafe_allow_html=True)
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
                st.success(t('playing_loop'))
        
        if st.session_state.show_answer:
            st.markdown("---")
            
            # Display answer
            if st.session_state.language == 'Hindi':
                # Display in Hindi
                st.markdown(f"""<div style='color:red; font-size:30px; padding:20px; border-left:5px solid #4CAF50; background-color:#f9f9f9; border-radius:5px; margin:10px 0;'><strong>{t('answer_in_hindi')}</strong><br>{hindi_answer}</div>""", unsafe_allow_html=True)
                
                # Show English translation if enabled
                if st.session_state.show_hindi:
                    st.markdown(f"*{t('original_text')}: {english_answer}*")
            else:  # English
                # Display in English
                st.markdown(f"""<div style='color:red; font-size:30px; padding:20px; border-left:5px solid #4CAF50; background-color:#f9f9f9; border-radius:5px; margin:10px 0;'><strong>A:</strong><br>{english_answer}</div>""", unsafe_allow_html=True)
                
                # Show Hindi translation if enabled
                if st.session_state.show_hindi:
                    st.markdown(f"*{t('hindi_translation')}: {hindi_answer}*")
            
            # Answer voice controls
            current_audio_id_answer = f"card_{idx}_answer"
            is_playing_answer = st.session_state.audio_playing == current_audio_id_answer
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button(t('listen_english'), key="play_answer_en", disabled=is_playing_answer):
                    with st.spinner("Generating audio..."):
                        audio_bytes = text_to_speech(english_answer, lang="en")
                        if audio_bytes:
                            st.session_state[f"audio_{current_audio_id_answer}"] = audio_bytes
                            st.session_state.audio_playing = current_audio_id_answer
                            st.session_state.stop_requested = False
                            st.rerun()
            
            with col2:
                if st.button(t('listen_hindi'), key="play_answer_hi", disabled=is_playing_answer):
                    with st.spinner("Generating audio..."):
                        audio_bytes = text_to_speech(hindi_answer, lang="hi")
                        if audio_bytes:
                            st.session_state[f"audio_{current_audio_id_answer}"] = audio_bytes
                            st.session_state.audio_playing = current_audio_id_answer
                            st.session_state.stop_requested = False
                            st.rerun()
            
            with col3:
                if is_playing_answer:
                    if st.button(t('stop'), key="stop_answer", type="secondary"):
                        stop_audio()
                        st.rerun()
            
            # Download answer audio buttons
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(t('download_english'), key=f"dl_a_en_{idx}", use_container_width=True):
                    with st.spinner("Generating download..."):
                        audio_bytes = text_to_speech(english_answer, lang="en")
                        if audio_bytes:
                            filename = f"answer_{idx+1}_en.mp3"
                            b64 = base64.b64encode(audio_bytes).decode()
                            href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">'
                            st.markdown(f'{href}<button style="display:none;" id="download_a_en_{idx}">Download</button></a>', unsafe_allow_html=True)
                            st.markdown(f'<script>document.getElementById("download_a_en_{idx}").click();</script>', unsafe_allow_html=True)
                            st.success(f"Download started: {filename}")
            
            with col2:
                if st.button(t('download_hindi'), key=f"dl_a_hi_{idx}", use_container_width=True):
                    with st.spinner("Generating download..."):
                        audio_bytes = text_to_speech(hindi_answer, lang="hi")
                        if audio_bytes:
                            filename = f"answer_{idx+1}_hi.mp3"
                            b64 = base64.b64encode(audio_bytes).decode()
                            href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">'
                            st.markdown(f'{href}<button style="display:none;" id="download_a_hi_{idx}">Download</button></a>', unsafe_allow_html=True)
                            st.markdown(f'<script>document.getElementById("download_a_hi_{idx}").click();</script>', unsafe_allow_html=True)
                            st.success(f"Download started: {filename}")
            
            # Combined audio downloads
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(t('combined_qa') + " (EN)", key=f"dl_combined_en_{idx}", type="primary", use_container_width=True):
                    with st.spinner("Generating combined audio..."):
                        combined_audio = generate_combined_audio(english_question, english_answer, lang="en")
                        if combined_audio:
                            filename = f"flashcard_{idx+1}_en.mp3"
                            b64 = base64.b64encode(combined_audio).decode()
                            href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">'
                            st.markdown(f'{href}<button style="display:none;" id="download_combined_en_{idx}">Download</button></a>', unsafe_allow_html=True)
                            st.markdown(f'<script>document.getElementById("download_combined_en_{idx}").click();</script>', unsafe_allow_html=True)
                            st.success(f"Download started: {filename}")
            
            with col2:
                if st.button(t('combined_bilingual'), key=f"dl_bilingual_{idx}", type="primary", use_container_width=True):
                    with st.spinner("Generating bilingual audio..."):
                        english_content = f"Question: {english_question} Answer: {english_answer}"
                        hindi_content = f"प्रश्न: {hindi_question} उत्तर: {hindi_answer}"
                        bilingual_audio = generate_bilingual_audio(english_content, hindi_content)
                        if bilingual_audio:
                            filename = f"flashcard_{idx+1}_bilingual.mp3"
                            b64 = base64.b64encode(bilingual_audio).decode()
                            href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">'
                            st.markdown(f'{href}<button style="display:none;" id="download_bilingual_{idx}">Download</button></a>', unsafe_allow_html=True)
                            st.markdown(f'<script>document.getElementById("download_bilingual_{idx}").click();</script>', unsafe_allow_html=True)
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
                    st.success(t('playing_loop'))
        
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
        col1.button(t('show_answer'), on_click=handle_show_answer)
        col2.button(t('next_card'), on_click=handle_next_card)
        
        # Optional controls
        with st.expander(f"⚙️ {t('card_settings')}"):
            if st.button(t('shuffle_deck')):
                random.shuffle(st.session_state.order)
                st.session_state.index = 0
                st.session_state.show_answer = False
                # Stop any playing audio when shuffling
                st.session_state.audio_playing = None
                st.session_state.stop_requested = False
                st.success("Deck shuffled!")
            
            st.write(f"**{t('card_settings')} {st.session_state.index + 1} of {len(st.session_state.order)}**")
            
            # Navigation
            st.markdown("---")
            st.write(f"**{t('quick_navigation')}:**")
            nav_col1, nav_col2, nav_col3 = st.columns(3)
            with nav_col1:
                if st.button(t('first')):
                    st.session_state.index = 0
                    st.session_state.show_answer = False
                    st.session_state.audio_playing = None
                    st.rerun()
            with nav_col2:
                if st.button(t('previous')):
                    st.session_state.index = (st.session_state.index - 1) % len(st.session_state.order)
                    st.session_state.show_answer = False
                    st.session_state.audio_playing = None
                    st.rerun()
            with nav_col3:
                if st.button(t('next')):
                    st.session_state.index = (st.session_state.index + 1) % len(st.session_state.order)
                    st.session_state.show_answer = False
                    st.session_state.audio_playing = None
                    st.rerun()

# 📝 Quiz functionality (simplified for bilingual)
def show_quiz():
    st.title(t('quiz_title'))
    
    # TOP MENU LANGUAGE SWITCH BUTTONS for Quiz page too
    with st.container():
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.markdown(f"### {t('current_language')}: **{t('english') if st.session_state.language == 'English' else t('hindi')}**")
        
        with col2:
            st.markdown("### 🌐")
        
        with col3:
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                if st.button(f"🇺🇸 {t('english')}", 
                           type="primary" if st.session_state.language == 'English' else "secondary",
                           use_container_width=True,
                           key="quiz_switch_to_english"):
                    st.session_state.language = 'English'
                    st.rerun()
            
            with btn_col2:
                if st.button(f"🇮🇳 {t('hindi')}", 
                           type="primary" if st.session_state.language == 'Hindi' else "secondary",
                           use_container_width=True,
                           key="quiz_switch_to_hindi"):
                    st.session_state.language = 'Hindi'
                    st.rerun()
        
        st.markdown("---")
    
    if not st.session_state.quiz_started:
        st.write(t('test_knowledge'))
        st.write(f"{t('cards_available')}: {len(st.session_state.cards)}")
        
        num_questions = st.slider(
            t('num_questions'),
            min_value=3,
            max_value=min(20, len(st.session_state.cards)),
            value=min(10, len(st.session_state.cards))
        )
        
        # Language selection for quiz
        quiz_lang = st.radio(
            "Quiz Language",
            ["English", "Hindi"],
            horizontal=True
        )
        
        if st.button(t('start_quiz'), type="primary"):
            if len(st.session_state.cards) < 4:
                st.error("Need at least 4 flashcards to create a quiz with options.")
                return
            
            st.session_state.quiz_started = True
            st.session_state.quiz_completed = False
            st.session_state.quiz_answers = {}
            st.session_state.quiz_feedback = {}
            st.session_state.current_question_index = 0
            st.session_state.quiz_language = quiz_lang
            
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
                st.metric(t('questions'), f"{current_index + 1}/{len(quiz_cards)}")
            with col2:
                percentage = ((current_index) / len(quiz_cards)) * 100 if quiz_cards else 0
                st.metric(t('progress'), f"{percentage:.0f}%")
            
            st.markdown("---")
            
            if current_index < len(quiz_cards):
                card = quiz_cards[current_index]
                english_question, english_answer = card['english']
                hindi_question, hindi_answer = card['hindi']
                question_num = current_index + 1
                
                st.subheader(f"{t('questions')} {question_num} of {len(quiz_cards)}")
                
                # Display question
                if st.session_state.quiz_language == "Hindi":
                    display_question = hindi_question
                    st.markdown(f'<h3 style="color:#FF0000;">{display_question}</h3>', unsafe_allow_html=True)
                else:
                    display_question = english_question
                    st.markdown(f'<h3 style="color:#FF0000;">{display_question}</h3>', unsafe_allow_html=True)
                
                st.write(f"{t('select_answer')}")
                
                # Check if answer already submitted for this question
                if current_index in st.session_state.quiz_answers:
                    # Show feedback for already answered question
                    selected_answer = st.session_state.quiz_answers[current_index]
                    
                    # Show correct answer
                    if st.session_state.quiz_language == "Hindi":
                        display_answer = hindi_answer
                        st.info(f"**{t('correct_answer')}:** {display_answer}")
                    else:
                        display_answer = english_answer
                        st.info(f"**{t('correct_answer')}:** {display_answer}")
                    
                    # Next Question button
                    if st.button(t('next_question'), key=f"next_{current_index}", type="primary"):
                        if current_index + 1 < len(quiz_cards):
                            st.session_state.current_question_index = current_index + 1
                        else:
                            st.session_state.quiz_completed = True
                        st.rerun()
                
                else:
                    # Not answered yet - show options for selection
                    correct_answer = hindi_answer if st.session_state.quiz_language == "Hindi" else english_answer
                    options = [correct_answer]
                    
                    # Get wrong options from other cards
                    other_cards = [c for c in st.session_state.cards if c != card]
                    
                    if len(other_cards) >= 3:
                        # Get answers from other cards as wrong options
                        other_options = random.sample(other_cards, 3)
                        for opt_card in other_options:
                            wrong_answer = opt_card['hindi'][1] if st.session_state.quiz_language == "Hindi" else opt_card['english'][1]
                            options.append(wrong_answer)
                    else:
                        # Generic wrong answers if not enough cards
                        if st.session_state.quiz_language == "Hindi":
                            options.extend([
                                "यह संदर्भ में लागू नहीं है",
                                "यह एक गलत व्याख्या है",
                                "इसका विपरीत सत्य है"
                            ])
                        else:
                            options.extend([
                                "Not applicable in this context",
                                "This is an incorrect interpretation",
                                "The opposite is true"
                            ])
                    
                    random.shuffle(options)
                    
                    # Use a unique key for the radio button
                    radio_key = f"quiz_radio_{current_index}"
                    selected_answer = st.radio(
                        f"{t('choose_answer')}",
                        options,
                        key=radio_key,
                        index=None  # No default selection
                    )
                    
                    # Submit button
                    if selected_answer:
                        # Store the answer
                        st.session_state.quiz_answers[current_index] = selected_answer
                        
                        # Show immediate feedback
                        if selected_answer == correct_answer:
                            st.success("✅ Correct!")
                            st.balloons()
                        else:
                            st.error("❌ Incorrect")
                        
                        # Show correct answer
                        st.info(f"**{t('correct_answer')}:** {correct_answer}")
                        
                        # Auto-proceed after 2 seconds
                        time.sleep(2)
                        if current_index + 1 < len(quiz_cards):
                            st.session_state.current_question_index = current_index + 1
                        else:
                            st.session_state.quiz_completed = True
                        st.rerun()
                    
                    # Skip button
                    if st.button(t('skip_question'), key=f"skip_{current_index}", type="secondary"):
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
            st.success(t('quiz_completed'))
            
            # Calculate score
            total_questions = len(quiz_cards)
            correct_answers = 0
            for i in range(total_questions):
                user_answer = st.session_state.quiz_answers.get(i, "")
                card = quiz_cards[i]
                correct_answer = card['hindi'][1] if st.session_state.quiz_language == "Hindi" else card['english'][1]
                if user_answer == correct_answer:
                    correct_answers += 1
            
            # Display score
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(t('total_questions'), total_questions)
            with col2:
                st.metric(t('correct_answers'), correct_answers)
            with col3:
                percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
                st.metric(t('score'), f"{percentage:.1f}%")
            
            # Performance message
            if percentage >= 80:
                st.success(t('excellent'))
            elif percentage >= 60:
                st.info(t('good_job'))
            elif percentage >= 40:
                st.warning(t('keep_practicing'))
            else:
                st.error(t('review_material'))
            
            # Restart options
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(t('retry_quiz'), use_container_width=True):
                    # Reset for same quiz
                    st.session_state.quiz_started = True
                    st.session_state.quiz_completed = False
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_feedback = {}
                    st.session_state.current_question_index = 0
                    st.rerun()
            with col2:
                if st.button(t('new_quiz'), use_container_width=True, type="primary"):
                    # Go back to start
                    st.session_state.quiz_started = False
                    st.session_state.quiz_completed = False
                    st.session_state.current_question_index = 0
                    st.rerun()

# 📥 Bulk download functionality (simplified for Streamlit Cloud)
def show_bulk_download():
    st.title(t('bulk_download'))
    
    # TOP MENU LANGUAGE SWITCH BUTTONS for Download page too
    with st.container():
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.markdown(f"### {t('current_language')}: **{t('english') if st.session_state.language == 'English' else t('hindi')}**")
        
        with col2:
            st.markdown("### 🌐")
        
        with col3:
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                if st.button(f"🇺🇸 {t('english')}", 
                           type="primary" if st.session_state.language == 'English' else "secondary",
                           use_container_width=True,
                           key="download_switch_to_english"):
                    st.session_state.language = 'English'
                    st.rerun()
            
            with btn_col2:
                if st.button(f"🇮🇳 {t('hindi')}", 
                           type="primary" if st.session_state.language == 'Hindi' else "secondary",
                           use_container_width=True,
                           key="download_switch_to_hindi"):
                    st.session_state.language = 'Hindi'
                    st.rerun()
        
        st.markdown("---")
    
    st.write(t('generate_download'))
    
    st.warning(t('bulk_note'))
    
    download_type = st.selectbox(
        t('select_type'),
        [t('question_only'), t('answer_only'), t('question_then_answer')]
    )
    
    # Language selection for bulk download
    audio_lang = st.radio(
        "Audio Language",
        ["English", "Hindi"],
        horizontal=True
    )
    
    # Limit for Streamlit Cloud (timeouts)
    max_cards = min(20, len(st.session_state.cards))
    
    if st.button(t('generate_package'), type="primary"):
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
                        
                        for i, card in enumerate(st.session_state.cards[:max_cards]):
                            # Update progress
                            progress = (i + 1) / max_cards
                            progress_bar.progress(progress)
                            
                            english_question, english_answer = card['english']
                            hindi_question, hindi_answer = card['hindi']
                            
                            # Generate audio based on type and language
                            if download_type == t('question_only'):
                                if audio_lang == "English":
                                    audio_bytes = text_to_speech(english_question, lang="en")
                                else:  # Hindi
                                    audio_bytes = text_to_speech(hindi_question, lang="hi")
                                
                                if audio_bytes:
                                    lang_suffix = "_en" if audio_lang == "English" else "_hi"
                                    filename = f"question_{i+1:02d}{lang_suffix}.mp3"
                                    zipf.writestr(filename, audio_bytes)
                                    processed += 1
                            
                            elif download_type == t('answer_only'):
                                if audio_lang == "English":
                                    audio_bytes = text_to_speech(english_answer, lang="en")
                                else:  # Hindi
                                    audio_bytes = text_to_speech(hindi_answer, lang="hi")
                                
                                if audio_bytes:
                                    lang_suffix = "_en" if audio_lang == "English" else "_hi"
                                    filename = f"answer_{i+1:02d}{lang_suffix}.mp3"
                                    zipf.writestr(filename, audio_bytes)
                                    processed += 1
                            
                            elif download_type == t('question_then_answer'):
                                if audio_lang == "English":
                                    audio_bytes = generate_combined_audio(english_question, english_answer, lang="en")
                                else:  # Hindi
                                    audio_bytes = generate_combined_audio(hindi_question, hindi_answer, lang="hi")
                                
                                if audio_bytes:
                                    lang_suffix = "_en" if audio_lang == "English" else "_hi"
                                    filename = f"flashcard_{i+1:02d}_qa{lang_suffix}.mp3"
                                    zipf.writestr(filename, audio_bytes)
                                    processed += 1
                        
                        progress_bar.empty()
                    
                    # Read the zip file
                    with open(zip_path, 'rb') as f:
                        zip_data = f.read()
                    
                    # Provide download link
                    b64_zip = base64.b64encode(zip_data).decode()
                    href = f'<a href="data:application/zip;base64,{b64_zip}" download="{zip_filename}" style="text-decoration:none;">'
                    st.markdown(f'{href}<button style="background-color:#2196F3; color:white; padding:10px 20px; border:none; border-radius:5px; font-size:16px; cursor:pointer;">⬇️ {t("downloading")} ({processed} files)</button></a>', unsafe_allow_html=True)
                    
                    st.success(f"✅ {t('generated_files')}")
                    st.info(t('zip_info'))
                    
            except Exception as e:
                st.error(f"Error generating download package: {e}")
                st.info("This might be due to timeout or memory limits on Streamlit Cloud.")

# ⚙️ Settings tab
def show_settings():
    st.subheader(t('settings'))
    
    # TOP MENU LANGUAGE SWITCH BUTTONS for Settings page too
    with st.container():
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.markdown(f"### {t('current_language')}: **{t('english') if st.session_state.language == 'English' else t('hindi')}**")
        
        with col2:
            st.markdown("### 🌐")
        
        with col3:
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                if st.button(f"🇺🇸 {t('english')}", 
                           type="primary" if st.session_state.language == 'English' else "secondary",
                           use_container_width=True,
                           key="settings_switch_to_english"):
                    st.session_state.language = 'English'
                    st.rerun()
            
            with btn_col2:
                if st.button(f"🇮🇳 {t('hindi')}", 
                           type="primary" if st.session_state.language == 'Hindi' else "secondary",
                           use_container_width=True,
                           key="settings_switch_to_hindi"):
                    st.session_state.language = 'Hindi'
                    st.rerun()
        
        st.markdown("---")
    
    if st.session_state.cards:
        st.success(f"✅ {t('loaded_cards')} {len(st.session_state.cards)}")
    else:
        st.error(t('no_cards_loaded'))
    
    # Display document info
    with st.expander(t('document_info')):
        st.write(f"**{t('document_path')}:** {DOC_PATH}")
        st.write(f"**{t('file_exists')}:** {'✅ Yes' if os.path.exists(DOC_PATH) else '❌ No'}")
        if st.session_state.cards:
            st.write(f"**{t('sample_cards')}:**")
            for i, card in enumerate(st.session_state.cards[:3]):
                english_q, english_a = card['english']
                hindi_q, hindi_a = card['hindi']
                st.write(f"{i+1}. **English Q:** {english_q[:50]}...")
                st.write(f"   **English A:** {english_a[:50]}...")
                st.write(f"   **Hindi Q:** {hindi_q[:50]}...")
                st.write(f"   **Hindi A:** {hindi_a[:50]}...")
                st.write("---")
    
    # Language statistics
    with st.expander("🌐 Language Statistics"):
        st.write(f"**Current display language:** {st.session_state.language}")
        st.write(f"**Show translation:** {'✅ Yes' if st.session_state.show_hindi else '❌ No'}")
        st.write(f"**Total bilingual cards:** {len(st.session_state.cards)}")
        
        # Count cards with proper Hindi translations
        hindi_cards = sum(1 for card in st.session_state.cards if card['hindi'][0] != card['english'][0])
        st.write(f"**Cards with Hindi translations:** {hindi_cards}")
    
    # Reset button
    if st.button(t('reset_state')):
        for key in list(st.session_state.keys()):
            if key not in ['language', 'show_hindi']:  # Keep language settings
                del st.session_state[key]
        st.rerun()
    
    # About section
    with st.expander(t('about_app')):
        st.write("""
        **LLB Preparation Flashcards with Voiceover (Bilingual)**
        
        This bilingual app helps you study for LLB exams in both English and Hindi:
        - Interactive flashcards with voice support in both languages
        - Quiz mode for self-testing
        - Audio generation for auditory learning in English and Hindi
        - Bulk download of study materials
        - Easy language switching with top menu buttons
        
        **Features:**
        - 📚 Flashcards with Q&A format in English & Hindi
        - 🔊 Text-to-speech for questions and answers in both languages
        - 🔁 Looping audio with stop controls
        - 📝 Interactive quiz with scoring in both languages
        - 📥 Bulk audio download in multiple languages
        - 🌐 Easy language switching with top menu buttons
        - ⚙️ Easy document loading
        
        **Requirements:**
        - Word document with bilingual Q&A format
        - Internet connection for audio generation
        - Modern web browser
        """)

# 🚀 Run the app
def main():
    # Set page config
    st.set_page_config(
        page_title="LLB Preparation Flashcards (Bilingual)",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Sidebar info
    with st.sidebar:
        st.title(t('sidebar_title'))
        st.markdown("---")
        st.info(t('sidebar_info'))
        
        if st.session_state.cards:
            st.success(f"**{len(st.session_state.cards)} {t('cards_loaded')}**")
        else:
            st.warning("No cards loaded")
        
        # Language indicator in sidebar
        st.markdown("---")
        st.markdown(f"**{t('current_language')}:**")
        if st.session_state.language == 'English':
            st.markdown("🇺🇸 **English**")
        else:
            st.markdown("🇮🇳 **हिंदी**")
        
        st.markdown("---")
        st.caption(t('made_with'))
    
    # Create tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs([f"🎴 {t('flashcards')}", f"📝 {t('quiz')}", f"📥 {t('download')}", f"⚙️ {t('settings_tab')}"])
    
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