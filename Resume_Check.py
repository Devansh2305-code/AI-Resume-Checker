import fitz
import ollama
import json
import re

def extract_text_from_pdf(pdf_path):
    with fitz.open(pdf_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

def screen_resume(resume_text, job_description):
    prompt = f"""
    You are a Senior Technical Recruiter with 20 years of experience. 
    Your goal is to objectively evaluate a candidate based on a Job Description (JD).
    
    JOB DESCRIPTION:
    {job_description}
    
    CANDIDATE RESUME:
    {resume_text}
    
    TASK:
    Analyze the resume against the JD. Look for key skills, experience levels, and project relevance.
    Be strict but fair. "React" matches "React.js". "AWS" matches "Amazon Web Services".
    
    OUTPUT FORMAT:
    Provide the response in valid JSON format only. Do not add any conversational text.
    structure:
    {{
        "candidate_name": "extracted name",
        "match_score": "0-100",
        "key_strengths": ["list of 3 key strengths"],
        "missing_critical_skills": ["list of missing skills"],
        "recommendation": "Interview" or "Reject",
        "reasoning": "A 2-sentence summary of why."
    }}
    """
    
    try:
        response = ollama.chat(model='llama3.2:1b', messages=[
            {'role': 'user', 'content': prompt},
        ])
        return response['message']['content']
    except Exception as e:
        print(f"Error communicating with Ollama: {e}")
        return "{}"

job_description = """
We are looking for a Junior Data Analyst.
Must have:
- Python (Pandas, NumPy, Scikit-Learn)
- Experience with SQL
- Basic understanding of Machine Learning algorithms
- Good communication skills
- Power BI
- EXCEL
Nice to have:
- Experience with AWS or Cloud deployment
- Knowledge of NLP
"""

try:
    resume_text = extract_text_from_pdf("Resume_DevanshJain.pdf")
    print(f"Resume loaded. Length: {len(resume_text)} characters.")
except Exception as e:
    print(f"Error loading resume: {e}")
    exit()

print("AI is analyzing the candidate... (this may take a few seconds on local hardware)")
result_json_string = screen_resume(resume_text, job_description)

try:
    # Use regex to find the JSON object within the response, handling potential conversational text
    match = re.search(r'\{.*\}', result_json_string, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in LLM response.")

    result_data = json.loads(match.group(0))
    
    print("\n--- SCREENING REPORT ---")
    print(f"Candidate: {result_data.get('candidate_name', 'Unknown')}")
    print(f"Score: {result_data.get('match_score', 'N/A')}/100")
    print(f"Decision: {result_data.get('recommendation', 'Unknown').upper()}")
    print(f"Reasoning: {result_data.get('reasoning', 'No reasoning provided')}")
    print(f"Missing Skills: {', '.join(result_data.get('missing_critical_skills', []))}")
    
except (json.JSONDecodeError, ValueError) as e:
    print(f"Failed to parse JSON: {e}")
    print(result_json_string)