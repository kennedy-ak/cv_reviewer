import streamlit as st
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import PyPDF2
import docx
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="CV Reviewer Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown("""
<style>
    .main {
        padding: 2rem 3rem;
        background-color: #f8f9fa;
    }
    h1 {
        color: #2c3e50;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    h2 {
        color: #3498db;
        font-size: 1.8rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
    .upload-section {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    .footer {
        margin-top: 3rem;
        text-align: center;
        color: #7f8c8d;
        font-size: 0.8rem;
    }
    .feature-box {
        background-color: #f1f9ff;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #3498db;
    }
    .success-box {
        background-color: #eafbea;
        padding: 2rem;
        border-radius: 10px;
        border-left: 4px solid #2ecc71;
        margin-bottom: 2rem;
    }
    .review-box {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .info-text {
        color: #7f8c8d;
        font-size: 0.9rem;
    }
    /* Customize file uploader */
    .uploadedFile {
        border: 2px dashed #3498db !important;
        border-radius: 8px !important;
        padding: 1.5rem !important;
    }
    /* Progress bar color */
    .stProgress > div > div {
        background-color: #3498db;
    }
</style>
""", unsafe_allow_html=True)


col1, col2 = st.columns([3, 1])
with col1:
    st.title("📄 NeuroReview Pro")
    st.markdown("<p class='info-text'>Get expert AI feedback on your CV to stand out in the job market</p>", unsafe_allow_html=True)


st.markdown("<div class='feature-box'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 🔍 Professional Analysis")
    st.markdown("In-depth review of your CV structure, content, and formatting")
with col2:
    st.markdown("### 🎯 Job-Specific Feedback")
    st.markdown("Customized recommendations for your target role")
with col3:
    st.markdown("### ⚡️ Fast Results")
    st.markdown("Receive your review within minutes")

st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<div class='upload-section'>", unsafe_allow_html=True)
st.subheader("📤 Upload Your CV")


if 'review_completed' not in st.session_state:
    st.session_state.review_completed = False
if 'review_content' not in st.session_state:
    st.session_state.review_content = ""

# File uploader with instructions
st.markdown("**Step 1:** Upload your CV file (PDF or DOCX format)")
uploaded_file = st.file_uploader("", type=["pdf", "docx"], label_visibility="collapsed")

if uploaded_file:
    file_details = {"Filename": uploaded_file.name, "File size": f"{uploaded_file.size / 1024:.2f} KB"}
    st.success(f"✓ File uploaded: **{uploaded_file.name}**")

# Email input with explanation
st.markdown("**Step 2:** Enter your email address to receive the review")
email_placeholder = "your.email@example.com"
email = st.text_input("", placeholder=email_placeholder, label_visibility="collapsed")

# Optional job role input
st.markdown("**Step 3:** Specify the job role (optional)")
job_role_checkbox = st.checkbox("I want targeted feedback for a specific job role")
job_role = None
if job_role_checkbox:
    job_role = st.text_input("Job title", placeholder="e.g., Software Engineer, Marketing Manager, Data Analyst")

# Submit button
submit_button = st.button("📋 Review My CV")
st.markdown("</div>", unsafe_allow_html=True)

# Function to extract text from PDF
def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

# Function to extract text from DOCX
def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {str(e)}")
        return ""

# Email sending function (same as before)
def send_email(recipient_email, subject, body):
    """
    Send an email with improved error handling and debugging.
    Supports both TLS (port 587) and SSL (port 465) connections.
    """
    try:
        # Get email credentials from environment variables
        sender_email = st.secrets["EMAIL_USER"]
        password = st.secrets["EMAIL_PASSWORD"]
        smtp_server = st.secrets["SMTP_SERVER"]
        smtp_port = int(st.secrets["SMTP_PORT"])
        
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        
        # Add body to email
        message.attach(MIMEText(body, "html"))
        
        with st.spinner("Connecting to email server..."):
            # Try different connection methods based on port
            try:
                # For port 587 (TLS)
                if smtp_port == 587:
                    server = smtplib.SMTP(smtp_server, smtp_port, timeout=15)
                    server.set_debuglevel(1)  # Enable debug output
                    server.ehlo()  # Identify with the server
                    server.starttls()
                    server.ehlo()  # Re-identify after TLS
                    server.login(sender_email, password)
                
                # For port 465 (SSL)
                elif smtp_port == 465:
                    server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=15)
                    server.set_debuglevel(1)  # Enable debug output
                    server.login(sender_email, password)
                
                # Fallback for other ports
                else:
                    server = smtplib.SMTP(smtp_server, smtp_port, timeout=15)
                    server.set_debuglevel(1)
                    
                    # Try both with and without TLS
                    try:
                        server.starttls()
                    except:
                        pass
                    
                    server.login(sender_email, password)
                
                # Send the email
                server.send_message(message)
                server.quit()
                
                return True
                
            except smtplib.SMTPServerDisconnected as e:
                # Try alternative connection method
                if smtp_port == 587:
                    # Try SSL connection
                    server = smtplib.SMTP_SSL(smtp_server, 465, timeout=15)
                    server.login(sender_email, password)
                    server.send_message(message)
                    server.quit()
                    return True
                else:
                    raise
                    
        # Various exception handlers omitted for brevity - same as your original function
                
    except Exception as e:
        st.error(f"Email delivery error: {str(e)}")
        if hasattr(e, 'smtp_code') and hasattr(e, 'smtp_error'):
            st.error(f"SMTP Code: {e.smtp_code}, SMTP Error: {e.smtp_error}")
        return False

# Function to initialize Groq client
@st.cache_resource
def get_groq_client():
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        if not api_key:
            st.error("GROQ_API_KEY not found in environment variables.")
            return None
        
        client = Groq(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"Error initializing Groq client: {str(e)}")
        return None

# Function to review CV using Groq
def review_cv(cv_text, job_role=None):
    try:
        client = get_groq_client()
        
        if not client:
            return "Failed to initialize the Groq client. Please check your API key and try again."
        
        # Prepare system and user message based on whether job role is provided
        if job_role:
            system_message = (
                "You are a professional CV reviewer and career coach. "
                f"Provide a detailed analysis of the CV for a {job_role} position. Focus on: "
                "1. Overall structure and formatting, "
                f"2. Content relevance for the {job_role} position, "
                "3. Skills assessment compared to job requirements, "
                "4. Experience highlights and gaps, "
                "5. Specific improvement suggestions, "
        
                "Format your response in clear sections with HTML formatting using h2 tags for section headers, "
                "bullet points for lists, and highlight important points. Use a professional and constructive tone."
            )
            
            user_message = f"Here is the CV content for a {job_role} position:\n\n{cv_text}"
        else:
            system_message = (
                "You are a professional CV reviewer and career coach. "
                "Provide a detailed analysis of the CV. Focus on: "
                "1. Overall structure and formatting, "
                "2. Content quality and clarity, "
                "3. Skills presentation, "
                "4. Experience highlights, "
                "5. Specific improvement suggestions, "
                
                "Format your response in clear sections with HTML formatting using h2 tags for section headers, "
                "bullet points for lists, and highlight important points. Use a professional and constructive tone."
            )
            
            user_message = f"Here is the CV content:\n\n{cv_text}"
        
        # Choose the model
        model = "llama-3.3-70b-versatile"
        
        # Create progress bar
        progress_bar = st.progress(0)
        st.markdown("<p class='info-text'>Analyzing your CV with AI...</p>", unsafe_allow_html=True)
        
        # Update progress
        progress_bar.progress(30)
        
        # Generate review
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            model=model,
            temperature=0.7,
            max_tokens=1500,
            top_p=0.9
        )
        
        # Update progress
        progress_bar.progress(100)
        
        # Extract the response
        review = chat_completion.choices[0].message.content
        
        return review
    
    except Exception as e:
        st.error(f"Error during CV review: {str(e)}")
        return "An error occurred during the review process. Please try again later."

# Process submission
if submit_button:
    if not uploaded_file:
        st.error("⚠️ Please upload your CV.")
    elif not email or "@" not in email or "." not in email:
        st.error("⚠️ Please enter a valid email address.")
    elif job_role_checkbox and not job_role:
        st.error("⚠️ Please specify the job role or uncheck the option.")
    else:
        with st.spinner("Processing your CV..."):
            # Extract text from CV
            file_extension = uploaded_file.name.split(".")[-1].lower()
            if file_extension == "pdf":
                cv_text = extract_text_from_pdf(uploaded_file)
            elif file_extension == "docx":
                cv_text = extract_text_from_docx(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload a PDF or DOCX file.")
                st.stop()
            
            if cv_text:
                # Review the CV
                review_result = review_cv(cv_text, job_role)
                
                # Store the review content in session state
                st.session_state.review_content = review_result
                
                # Send email
                email_subject = "Your CV Review Results from CV Reviewer Pro"
                email_body = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                        h2 {{ color: #3498db; margin-top: 25px; border-left: 4px solid #3498db; padding-left: 10px; }}
                        ul {{ padding-left: 20px; }}
                        li {{ margin-bottom: 8px; }}
                        .highlight {{ background-color: #f1f9ff; padding: 15px; border-radius: 5px; }}
                        .footer {{ margin-top: 40px; font-size: 12px; color: #7f8c8d; text-align: center; }}
                        .button {{ display: inline-block; background-color: #3498db; color: white; padding: 10px 20px; 
                                  text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Your CV Review Results</h1>
                        <p>Thank you for using CV Reviewer Pro. Here is your personalized CV assessment:</p>
                        
                        {review_result}
                        
                        <div class="highlight">
                            <h2>Next Steps</h2>
                            <p>Consider implementing these suggestions to strengthen your CV. After revisions, you may want to:</p>
                            <ul>
                                <li>Ask a colleague or mentor to review your updated CV</li>
                                <li>Tailor your CV further for each specific job application</li>
                                <li>Update your LinkedIn profile to match your improved CV</li>
                            </ul>
                        </div>
                        
                        <div class="footer">
                            <p>This review was generated using AI and should be considered as suggestions. 
                            For more personalized advice, consider consulting with a career coach.</p>
                            <p>&copy; 2025 CV Reviewer Pro | Powered by Groq</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                # Send the email
                email_sent = send_email(email, email_subject, email_body)
                
                if email_sent:
                    st.session_state.review_completed = True
                else:
                    st.error("⚠️ We couldn't send the email. Your review is available below, but you won't receive it by email.")
                    st.session_state.review_completed = True  # Still show the review
            else:
                st.error("⚠️ Could not extract text from the uploaded file. Please try again with a different file.")

# Display success message and review preview if review is completed
if st.session_state.review_completed:
    st.markdown("<div class='success-box'>", unsafe_allow_html=True)
    st.success("✅ CV review completed!")
    
    if 'review_content' in st.session_state and st.session_state.review_content:
        st.markdown("### Your CV Assessment")
        st.markdown("Here's a preview of the review that was sent to your email:")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='review-box'>", unsafe_allow_html=True)
        st.markdown(st.session_state.review_content, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Download option and reset button
    col1, col2 = st.columns(2)
    
    with col2:
        if st.button("🔄 Submit Another CV"):
            st.session_state.review_completed = False
            st.session_state.review_content = ""
            st.rerun()

# FAQ Section
if not st.session_state.review_completed:
    with st.expander("❓ Frequently Asked Questions"):
        st.markdown("""
        **How does NeuroReview Pro work?**  
        The application uses advanced AI to analyze your CV and provide professional feedback on structure, content, and relevance to your target role.
        
        **Is my data secure?**  
        Yes, I  do not store your CV or personal information. After processing, all data is deleted .
        
        **How long does the review take?**  
        Most reviews are completed within 1-2 minutes, depending on the length and complexity of your CV.
        
        **What file formats are supported?**  
        Currently, we support PDF and DOCX formats. For best results, ensure your file is text-based (not scanned).
        
        **Why should I specify a job role?**  
        Providing a specific job role allows our AI to customize feedback for that position, highlighting relevant skills and suggesting targeted improvements.
        """)

    # Tips Section
    with st.expander("💡 Tips for a Great CV"):
        st.markdown("""
        - **Keep it concise**: Aim for 1-2 pages maximum
        - **Use keywords**: Include industry-specific terms relevant to your target role
        - **Quantify achievements**: Use numbers and percentages to demonstrate impact
        - **Focus on recent experience**: Emphasize your most recent and relevant positions
        - **Check formatting**: Ensure consistent fonts, spacing, and bullet points
        - **Proofread carefully**: Eliminate spelling and grammatical errors
        - **Use action verbs**: Start bullet points with impactful verbs like "achieved," "delivered," or "implemented"
        """)

# Footer
st.markdown("<div class='footer'>", unsafe_allow_html=True)
st.markdown("**NeuroReview Pro** © 2025 | Powered by Groq | Built by Kennedy | ")
st.markdown("</div>", unsafe_allow_html=True)