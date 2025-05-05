#!/usr/bin/env python3

import os
import glob
import PyPDF2
import litellm
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file (for API keys)
load_dotenv()

class MatchlyEngine:
    def __init__(self, api_key=None):
        """Initialize the Matchly Engine with OpenAI API key."""
        # Use API key from args, env var, or .env file
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set it as an environment variable OPENAI_API_KEY or pass it as an argument.")
        
        # Set the API key for litellm
        os.environ["OPENAI_API_KEY"] = self.api_key
        
    def extract_text_from_pdf(self, pdf_path):
        """Extract text content from a PDF file, treating each page as a separate resume."""
        resumes = []
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page_text = pdf_reader.pages[page_num].extract_text()
                    resumes.append({
                        'source_file': os.path.basename(pdf_path),
                        'page': page_num + 1,
                        'content': page_text
                    })
            return resumes
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return []
    
    def get_resumes(self, data_folder="data"):
        """Get all resumes from the data folder, treating each page as a separate resume."""
        resumes = []
        # Look for PDF files in the data folder
        pdf_files = glob.glob(os.path.join(data_folder, "*.pdf"))
        
        for pdf_file in pdf_files:
            pdf_resumes = self.extract_text_from_pdf(pdf_file)
            resumes.extend(pdf_resumes)
            
        return resumes
    
    def match_resume_to_job(self, job_description, resumes, model="gpt-3.5-turbo"):
        """Match resumes to job description using LiteLLM."""
        # Prepare resumes as context
        resume_texts = [f"Resume {i+1} (File: {resume['source_file']}, Page: {resume['page']}):\n{resume['content']}" 
                        for i, resume in enumerate(resumes)]
        
        # Combine all resumes with job description in the prompt
        prompt = f"""Job Description:
{job_description}

I have the following resumes:
{''.join(resume_texts)}

Based on the job description, rank these resumes from best to worst match. 
Provide a score from 0-100 for each resume and explain the reasoning. 
Format your response as:
1. Resume X (File: filename, Page: Y) - Score: XX/100 - [Brief explanation]
2. Resume Z (File: filename, Page: W) - Score: XX/100 - [Brief explanation]
And so on...
"""
        
        try:
            # Use litellm with proper configuration
            response = litellm.completion(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional HR assistant that specializes in matching resumes to job descriptions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error matching resumes to job: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Matchly Engine - Match resumes to job descriptions")
    parser.add_argument("--data-folder", default="data", help="Folder containing resume PDFs")
    parser.add_argument("--job-description", help="Job description text or file path")
    parser.add_argument("--api-key", help="OpenAI API key")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="Model to use (default: gpt-3.5-turbo)")
    
    args = parser.parse_args()
    
    # Initialize Matchly Engine
    engine = MatchlyEngine(api_key=args.api_key)
    
    # Get resumes
    resumes = engine.get_resumes(args.data_folder)
    resumes = resumes[:10]
    if not resumes:
        print(f"No PDF resumes found in {args.data_folder}. Please add some resume PDFs and try again.")
        return
    
    print(f"Found {len(resumes)} resumes across {len(set(r['source_file'] for r in resumes))} PDF files:")
    for i, resume in enumerate(resumes):
        print(f"- Resume {i+1}: {resume['source_file']} (Page {resume['page']})")
    
    # Get job description
    job_description = args.job_description
    if not job_description:
        job_description = input("Please enter the job description: ")
    elif os.path.isfile(job_description):
        with open(job_description, 'r') as file:
            job_description = file.read()
    
    # Match resumes to job description
    result = engine.match_resume_to_job(job_description, resumes, model=args.model)
    
    print("\nMatching Results:")
    print(result)

if __name__ == "__main__":
    main() 