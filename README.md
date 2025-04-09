# CV Reviewer Application

This is a Streamlit application that uses Meta's LLaMA 4 model to review CVs/resumes and send feedback via email.

## Features

- Upload CV/resume files (PDF or DOCX)
- Provide email for receiving review results
- Optional job role specification for targeted feedback
- AI-powered CV analysis using Meta LLaMA 4
- Email delivery of review results

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/cv-reviewer.git
cd cv-reviewer
```

### 2. Set up a Python virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root directory with the following content:

```
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**Notes for Gmail users:**
- You'll need to generate an app password
- Go to your Google Account > Security > App passwords
- Generate a new app password for your application

### 5. Hugging Face authentication

You'll need to authenticate with Hugging Face to use the LLaMA 4 model:

```bash
huggingface-cli login
```

Enter your Hugging Face token when prompted. Make sure you have access to the Meta LLaMA 4 model.

### 6. Run the application

```bash
streamlit run app.py
```

The application will be available at http://localhost:8501

## Usage

1. Upload your CV/resume (PDF or DOCX format)
2. Enter your email address
3. Optionally specify the job role you're applying for
4. Click "Review My CV"
5. Wait for the analysis to complete
6. Check your email for the detailed review results

## Technologies Used

- Streamlit for the web interface
- Meta LLaMA 4 for AI-powered CV analysis
- PyPDF2 and python-docx for file processing
- SMTP for email delivery

## Customization

You can modify the prompt templates in the `review_cv` function to customize the review criteria and output format.