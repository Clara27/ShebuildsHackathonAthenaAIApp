import streamlit as st
import google.generativeai as genai
import PyPDF2
import io
import time
from datetime import datetime
from gtts import gTTS
import base64
from docx import Document


st.markdown("<h1 style='text-align: center;'> 📋 Summarize Genie </h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'> Summarize Text and Read aloud! </h3>", unsafe_allow_html=True)
# Custom CSS for styling
st.markdown(
"""
    <style>
    /* Main background and text colors */
    .stApp {
        background: linear-gradient(135deg, #81334C, #81334C);
        color: #ffffff;
    }

    /* Headings */
    h1, h2, h3 {
        color: #ffffff !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    /* Paragraphs */
    p {
        font-size: 1.1em;
        line-height: 1.6;
    }

    /* Links */
    a {
        color: #FFB6C1 !important;
        text-decoration: none;
        transition: all 0.3s ease;
    }

    a:hover {
        color: #FFC0CB !important;
        text-decoration: underline;
    }

    /* Buttons */
    .stButton > button {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        font-size: 1em;
        padding: 10px 20px;
    }

    .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* Spacing */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 3rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
def read_docx(file):
    """Extract text from DOCX file"""
    try:
        doc = Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
        return None

def text_to_speech(text, lang='en'):
    """Convert text to speech and return HTML audio player"""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        audio_base64 = base64.b64encode(audio_buffer.read()).decode()
        audio_player = f'<audio controls autoplay="false"><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
        return audio_player
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return None

def init_gemini(api_key):
    """Initialize Gemini AI with the provided API key"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        return model
    except Exception as e:
        st.error(f"Error initializing Gemini: {str(e)}")
        return None

def read_pdf(file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def summarize_text(model, text, summary_type):
    """Generate summary using Gemini AI based on summary type"""
    try:
        if summary_type == "Brief":
            prompt = f"Please provide a very concise summary (2-3 sentences) of the following text:\n\n{text}"
        elif summary_type == "Detailed":
            prompt = f"Please provide a detailed summary with key points of the following text:\n\n{text}"
        else:  # Bullet Points
            prompt = f"Please summarize the following text in bullet points (5-7 points):\n\n{text}"
            
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

def count_words(text):
    """Count words in text"""
    return len(text.split())

def main():
    # Clean header without container
    # st.markdown(
        # """
        # <h1 class="main-title">
            # <span class="icon">📋</span>
            # Summarize Genie
        # </h1>
        # <h3 class="subtitle">Summarize Text and Read aloud!</h3>
        # """,
        # unsafe_allow_html=True
    # )
    
    if 'model' not in st.session_state:
        st.session_state.model = None

    api_key = st.text_input(
        "Enter your Gemini API Key:",
        type="password"
    )
    
    if api_key and st.session_state.model is None:
        st.session_state.model = init_gemini(api_key)

    input_method = st.radio(
        "Choose input method:",
        ["Text Input", "File Upload"]
    )
    
    text_content = None
    
    if input_method == "Text Input":
        text_content = st.text_area(
            "Enter your text:",
            height=200
        )
        if text_content:
            st.info(f"Word count: {count_words(text_content)}")
            
    else:
        uploaded_file = st.file_uploader(
            "Upload a file",
            type=['txt', 'pdf', 'docx'],
            help="Upload a TXT, PDF, or DOCX file"
        )
        
        if uploaded_file is not None:
            try:
                with st.spinner("Processing file..."):
                    if uploaded_file.type == "application/pdf":
                        text_content = read_pdf(uploaded_file)
                    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        text_content = read_docx(io.BytesIO(uploaded_file.read()))
                    else:  # txt file
                        text_content = uploaded_file.getvalue().decode("utf-8")
                
                if text_content:
                    st.success(f"Successfully processed {uploaded_file.name}")
                    st.info(f"Word count: {count_words(text_content)}")
                    with st.expander("Show extracted text"):
                        st.text(text_content)
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    # Language selection for TTS
    language = st.selectbox(
        "Select Language for Text-to-Speech",
        ["English", "Hindi", "Spanish", "French", "German"],
        index=0
    )
    
    # Language code mapping
    lang_codes = {
        "English": "en", "Hindi": "hi", "Spanish": "es",
        "French": "fr", "German": "de"
    }
    
    summary_type = st.select_slider(
        "Select Summary Type",
        options=["Brief", "Detailed", "Bullet Points"],
        value="Brief"
    )
    
    if text_content and st.session_state.model and st.button("Generate Summary"):
        with st.spinner("Generating summary..."):
            start_time = time.time()
            summary = summarize_text(st.session_state.model, text_content, summary_type)
            end_time = time.time()
            
            if summary:
                processing_time = round(end_time - start_time, 2)
                st.success(f"Summary generated in {processing_time} seconds")
                
                st.subheader("Summary")
                st.write(summary)
                
                # Text-to-Speech
                st.subheader("Listen to Summary")
                with st.spinner("Generating audio..."):
                    audio_player = text_to_speech(summary, lang_codes[language])
                    if audio_player:
                        st.markdown(audio_player, unsafe_allow_html=True)
                
                # Download button
                st.download_button(
                    label="Download Summary (Text)",
                    data=summary,
                    file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

if __name__ == "__main__":
    main()