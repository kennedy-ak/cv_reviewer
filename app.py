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
import re

load_dotenv()


st.set_page_config(
    page_title="CV Reviewer Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# adding css
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


st.markdown("**Step 1:** Upload your CV file (PDF or DOCX format)")
# Fixed accessibility warning by adding a proper label
uploaded_file = st.file_uploader("Upload CV file", type=["pdf", "docx"], label_visibility="collapsed")

if uploaded_file:
    file_details = {"Filename": uploaded_file.name, "File size": f"{uploaded_file.size / 1024:.2f} KB"}
    st.success(f"✓ File uploaded: **{uploaded_file.name}**")


st.markdown("**Step 2:** Enter your email address to receive the review")
email_placeholder = "your.email@example.com"
# Fixed accessibility warning by adding a proper label
email = st.text_input("Email address", placeholder=email_placeholder, label_visibility="collapsed")


st.markdown("**Step 3:** Specify the job role (optional)")
job_role_checkbox = st.checkbox("I want targeted feedback for a specific job role")
job_role = None
if job_role_checkbox:
    job_role = st.text_input("Job title", placeholder="e.g., Software Engineer, Marketing Manager, Data Analyst")


submit_button = st.button("📋 Review My CV")
st.markdown("</div>", unsafe_allow_html=True)

# extract text from PDF
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

#  extract text from DOCX
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

# Update your send_email function to ensure CSS is properly included
def send_email(recipient_email, subject, body):
    try:
        sender_email = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASSWORD")
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT"))  # Convert port to integer
       
        # Create a MIMEMultipart message
        message = MIMEMultipart("alternative")  # Use "alternative" for HTML emails
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        
        # Attach HTML content
        # Make sure CSS is inline within the HTML tags, not in a separate style block
        message.attach(MIMEText(body, "html"))
        
        with st.spinner("Connecting to email server..."):
            try:
                # Handle different SMTP connection methods based on port
                if smtp_port == 587:
                    server = smtplib.SMTP(smtp_server, smtp_port, timeout=15)
                    server.set_debuglevel(1)  # Enable debug output
                    server.ehlo()
                    server.starttls()
                    server.ehlo() 
                    server.login(sender_email, password)
                
                elif smtp_port == 465:
                    server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=15)
                    server.set_debuglevel(1)  # Enable debug output
                    server.login(sender_email, password)
                
                else:
                    server = smtplib.SMTP(smtp_server, smtp_port, timeout=15)
                    server.set_debuglevel(1)
                    
                    try:
                        server.starttls()
                    except:
                        pass
                    
                    server.login(sender_email, password)
                
                # Send email
                server.send_message(message)
                server.quit()
                
                return True
                
            except smtplib.SMTPServerDisconnected as e:
                # Fallback to SSL if TLS fails
                if smtp_port == 587:
                    server = smtplib.SMTP_SSL(smtp_server, 465, timeout=15)
                    server.login(sender_email, password)
                    server.send_message(message)
                    server.quit()
                    return True
                else:
                    raise
                    
    except Exception as e:
        st.error(f"Email delivery error: {str(e)}")
        if hasattr(e, 'smtp_code') and hasattr(e, 'smtp_error'):
            st.error(f"SMTP Code: {e.smtp_code}, SMTP Error: {e.smtp_error}")
        return False

# Groq client
@st.cache_resource
def get_groq_client():
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            st.error("GROQ_API_KEY not found in environment variables.")
            return None
        
        client = Groq(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"Error initializing Groq client: {str(e)}")
        return None

# Improved function to format review text with proper HTML conversion
def format_review_for_email(review_text):
    """
    Process the review text to convert markdown to HTML and apply inline CSS styles
    for maximum email client compatibility
    """
    import re
    
    # Convert markdown headers to HTML headers with inline styles
    # Replace ## headers with styled h2 tags
    review_text = re.sub(
        r'## ([^\n]+)',
        r'<h2 style="color: #3498db; margin-top: 25px; border-left: 4px solid #3498db; padding-left: 10px;">\1</h2>',
        review_text
    )
    
    # Convert markdown bold (**text**) to HTML bold with inline styles
    review_text = re.sub(
        r'\*\*([^*]+)\*\*',
        r'<strong style="font-weight: bold;">\1</strong>',
        review_text
    )
    
    # Convert bullet points (* item) to HTML list items
    if "* " in review_text:
        # First, identify bullet point lists and wrap them in <ul> tags
        bullet_list_pattern = r'(\n\* [^\n]+(?:\n\* [^\n]+)*)'
        
        def replace_bullet_list(match):
            bullet_list = match.group(1)
            items = bullet_list.strip().split('\n* ')
            items = [item for item in items if item]
            
            html_list = '<ul style="padding-left: 20px;">\n'
            for item in items:
                html_list += f'<li style="margin-bottom: 8px;">{item}</li>\n'
            html_list += '</ul>'
            
            return html_list
        
        review_text = re.sub(bullet_list_pattern, replace_bullet_list, '\n' + review_text)
    
    # Add paragraph tags to text blocks
    paragraphs = review_text.split('\n\n')
    formatted_paragraphs = []
    
    for p in paragraphs:
        if not p.strip():
            continue
        if not (p.startswith('<h2') or p.startswith('<ul') or p.startswith('<li') or p.startswith('<strong')):
            p = f'<p style="margin-bottom: 15px; line-height: 1.6;">{p}</p>'
        formatted_paragraphs.append(p)
    
    review_text = '\n'.join(formatted_paragraphs)
    
    # Style percentage mentions
    percentage_pattern = r'(\d{1,3}%)'
    review_text = re.sub(
        percentage_pattern, 
        r'<span style="font-weight: bold; color: #3498db;">\1</span>', 
        review_text
    )
    
    return review_text

# Review CV using Groq with improved formatting
def review_cv(cv_text, job_role=None):
    try:
        client = get_groq_client()
        
        if not client:
            return "Failed to initialize the Groq client. Please check your API key and try again."
        
        # Create system and user message based on inputs
        if job_role:
            system_message = (
                "You are a professional CV reviewer and career coach. "
                f"Provide a detailed analysis of the CV for a {job_role} position with percentage scores. Focus on: "
                "1. Overall structure and formatting (score this out of 100%), "
                "2. Content relevance for the position (score this out of 100%), "
                "3. Skills assessment compared to job requirements (score this out of 100%), "
                "4. Experience highlights and gaps (score this out of 100%), "
                "5. Specific improvement suggestions, "
                
                "Also provide an overall CV score as a percentage based on the average of all sections. "
                
                "Format your response in clear sections with markdown formatting using ## for section headers, "
                "* for bullet points, and **bold text** for important points. Include percentages for each major section. "
                "For each section, explain the reasoning behind the score and what could be improved. "
                "Use a professional and constructive tone."
            )
            user_message = f"Here is the CV content for a {job_role} position:\n\n{cv_text}"
        else:
            system_message = (
                "You are a professional CV reviewer and career coach. "
                "Provide a detailed analysis of the CV with percentage scores. Focus on: "
                "1. Overall structure and formatting (score this out of 100%), "
                "2. Content quality and clarity (score this out of 100%), "
                "3. Skills presentation (score this out of 100%), "
                "4. Experience highlights (score this out of 100%), "
                "5. Specific improvement suggestions, "
                
                "Also provide an overall CV score as a percentage based on the average of all sections. "
                
                "Format your response in clear sections with markdown formatting using ## for section headers, "
                "* for bullet points, and **bold text** for important points. Include percentages for each major section. "
                "For each section, explain the reasoning behind the score and what could be improved. "
                "Use a professional and constructive tone."
            )
            user_message = f"Here is the CV content:\n\n{cv_text}"
        
        # Choose model
        model = "llama-3.3-70b-versatile"
        
        # Show progress bar
        progress_bar = st.progress(0)
        st.markdown("<p class='info-text'>Analyzing your CV with AI...</p>", unsafe_allow_html=True)
        
        # Update progress bar
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
        
        # Update progress bar
        progress_bar.progress(100)
        
        # Get review text
        review = chat_completion.choices[0].message.content
        
        # Format the review for email with inline styles
        formatted_review = format_review_for_email(review)
        
        return formatted_review
    
    except Exception as e:
        st.error(f"Error during CV review: {str(e)}")
        return "An error occurred during the review process. Please try again later."

# user email validation
if submit_button:
    if not uploaded_file:
        st.error("⚠️ Please upload your CV.")
    elif not email or "@" not in email or "." not in email:
        st.error("⚠️ Please enter a valid email address.")
    elif job_role_checkbox and not job_role:
        st.error("⚠️ Please specify the job role or uncheck the option.")
    else:
        with st.spinner("Processing your CV..."):
           
            file_extension = uploaded_file.name.split(".")[-1].lower()
            if file_extension == "pdf":
                cv_text = extract_text_from_pdf(uploaded_file)
            elif file_extension == "docx":
                cv_text = extract_text_from_docx(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload a PDF or DOCX file.")
                st.stop()
            
            if cv_text:
                
                review_result = review_cv(cv_text, job_role)
                
               
                st.session_state.review_content = review_result
                
                # Send email with improved template
                email_subject = "Your CV Review Results from CV Reviewer Pro"
                email_body = f"""
                <html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Your CV Review</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0;">
    <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Your CV Review Results</h1>
        <p style="margin-bottom: 15px; line-height: 1.6;">Thank you for using CV Reviewer Pro. Here is your personalized CV assessment:</p>
        
        <div style="margin-top: 20px;">
            {review_result}
        </div>
        
        <div style="background-color: #f1f9ff; padding: 15px; border-radius: 5px; margin-top: 30px;">
            <h2 style="color: #3498db; margin-top: 5px; border-left: 4px solid #3498db; padding-left: 10px;">Next Steps</h2>
            <p style="margin-bottom: 15px; line-height: 1.6;">Consider implementing these suggestions to strengthen your CV. After revisions, you may want to:</p>
            <ul style="padding-left: 20px;">
                <li style="margin-bottom: 8px;">Ask a colleague or mentor to review your updated CV</li>
                <li style="margin-bottom: 8px;">Tailor your CV further for each specific job application</li>
                <li style="margin-bottom: 8px;">Update your LinkedIn profile to match your improved CV</li>
            </ul>
        </div>
        
        <div style="margin-top: 40px; font-size: 12px; color: #7f8c8d; text-align: center;">
            <p style="margin-bottom: 15px; line-height: 1.6;">This review was generated using AI and should be considered as suggestions. 
            For more personalized advice, consider consulting with a career coach.</p>
            <p style="margin-bottom: 15px; line-height: 1.6;">&copy; 2025 CV Reviewer Pro | Powered by Groq | Built by Kennedy</p>
        </div>
    </div>
</body>
</html>
                """
                
                # Send email
                email_sent = send_email(email, email_subject, email_body)
                
                if email_sent:
                    st.session_state.review_completed = True
                else:
                    st.error("⚠️ We couldn't send the email. Your review is available below, but you won't receive it by email.")
                    st.session_state.review_completed = True  # Still show the review
            else:
                st.error("⚠️ Could not extract text from the uploaded file. Please try again with a different file.")

# Display review in app
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
        Yes, I  do not store your CV or personal information. After processing, all data is deleted.
        
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
        - **Focus on recent experience**: Stress your most recent and relevant positions
        - **Check formatting**: Ensure consistent fonts, spacing, and bullet points
        - **Proofread carefully**: Remove spelling and grammatical errors
        - **Use action verbs**: Start bullet points with impactful verbs like "achieved," "delivered," or "implemented"
        """)

# Footer
st.markdown("<div class='footer'>", unsafe_allow_html=True)
st.markdown("**NeuroReview Pro** © 2025 | Powered by Groq | Built by Kennedy | ")
st.markdown("</div>", unsafe_allow_html=True)