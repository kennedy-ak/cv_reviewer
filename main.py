
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
    page_title="CV Reviewer",
    page_icon="📝",
    layout="centered"
)

# App title and description
st.title("CV Reviewer")
st.markdown("""
Upload your CV and get a professional review sent to your email.
Optionally, specify the job role you're applying for to receive targeted feedback.
""")

# Initialize session state variables if they don't exist
if 'review_completed' not in st.session_state:
    st.session_state.review_completed = False
if 'review_content' not in st.session_state:
    st.session_state.review_content = ""

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

# # Function to send email
# def send_email(recipient_email, subject, body):
#     try:
#         # Get email credentials from environment variables
#         sender_email = os.getenv("EMAIL_USER")
#         password = os.getenv("EMAIL_PASSWORD")
#         smtp_server = os.getenv("SMTP_SERVER")
#         smtp_port = int(os.getenv("SMTP_PORT"))
        
#         # Create message
#         message = MIMEMultipart()
#         message["From"] = sender_email
#         message["To"] = recipient_email
#         message["Subject"] = subject
        
#         # Add body to email
#         message.attach(MIMEText(body, "html"))
        
#         # Connect to server and send email
#         with smtplib.SMTP(smtp_server, smtp_port) as server:
#             server.starttls()
#             server.login(sender_email, password)
#             server.send_message(message)
        
#         return True
#     except Exception as e:
#         st.error(f"Error sending email: {str(e)}")
#         return False

def send_email(recipient_email, subject, body):
    """
    Send an email with improved error handling and debugging.
    Supports both TLS (port 587) and SSL (port 465) connections.
    """
    try:
        # Get email credentials from environment variables
        sender_email = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASSWORD")
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT"))
        
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        
        # Add body to email
        message.attach(MIMEText(body, "html"))
        
        st.info(f"Attempting to connect to {smtp_server}:{smtp_port}...")
        
        # Try different connection methods based on port
        try:
            # For port 587 (TLS)
            if smtp_port == 587:
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=15)
                server.set_debuglevel(1)  # Enable debug output
                server.ehlo()  # Identify with the server
                
                st.info("Starting TLS...")
                server.starttls()
                server.ehlo()  # Re-identify after TLS
                
                st.info(f"Logging in as {sender_email}...")
                server.login(sender_email, password)
            
            # For port 465 (SSL)
            elif smtp_port == 465:
                st.info("Using SSL connection...")
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=15)
                server.set_debuglevel(1)  # Enable debug output
                
                st.info(f"Logging in as {sender_email}...")
                server.login(sender_email, password)
            
            # Fallback for other ports
            else:
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=15)
                server.set_debuglevel(1)
                
                # Try both with and without TLS
                try:
                    server.starttls()
                except:
                    st.warning("TLS not supported, continuing without encryption...")
                
                server.login(sender_email, password)
            
            # Send the email
            st.info(f"Sending email to {recipient_email}...")
            server.send_message(message)
            
            # Close the connection
            st.info("Closing connection...")
            server.quit()
            
            return True
            
        except smtplib.SMTPServerDisconnected as e:
            st.error(f"Server disconnected: {str(e)}")
            # Try alternative connection method
            if smtp_port == 587:
                st.warning("TLS connection failed. Attempting SSL connection on port 465...")
                # Store original port for error reporting
                original_port = smtp_port
                smtp_port = 465
                
                # Try SSL connection
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=15)
                server.set_debuglevel(1)
                server.login(sender_email, password)
                server.send_message(message)
                server.quit()
                
                st.success(f"Email sent successfully using SSL (port 465) after TLS (port {original_port}) failed!")
                return True
            else:
                raise
                
    except smtplib.SMTPAuthenticationError as e:
        st.error(f"Authentication failed: {str(e)}")
        st.warning("Possible causes:")
        st.warning("1. Incorrect email or password")
        st.warning("2. You need to create an App Password if using 2-factor authentication")
        st.warning("3. 'Less secure app access' might be disabled in your Google account")
        return False
        
    except smtplib.SMTPSenderRefused as e:
        st.error(f"Sender refused: {str(e)}")
        st.warning("Your email provider may have restrictions on sending emails via SMTP")
        return False
        
    except smtplib.SMTPRecipientsRefused as e:
        st.error(f"Recipients refused: {str(e)}")
        st.warning("The recipient email addresses were rejected by the server")
        return False
        
    except smtplib.SMTPConnectError as e:
        st.error(f"Connection error: {str(e)}")
        st.warning("Could not connect to the SMTP server. Check your network connection and server address.")
        return False
        
    except smtplib.SMTPHeloError as e:
        st.error(f"HELO error: {str(e)}")
        return False
        
    except smtplib.SMTPNotSupportedError as e:
        st.error(f"Not supported: {str(e)}")
        return False
        
    except smtplib.SMTPDataError as e:
        st.error(f"Data error: {str(e)}")
        return False
        
    except TimeoutError as e:
        st.error(f"Connection timed out: {str(e)}")
        st.warning("The server took too long to respond. It might be down or your network connection might be slow.")
        return False
        
    except Exception as e:
        st.error(f"Unexpected error sending email: {str(e)}")
        if hasattr(e, 'smtp_code') and hasattr(e, 'smtp_error'):
            st.error(f"SMTP Code: {e.smtp_code}, SMTP Error: {e.smtp_error}")
        return False

# Function to initialize Groq client
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
             
                "Format your response in clear sections with HTML formatting."
            )
            
            user_message = f"Here is the CV content:\n{cv_text}\n\nPlease review this CV for a {job_role} position."
        else:
            system_message = (
                "You are a professional CV reviewer and career coach. "
                "Provide a detailed analysis of the CV. Focus on: "
                "1. Overall structure and formatting, "
                "2. Content quality and clarity, "
                "3. Skills presentation, "
                "4. Experience highlights, "
                "5. Specific improvement suggestions, "
             
                "Format your response in clear sections with HTML formatting."
            )
            
            user_message = f"Here is the CV content:\n{cv_text}\n\nPlease provide a comprehensive review of this CV."
        
        # Choose the model - using LLaMA 2 70B model provided by Groq
        model = "llama-3.3-70b-versatile"
        
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
        
        # Extract the response
        review = chat_completion.choices[0].message.content
        
        return review
    
    except Exception as e:
        st.error(f"Error during CV review: {str(e)}")
        return "An error occurred during the review process. Please try again later."

# File uploader
uploaded_file = st.file_uploader("Upload your CV (PDF or DOCX)", type=["pdf", "docx"])

# Email input
email = st.text_input("Your Email Address")

# Optional job role input
job_role_checkbox = st.checkbox("I want to specify the job role I'm applying for")
job_role = None
if job_role_checkbox:
    job_role = st.text_input("Job Role/Position")

# Submit button
if st.button("Review My CV"):
    if not uploaded_file:
        st.error("Please upload your CV.")
    elif not email or "@" not in email or "." not in email:
        st.error("Please enter a valid email address.")
    elif job_role_checkbox and not job_role:
        st.error("Please specify the job role or uncheck the option.")
    else:
        with st.spinner("Analyzing your CV..."):
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
                email_subject = "Your CV Review Results"
                email_body = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                        h1 {{ color: #2c3e50; }}
                        h2 {{ color: #3498db; margin-top: 20px; }}
                        .footer {{ margin-top: 30px; font-size: 12px; color: #7f8c8d; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Your CV Review Results</h1>
                        <p>Thank you for using our CV Review service. Here is your personalized CV review:</p>
                        
                        {review_result}
                        
                        <div class="footer">
                            <p>This review was generated using AI and should be considered as suggestions. For more personalized advice, consider consulting with a career coach.</p>
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
                    st.error("Failed to send email. Please check your email address and try again.")
            else:
                st.error("Could not extract text from the uploaded file. Please try again with a different file.")

# Display success message and review preview if review is completed
if st.session_state.review_completed:
    st.success("CV review completed! The results have been sent to your email.")
    
    with st.expander("Preview Review", expanded=True):
        st.markdown(st.session_state.review_content, unsafe_allow_html=True)
    
    # Reset button
    if st.button("Submit Another CV"):
        st.session_state.review_completed = False
        st.session_state.review_content = ""
        st.rerun()

# Footer
st.markdown("---")
st.markdown("CV Reviewer © 2025 | Powered by Groq")