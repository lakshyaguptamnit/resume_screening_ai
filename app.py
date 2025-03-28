from flask import Flask, render_template, request, send_from_directory
import os
import fitz  # PyMuPDF for PDF text extraction

app = Flask(__name__)

# Create an 'uploads' folder to store resumes
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define required skills for different job roles
JOB_ROLE_SKILLS = {
    "Data Scientist": {"python", "machine learning", "deep learning", "pandas", "numpy"},
    "Web Developer": {"html", "css", "javascript", "react", "flask"},
    "AI Engineer": {"python", "tensorflow", "pytorch", "nlp", "computer vision"},
    "Software Engineer": {"java", "c++", "data structures", "algorithms", "sql"}
}

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf_document:
        for page in pdf_document:
            text += page.get_text("text") + "\n"
    return text.lower()  # Convert text to lowercase for case-insensitive matching

# Function to check for required skills based on job role
def match_skills(resume_text, job_role):
    required_skills = JOB_ROLE_SKILLS.get(job_role, set())
    found_skills = {skill for skill in required_skills if skill in resume_text}
    missing_skills = required_skills - found_skills

    # Calculate score (percentage of skills matched)
    total_skills = len(required_skills)
    score = (len(found_skills) / total_skills) * 100 if total_skills > 0 else 0

    return found_skills, missing_skills, round(score, 2)

@app.route('/', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        if 'resume' not in request.files:
            return "No file uploaded"
        
        file = request.files['resume']
        job_role = request.form.get("job_role")  # Capture selected job role

        if file.filename == '':
            return "No selected file"
        
        if file and job_role:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            filename = file.filename

            # Extract text from uploaded resume
            extracted_text = extract_text_from_pdf(file_path)

            # Match skills and get score (FIXED function call)
            found_skills, missing_skills, score = match_skills(extracted_text, job_role)

            return render_template("result.html", 
                                   found_skills=found_skills, 
                                   missing_skills=missing_skills, 
                                   score=score, 
                                   filename=filename, 
                                   job_role=job_role)  # Pass job role to template
    
    return render_template('upload.html')


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
