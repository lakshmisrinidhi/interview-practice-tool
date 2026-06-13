from google import genai
import os

def generate_questions(resume_text, skills, mode="Technical", num_questions=5):
    """Generate interview questions based on resume and skills"""
    
    # Configure Gemini
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    skills_str = ", ".join(skills) if skills else "General Skills"
    
    if mode == "Technical":
        prompt = f"""
        You are an expert technical interviewer.
        
        Based on this resume:
        {resume_text}
        
        And these skills: {skills_str}
        
        Generate exactly {num_questions} technical interview questions.
        
        Rules:
        - Questions must be specific to the candidate's actual projects and skills
        - Mix of easy, medium and hard questions
        - Focus on real practical knowledge
        
        Format your response exactly like this:
        1. [Question here]
        2. [Question here]
        3. [Question here]
        4. [Question here]
        5. [Question here]
        """
    else:
        prompt = f"""
        You are an expert HR interviewer.
        
        Based on this resume:
        {resume_text}
        
        Generate exactly {num_questions} HR interview questions.
        
        Rules:
        - Focus on personality, communication, teamwork
        - Include behavioral questions
        - Include situational questions
        
        Format your response exactly like this:
        1. [Question here]
        2. [Question here]
        3. [Question here]
        4. [Question here]
        5. [Question here]
        """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    
    # Parse questions from response
    lines = response.text.strip().split("\n")
    questions = []
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit() and "." in line:
            question = line.split(".", 1)[1].strip()
            questions.append(question)
    
    return questions