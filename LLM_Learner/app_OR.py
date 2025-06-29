import streamlit as st
from datetime import datetime
import os
from typing import List, Dict
import base64
import requests
import json

# Enable file handling imports
import PyPDF2
import io
import docx

# Configure the page
st.set_page_config(
    page_title="",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []


if "hf_api_key" not in st.session_state:
    st.session_state.hf_api_key = ""

# File upload functionality (currently disabled)
# def extract_text_from_file(uploaded_file):
#     """Extract text from uploaded file"""
#     try:
#         if uploaded_file.type == "text/plain":
#             # Handle plain text files
#             return str(uploaded_file.read(), "utf-8")
#         elif uploaded_file.type == "application/pdf":
#             # Handle PDF files
#             pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
#             text = ""
#             for page in pdf_reader.pages:
#                 text += page.extract_text() + "\n"
#             return text
#         else:
#             return f"File type {uploaded_file.type} is not supported. Please upload a .txt or .pdf file."
#     except Exception as e:
#         return f"Error reading file: {str(e)}"


def get_llm_response(messages: List[Dict[str, str]]) -> str:
    """Get response from OpenRouter LLM (Gemma 3n)"""
    try:
        api_key = st.session_state.openrouter_api_key.strip() if "openrouter_api_key" in st.session_state else None
        if not api_key:
            return "Error: Please enter your OpenRouter API key in the sidebar."
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # Optionally add Referer and X-Title if you want
        }
        payload = {
            "model": "google/gemma-3n-e4b-it:free",
            "messages": [
                {"role": m["role"], "content": m["content"]} for m in messages
            ]
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code != 200:
            return f"Error: {response.status_code} - {response.text}"
        data = response.json()
        # OpenRouter returns choices[0].message.content
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        import traceback
        return f"Error: {str(e)}\nTraceback:\n{traceback.format_exc()}"

def add_message(role: str, content: str):
    """Add message to chat history"""
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

def clear_chat():
    """Clear chat history"""
    st.session_state.messages = []

# Add this function at the top of your file
def get_img_tag(image_path, width=16):
    """Convert an image file to a data URL for embedding in HTML"""
    try:
        with open(image_path, "rb") as img_file:
            img_data = base64.b64encode(img_file.read()).decode()
            return f'<img src="data:image/png;base64,{img_data}" width="{width}" style="vertical-align:middle;margin-right:8px">'
    except Exception as e:
        # Return empty string if file not found
        print(f"Icon not found: {e}")
        return ""

# Sidebar with instruction buttons and settings
with st.sidebar:
    st.title("🎓 Learning Tools")
    
    # Navigation Section - Collapsible
    with st.expander("Navigation", expanded=True):
        nav_labels = [
            ("Next Concept", "Move to the next learning concept or topic in the current subject area:"),
            ("Previous Concept", "Return to the previous learning concept or topic we covered:"),
            ("Concept History", "List all the concepts and topics we have navigated through in our learning session:")  # Remove HTML tag
        ]

        for i, (short_label, instruction) in enumerate(nav_labels):
            if st.button(short_label, key=f"nav_btn_{i}", help=f"Navigation: {short_label}", use_container_width=True):
                if "current_input" not in st.session_state:
                    st.session_state.current_input = ""
                st.session_state.current_input = instruction + " "
                st.rerun()
    
    # Teaching Methods Section - Collapsible
    with st.expander("Teaching Methods", expanded=True):
        learning_labels = [
            ("Syllabus", "Provide a Table of Content based on relevancy for the current Concept:"),
            ("Analogy", "Compare new concepts to familiar things the student already knows to make complex ideas easier to understand:"),
            ("Chunk", "Break large amounts of information into smaller, manageable pieces that are easier to process and remember:"),
            ("Big Picture", "Start with the overall concept or framework before diving into details, helping students see how pieces fit together:"),
            ("Jargon", "Identify and clearly explain specialized terminology, replacing complex language with simpler alternatives when possible:"),
            ("Memory", "Use memory aids like acronyms, rhymes, or visual associations to help students remember key information:"),
            ("Visual", "Encourage visualization and mental imagery to help students create vivid mental representations of concepts:"),
            ("Rephrase", "Express the same information in different ways to reinforce understanding and accommodate different learning preferences:")
        ]

        for i, (short_label, instruction) in enumerate(learning_labels):
            if st.button(short_label, key=f"learn_btn_{i}", help=f"Learning Strategy: {short_label}", use_container_width=True):
                if "current_input" not in st.session_state:
                    st.session_state.current_input = ""
                st.session_state.current_input = instruction + " "
                st.rerun()
    
    # Assessment Strategies Section - Collapsible
    with st.expander("Assessment Methods", expanded=True):
        assessment_labels = [
            ("Multiple Choice", "Present questions with several answer options to test recognition and understanding:"),
            ("True/False", "Create simple binary questions that test basic comprehension of facts or concepts:"),
            (" Matching", "Connect related items, terms, or concepts to test understanding of relationships:"),
            ("Fill-in Blanks", "Test recall by having students complete sentences or phrases with missing key terms:"),
            ("Short Response", "Brief written answers that require students to explain concepts in their own words:"),
            (" Error Spotting", "Present incorrect information for students to identify and correct, testing critical thinking:"),
            ("Deep Thinking", "Open-ended questions that require analysis, synthesis, or evaluation of complex concepts:"),
            ("Tutor Mode", "I will now act as the teacher, you should act like a student and help me understand:")
        ]

        for i, (short_label, instruction) in enumerate(assessment_labels):
            if st.button(short_label, key=f"assess_btn_{i}", help=f"Assessment Strategy: {short_label}", use_container_width=True):
                if "current_input" not in st.session_state:
                    st.session_state.current_input = ""
                st.session_state.current_input = instruction + " "
                st.rerun()
    
    st.divider()

# Add custom CSS for Google Gemini-inspired styling
st.markdown("""
<style>
/* Global app styling */
.stApp {
    background: linear-gradient(135deg, #f0f4ff 0%, #fafbff 100%) !important;
}

.main .block-container {
    max-width: none !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* Main content area styling */

/* Chat container styling - Gemini-inspired */
.chat-container {
    max-width: 1000px !important;
    margin: 0 auto !important;
    background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%) !important;
    border-radius: 24px !important;
    padding: 24px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06) !important;
    border: 1px solid #e8eaed !important;
}

/* Chat messages styling - Gemini-inspired */
.stChatMessage {
    border-radius: 18px !important;
    margin: 12px 0 !important;
    max-width: 90% !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
}

/* User message styling - Gemini blue */
.stChatMessage[data-testid="chat-message-user"] {
    background: linear-gradient(135deg, #4285f4 0%, #1a73e8 100%) !important;
    color: white !important;
    margin-left: auto !important;
    margin-right: 0 !important;
}

/* Assistant message styling - Gemini light */
.stChatMessage[data-testid="chat-message-assistant"] {
    background: linear-gradient(135deg, #f8faff 0%, #ffffff 100%) !important;
    border: 1px solid #e8eaed !important;
    color: #3c4043 !important;
    margin-left: 0 !important;
    margin-right: auto !important;
}

/* Form styling - Gemini-inspired with full width */
.stForm {
    max-width: none !important;
    width: 100% !important;
    margin: 20px 0 !important;
    background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%) !important;
    border-radius: 20px !important;
    padding: 20px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
    border: 1px solid #e8eaed !important;
}

/* Text area styling - Gemini-inspired */
.stTextArea textarea {
    border-radius: 16px !important;
    border: 2px solid #e8eaed !important;
    padding: 16px !important;
    background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%) !important;
    color: #3c4043 !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

.stTextArea textarea:focus {
    border-color: #4285f4 !important;
    box-shadow: 0 0 0 3px rgba(66, 133, 244, 0.1) !important;
    background: #ffffff !important;
    outline: none !important;
}

/* Send button styling - Gemini blue */
.stFormSubmitButton button {
    border-radius: 12px !important;
    padding: 8px 16px !important;
    font-weight: 500 !important;
    background: linear-gradient(135deg, #4285f4 0%, #1a73e8 100%) !important;
    color: white !important;
    border: none !important;
    font-size: 13px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 6px rgba(66, 133, 244, 0.2) !important;
    height: 36px !important;
    min-height: 36px !important;
}

.stFormSubmitButton button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(66, 133, 244, 0.3) !important;
    background: linear-gradient(135deg, #1a73e8 0%, #1557b0 100%) !important;
}

/* Dropdown styling for attachment */
.stSelectbox {
    margin: 0 !important;
    width: 100% !important;
}

.stSelectbox > div > div {
    border-radius: 8px !important;
    border: 1px solid #e8eaed !important;
    background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%) !important;
    min-height: 32px !important;
    font-size: 12px !important;
}

.stSelectbox > div > div:hover {
    border-color: #4285f4 !important;
}

.stSelectbox label {
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #4285f4 !important;
}

/* File uploader styling - only when shown */
.stFileUploader {
    margin: 8px 0 !important;
    width: 100% !important;
}

.stFileUploader > div {
    background: linear-gradient(135deg, #f8faff 0%, #ffffff 100%) !important;
    border: 2px dashed #e8eaed !important;
    border-radius: 12px !important;
    padding: 16px !important;
    text-align: center !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

.stFileUploader > div:hover {
    border-color: #4285f4 !important;
    background: linear-gradient(135deg, #ffffff 0%, #f1f5ff 100%) !important;
}

.stFileUploader label {
    color: #3c4043 !important;
    font-weight: 500 !important;
    font-size: 14px !important;
}

/* Section headers - Gemini styling */
h3 {
    color: #3c4043 !important;
    font-weight: 600 !important;
    font-size: 20px !important;
    margin-bottom: 16px !important;
    text-align: center !important;
}

/* Sidebar styling - Gemini-inspired with better button support */
.css-1d391kg {
    background: linear-gradient(135deg, #f8faff 0%, #ffffff 100%) !important;
    border-right: 1px solid #e8eaed !important;
    width: 350px !important;  /* Wide sidebar for buttons */
    min-width: 350px !important;
}

/* Hide sidebar collapse button to make it fixed - multiple selectors */
button[kind="header"] {
    display: none !important;
}

/* Hide the sidebar toggle button with various selectors */
.css-1rs6os {
    display: none !important;
}

button[data-testid="collapsedControl"] {
    display: none !important;
}

button[data-testid="baseButton-header"] {
    display: none !important;
}

.css-1544g2n {
    display: none !important;
}

.css-1cypcdb {
    display: none !important;
}

/* Hide any button that contains chevron or arrow icons */
button svg[data-testid*="chevron"] {
    display: none !important;
}

button svg[data-testid*="arrow"] {
    display: none !important;
}

/* Hide the entire header area where collapse button sits */
.css-1avcm0n {
    display: none !important;
}

/* Ensure sidebar stays fixed */
.css-1d391kg {
    position: fixed !important;
    height: 100vh !important;
    overflow-y: auto !important;
}

/* Sidebar buttons - full width and properly styled */
.css-1d391kg .stButton > button {
    width: 100% !important;
    min-width: 100% !important;
    max-width: 100% !important;
    height: 40px !important;
    min-height: 40px !important;
    max-height: 40px !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
    padding: 8px 12px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    text-align: left !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    box-sizing: border-box !important;
    background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%) !important;
    border: 1px solid #e8eaed !important;
    color: #3c4043 !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 3px rgba(60, 64, 67, 0.06) !important;
    margin-bottom: 4px !important;
}

.css-1d391kg .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(66, 133, 244, 0.15) !important;
    border-color: #4285f4 !important;
    background: linear-gradient(135deg, #ffffff 0%, #f1f5ff 100%) !important;
}

/* Icon styling for all sidebar buttons */

/* Navigation Icons - Add the history icon directly here */
button[key="nav_btn_2"] {
    background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJDNi40NzcgMiAyIDYuNDc3IDIgMTJTNi40NzcgMjIgMTIgMjIgMjIgMTcuNTIzIDIyIDEyIDE3LjUyMyAyIDEyIDJaTTEyIDIwQzcuNTg5IDIwIDQgMTYuNDExIDQgMTJTNy41ODkgNCA0IDEyIDEyIDIwIDEyIDIwWk0xMSA3SDEzVjEyLjQxNEwxNS4yOTMgMTQuNzA3TDE0LjU4NiAxNS40MTRMMTJGMTNEMDY3WiIgZmlsbD0iIzMzMzMzMyIvPgo8L3N2Zz4K') !important;
    background-size: 16px 16px !important;
    background-repeat: no-repeat !important;
    background-position: 8px center !important;
    padding-left: 32px !important;
}
</style>

<script>
// JavaScript to hide sidebar collapse button after page loads
document.addEventListener('DOMContentLoaded', function() {
    function hideSidebarToggle() {
        // Try multiple selectors to find and hide the toggle button
        const selectors = [
            'button[kind="header"]',
            'button[data-testid="collapsedControl"]',
            'button[data-testid="baseButton-header"]',
            '.css-1rs6os',
            '.css-1544g2n',
            '.css-1cypcdb',
            '.css-1avcm0n',
            'button[aria-label*="collapse"]',
            'button[aria-label*="expand"]'
        ];
        
        selectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                el.style.display = 'none';
                el.style.visibility = 'hidden';
            });
        });
        
        // Also hide any buttons with chevron/arrow icons in sidebar area
        const allButtons = document.querySelectorAll('button');
        allButtons.forEach(button => {
            const svg = button.querySelector('svg');
            if (svg && (svg.innerHTML.includes('chevron') || svg.innerHTML.includes('arrow'))) {
                // Check if this looks like a sidebar toggle
                const rect = button.getBoundingClientRect();
                if (rect.left < 100) { // Likely in sidebar area
                    button.style.display = 'none';
                }
            }
        });
    }
    
    // Run immediately and also with delays to catch dynamically loaded content
    hideSidebarToggle();
    setTimeout(hideSidebarToggle, 100);
    setTimeout(hideSidebarToggle, 500);
    setTimeout(hideSidebarToggle, 1000);
    
    // Set up observer to catch future DOM changes
    const observer = new MutationObserver(hideSidebarToggle);
    observer.observe(document.body, { childList: true, subtree: true });
});
</script>
""", unsafe_allow_html=True)

# Welcome message above chat
st.markdown("<h1 style='text-align: center; color: #4285f4; font-weight: 600; font-size: 28px; margin: 32px 0 24px 0;'>Welcome to Gemma 3n Learner</h1>", unsafe_allow_html=True)

# Chat container - using streamlit's native width
chat_container = st.container()

# Display chat messages
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            st.caption(f"🕒 {message['timestamp']}")

# Chat input
if "current_input" not in st.session_state:
    st.session_state.current_input = ""

# Use a form for chat input
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_area(
        "Your message:",
        value=st.session_state.current_input,
        height=100,
        placeholder="What would you like to learn about today?",
        label_visibility="collapsed"
    )
    
    col3, col4, col5 = st.columns([1, 1, 2])
    with col3:
        submit_button = st.form_submit_button("Send")
    with col4:
        clear_input = st.form_submit_button("Clear")

# File attachment section - right below the chat form (no separator)
with st.expander("📎 Attach Syllabus ", expanded=False):
    uploaded_file_expanded = st.file_uploader(
        "Upload a file",
        type=['txt', 'pdf', 'docx'],
        help="Upload any supported file type"
    )
    
    # Display uploaded file info
    if uploaded_file_expanded:
        st.success(f"✅ **File uploaded:** {uploaded_file_expanded.name}")
        st.info(f"📁 **File size:** {uploaded_file_expanded.size} bytes")
        st.info(f"📋 **File type:** {uploaded_file_expanded.type}")
        
        # File details without nested expander
        st.markdown("**📋 File Details:**")
        st.write(f"• **Name:** {uploaded_file_expanded.name}")
        st.write(f"• **Size:** {uploaded_file_expanded.size} bytes")
        st.write(f"• **Type:** {uploaded_file_expanded.type}")

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file (.txt, .pdf, .docx)"""
    try:
        if uploaded_file.type == "text/plain":
            return str(uploaded_file.read(), "utf-8")
        elif uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text if text else "No extractable text found in PDF."
        elif uploaded_file.type in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword"
        ] or uploaded_file.name.lower().endswith(".docx"):
            doc = docx.Document(io.BytesIO(uploaded_file.read()))
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            return f"File type {uploaded_file.type} is not supported. Please upload a .txt, .pdf, or .docx file."
    except Exception as e:
        return f"Error reading file: {str(e)}"

if submit_button and user_input.strip():
    # Add user message (include file content if uploaded)
    message_content = user_input
    if uploaded_file_expanded:
        file_text = extract_text_from_file(uploaded_file_expanded)
        # Truncate file_text if too long (to avoid LLM token limits)
        max_file_chars = 3000
        if len(file_text) > max_file_chars:
            file_text = file_text[:max_file_chars] + "\n...[truncated]..."
        message_content += f"\n\n📎 **Attached file content:**\n{file_text}"
    add_message("user", message_content)
    st.session_state.current_input = ""
    messages_for_llm = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.messages
    ]
    with st.spinner("🤔 Analyzing..."):
        response = get_llm_response(messages_for_llm)
    add_message("assistant", response)
    st.rerun()

if clear_input:
    st.session_state.current_input = ""
    st.rerun()

# Footer
st.divider()

# API Configuration as expandable section at bottom
with st.expander("Configuration", expanded=False):
    # Remove Hugging Face API key input
    # api_key = st.text_input(
    #     "Hugging Face API Key",
    #     type="password",
    #     value=st.session_state.hf_api_key,
    #     help="Enter your Hugging Face API key to use the chatbot",
    #     key="hf_api_key_input"
    # )
    # if api_key != st.session_state.hf_api_key:
    #     st.session_state.hf_api_key = api_key
    #     st.success("API key updated successfully!")

    openrouter_api_key = st.text_input(
        "OpenRouter API Key",
        type="password",
        value=st.session_state.get("openrouter_api_key", ""),
        help="Enter your OpenRouter API key to use the chatbot",
        key="openrouter_api_key_input"
    )
    if openrouter_api_key != st.session_state.get("openrouter_api_key", ""):
        st.session_state.openrouter_api_key = openrouter_api_key
        st.success("API key updated successfully!")

st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        🎓 Educational LLM Chatbot with Gemma 3n model 
    </div>
    """,
    unsafe_allow_html=True
)
