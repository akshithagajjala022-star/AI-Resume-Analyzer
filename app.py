from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
import os
import requests

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_ai_analysis(resume_text, job_description):
    try:
        prompt = f"""
You are an expert resume reviewer.

Analyze the candidate's resume against the given job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Provide a concise professional analysis with these sections:

1. Overall Assessment
2. Key Strengths
3. Missing or Weak Areas
4. Improvement Suggestions
5. Interview Preparation Advice

Base the analysis only on the information provided.
Do not invent qualifications or experience.
"""

        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data.get("response", "").strip()

    except Exception as e:
        return f"AI analysis could not be generated: {str(e)}"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze_resume():

    if "resume" not in request.files:
        return jsonify({"error": "No resume uploaded."}), 400

    resume = request.files["resume"]
    job_description = request.form.get("job_description", "")

    if resume.filename == "":
        return jsonify({"error": "Please select a resume PDF."}), 400

    if not job_description.strip():
        return jsonify({"error": "Please enter a job description."}), 400

    try:
        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            resume.filename
        )

        resume.save(file_path)

        reader = PdfReader(file_path)

        page_count = len(reader.pages)

        resume_text = ""

        for page in reader.pages:
            text = page.extract_text()

            if text:
                resume_text += text + " "

        resume_text = resume_text.lower()
        job_text = job_description.lower()

        skills = [
    # Programming Languages
    "python",
    "java",
    "c",
    "c++",
    "c#",
    "javascript",
    "typescript",
    "php",
    "ruby",
    "go",
    "kotlin",
    "swift",

    # Web Development
    "html",
    "css",
    "react",
    "angular",
    "vue",
    "node.js",
    "express.js",
    "django",
    "flask",
    "fastapi",

    # Databases
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "oracle",
    "redis",

    # AI and Machine Learning
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "natural language processing",
    "nlp",
    "computer vision",
    "tensorflow",
    "pytorch",
    "scikit-learn",

    # Data Science
    "data analysis",
    "data science",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "excel",
    "power bi",
    "tableau",

    # Cloud
    "aws",
    "amazon web services",
    "microsoft azure",
    "azure",
    "google cloud",
    "gcp",

    # DevOps and Tools
    "git",
    "github",
    "gitlab",
    "docker",
    "kubernetes",
    "jenkins",

    # Other Technical Skills
    "rest api",
    "api",
    "json",
    "linux",
    "cybersecurity",
    "cloud computing",

    # General Professional Skills
    "communication",
    "leadership",
    "teamwork",
    "problem solving",
    "project management"
]

        detected_skills = [
            skill for skill in skills
            if skill in resume_text
        ]

        job_skills = [
            skill for skill in skills
            if skill in job_text
        ]

        matching_skills = [
            skill for skill in job_skills
            if skill in detected_skills
        ]

        missing_skills = [
            skill for skill in job_skills
            if skill not in detected_skills
        ]

        role_skills = {
            "Python Developer": [
                "python",
                "django",
                "flask",
                "fastapi",
                "sql"
            ],

            "Web Developer": [
                "html",
                "css",
                "javascript",
                "react",
                "angular",
                "node.js"
            ],

            "Data Analyst": [
                "python",
                "sql",
                "excel",
                "pandas",
                "numpy",
                "power bi",
                "tableau",
                "data analysis"
            ],

            "AI / ML Engineer": [
                "python",
                "machine learning",
                "deep learning",
                "tensorflow",
                "pytorch",
                "scikit-learn",
                "artificial intelligence"
            ],

            "Data Scientist": [
                "python",
                "machine learning",
                "pandas",
                "numpy",
                "sql",
                "data science",
                "statistics"
            ]
        }

        role_scores = {}

        for role, required_skills in role_skills.items():

            matched = sum(
                1 for skill in required_skills
                if skill in detected_skills
            )

            role_scores[role] = matched

        recommended_role = max(
            role_scores,
            key=role_scores.get
        )

        if job_skills:
            match_percentage = round(
                (len(matching_skills) / len(job_skills)) * 100
            )
        else:
            match_percentage = 0

        strengths = []

        if matching_skills:
            strengths.append(
                "Your resume contains relevant skills for this job."
            )

        if len(detected_skills) >= 5:
            strengths.append(
                "Your resume demonstrates a good range of technical skills."
            )

        if "project" in resume_text or "projects" in resume_text:
            strengths.append(
                "Your resume includes project experience."
            )

        if not strengths:
            strengths.append(
                "Your resume provides a starting point for improvement."
            )

        suggestions = []

        if missing_skills:
            suggestions.append(
                "Consider adding experience or projects related to: "
                + ", ".join(missing_skills)
            )

        if "project" not in resume_text and "projects" not in resume_text:
            suggestions.append(
                "Consider adding relevant academic or personal projects."
            )

        if "experience" not in resume_text:
            suggestions.append(
                "Consider clearly describing your practical experience."
            )

        if not suggestions:
            suggestions.append(
                "Continue improving your resume with measurable achievements."
            )

        return jsonify({
            "filename": resume.filename,
            "page_count": page_count,
            "recommended_role": recommended_role,
            "match_percentage": match_percentage,
            "detected_skills": detected_skills,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "strengths": strengths,
            "suggestions": suggestions
        })

    except Exception as e:

        return jsonify({
            "error": "Could not analyze the resume.",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
