# import streamlit as st
# import os
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# import PyPDF2
# import docx
# import pandas as pd
# from transformers import AutoTokenizer, AutoModelForCausalLM
# import torch
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Configure page
# st.set_page_config(
#     page_title="CV Reviewer",
#     page_icon="📝",
#     layout="centered"
# )

# # App title and description
# st.title("CV Reviewer")
# st.markdown("""
# Upload your CV and get a professional review sent to your email.
# Optionally, specify the job role you're applying for to receive targeted feedback.
# """)

# # Initialize session state variables if they don't exist
# if 'review_completed' not in st.session_state:
#     st.session_state.review_completed = False
# if 'review_content' not in st.session_state:
#     st.session_state.review_content = ""

# # Function to extract text from PDF
# def extract_text_from_pdf(file):
#     try:
#         pdf_reader = PyPDF2.PdfReader(file)
#         text = ""
#         for page in pdf_reader.pages:
#             text += page.extract_text()
#         return text
#     except Exception as e:
#         st.error(f"Error extracting text from PDF: {str(e)}")
#         return ""

# # Function to extract text from DOCX
# def extract_text_from_docx(file):
#     try:
#         doc = docx.Document(file)
#         text = ""
#         for para in doc.paragraphs:
#             text += para.text + "\n"
#         return text
#     except Exception as e:
#         st.error(f"Error extracting text from DOCX: {str(e)}")
#         return ""

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

# # Function to load and use LLaMA 4 model for CV review
# @st.cache_resource
# def load_llama_model():
#     try:
#         model_name = "meta-llama/Llama-4-8B-Instruct"
#         tokenizer = AutoTokenizer.from_pretrained(model_name)
#         model = AutoModelForCausalLM.from_pretrained(
#             model_name,
#             torch_dtype=torch.bfloat16,
#             device_map="auto"
#         )
#         return model, tokenizer
#     except Exception as e:
#         st.error(f"Error loading LLaMA model: {str(e)}")
#         return None, None

# # Function to review CV using LLaMA 4
# def review_cv(cv_text, job_role=None):
#     try:
#         model, tokenizer = load_llama_model()
        
#         if not model or not tokenizer:
#             return "Failed to load the language model. Please try again later."
        
#         # Prepare prompt based on whether job role is provided
#         if job_role:
#             prompt = f"""
#             <|system|>
#             You are a professional CV reviewer and career coach. Provide a detailed analysis of the following CV for a {job_role} position. Focus on:
#             1. Overall structure and formatting
#             2. Content relevance for the {job_role} position
#             3. Skills assessment compared to job requirements
#             4. Experience highlights and gaps
#             5. Specific improvement suggestions
#             6. ATS optimization tips
#             Format your response in clear sections with HTML formatting.
#             </|system|>
            
#             <|user|>
#             Here is the CV content:
#             {cv_text}
            
#             Please review this CV for a {job_role} position.
#             </|user|>
            
#             <|assistant|>
#             """
#         else:
#             prompt = f"""
#             <|system|>
#             You are a professional CV reviewer and career coach. Provide a detailed analysis of the following CV. Focus on:
#             1. Overall structure and formatting
#             2. Content quality and clarity
#             3. Skills presentation
#             4. Experience highlights
#             5. Specific improvement suggestions
#             6. ATS optimization tips
#             Format your response in clear sections with HTML formatting.
#             </|system|>
            
#             <|user|>
#             Here is the CV content:
#             {cv_text}
            
#             Please provide a comprehensive review of this CV.
#             </|user|>
            
#             <|assistant|>
#             """
            
#         # Generate review
#         inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
#         outputs = model.generate(
#             inputs.input_ids,
#             max_new_tokens=1500,
#             temperature=0.7,
#             top_p=0.9,
#             repetition_penalty=1.2,
#             do_sample=True
#         )
        
#         review = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
#         # Extract only the assistant's response (remove the prompt)
#         assistant_response = review.split("<|assistant|>")[-1].strip()
        
#         return assistant_response
    
#     except Exception as e:
#         st.error(f"Error during CV review: {str(e)}")
#         return "An error occurred during the review process. Please try again later."

# # File uploader
# uploaded_file = st.file_uploader("Upload your CV (PDF or DOCX)", type=["pdf", "docx"])

# # Email input
# email = st.text_input("Your Email Address")

# # Optional job role input
# job_role_checkbox = st.checkbox("I want to specify the job role I'm applying for")
# job_role = None
# if job_role_checkbox:
#     job_role = st.text_input("Job Role/Position")

# # Submit button
# if st.button("Review My CV"):
#     if not uploaded_file:
#         st.error("Please upload your CV.")
#     elif not email or "@" not in email or "." not in email:
#         st.error("Please enter a valid email address.")
#     elif job_role_checkbox and not job_role:
#         st.error("Please specify the job role or uncheck the option.")
#     else:
#         with st.spinner("Analyzing your CV..."):
#             # Extract text from CV
#             file_extension = uploaded_file.name.split(".")[-1].lower()
#             if file_extension == "pdf":
#                 cv_text = extract_text_from_pdf(uploaded_file)
#             elif file_extension == "docx":
#                 cv_text = extract_text_from_docx(uploaded_file)
#             else:
#                 st.error("Unsupported file format. Please upload a PDF or DOCX file.")
#                 st.stop()
            
#             if cv_text:
#                 # Review the CV
#                 review_result = review_cv(cv_text, job_role)
                
#                 # Store the review content in session state
#                 st.session_state.review_content = review_result
                
#                 # Send email
#                 email_subject = "Your CV Review Results"
#                 email_body = f"""
#                 <html>
#                 <head>
#                     <style>
#                         body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
#                         .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
#                         h1 {{ color: #2c3e50; }}
#                         h2 {{ color: #3498db; margin-top: 20px; }}
#                         .footer {{ margin-top: 30px; font-size: 12px; color: #7f8c8d; }}
#                     </style>
#                 </head>
#                 <body>
#                     <div class="container">
#                         <h1>Your CV Review Results</h1>
#                         <p>Thank you for using our CV Review service. Here is your personalized CV review:</p>
                        
#                         {review_result}
                        
#                         <div class="footer">
#                             <p>This review was generated using AI and should be considered as suggestions. For more personalized advice, consider consulting with a career coach.</p>
#                         </div>
#                     </div>
#                 </body>
#                 </html>
#                 """
                
#                 # Send the email
#                 email_sent = send_email(email, email_subject, email_body)
                
#                 if email_sent:
#                     st.session_state.review_completed = True
#                 else:
#                     st.error("Failed to send email. Please check your email address and try again.")
#             else:
#                 st.error("Could not extract text from the uploaded file. Please try again with a different file.")

# # Display success message and review preview if review is completed
# if st.session_state.review_completed:
#     st.success("CV review completed! The results have been sent to your email.")
    
#     with st.expander("Preview Review", expanded=True):
#         st.markdown(st.session_state.review_content, unsafe_allow_html=True)
    
#     # Reset button
#     if st.button("Submit Another CV"):
#         st.session_state.review_completed = False
#         st.session_state.review_content = ""
#         st.experimental_rerun()

# # Footer
# st.markdown("---")
# st.markdown("CV Reviewer © 2025 | Powered by Meta LLaMA 4")