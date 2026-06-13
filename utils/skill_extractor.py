import spacy

# Load English language model
nlp = spacy.load("en_core_web_sm")

# Common tech skills list
TECH_SKILLS = [
    "python", "java", "javascript", "c++", "c#", "ruby", "swift", "kotlin",
    "html", "css", "react", "angular", "vue", "node.js", "django", "flask",
    "machine learning", "deep learning", "artificial intelligence", "nlp",
    "natural language processing", "computer vision", "data science",
    "tensorflow", "pytorch", "keras", "scikit-learn", "opencv",
    "sql", "mysql", "postgresql", "mongodb", "sqlite", "redis",
    "aws", "azure", "google cloud", "docker", "kubernetes", "git",
    "pandas", "numpy", "matplotlib", "seaborn", "plotly",
    "excel", "power bi", "tableau", "hadoop", "spark",
    "android", "ios", "flutter", "react native",
    "linux", "bash", "rest api", "graphql", "microservices"
]

def extract_skills(resume_text):
    """Extract skills from resume text"""
    resume_lower = resume_text.lower()
    found_skills = []

    for skill in TECH_SKILLS:
        if skill in resume_lower:
            found_skills.append(skill.title())

    return list(set(found_skills))  # Remove duplicates