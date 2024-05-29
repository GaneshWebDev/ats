import fitz  # PyMuPDF, imported as fitz for backward compatibility reasons
from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        # Read the uploaded PDF file
        file_bytes = uploaded_file.read()
        
        # Save the uploaded file temporarily
        with open("temp.pdf", "wb") as temp_pdf:
            temp_pdf.write(file_bytes)
        
        # Open the document using PyMuPDF (fitz)
        doc = fitz.open("temp.pdf")
        images = []
        
        for i, page in enumerate(doc):
            pix = page.get_pixmap()  # render page to an image
            
            # Save the image to a file
            image_path = f"page_{i}.png"
            pix.save(image_path)
            
            # Read the image file as bytes
            with open(image_path, "rb") as img_file:
                img_byte_arr = img_file.read()
                images.append(img_byte_arr)
            
            # Delete the temporary image file
            os.remove(image_path)
        
        # Use the first page for processing
        first_page = images[0]
        
        # Convert to bytes and encode to base64
        pdf_parts = [
            {
                "mime_type": "image/png",
                "data": base64.b64encode(first_page).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit App
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")
input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

submit1 = st.button("Tell Me About the Resume")
submit3 = st.button("Percentage Match")

input_prompt1 = """
 You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description.
 Please share your professional evaluation on whether the candidate's profile aligns with the role.
 Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
Your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
the job description. First, the output should come as a percentage, then keywords missing, and finally, final thoughts.
"""

if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload the resume")

elif submit3:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt3, pdf_content, input_text)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload the resume")
