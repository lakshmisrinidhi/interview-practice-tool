from google import genai
import os

def evaluate_answer(question, answer, resume_text):
    """Evaluate candidate's answer and give score + feedback"""
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = f"""
    You are an expert interview coach evaluating a candidate's answer.
    
    Resume Context:
    {resume_text}
    
    Interview Question:
    {question}
    
    Candidate's Answer:
    {answer}
    
    Evaluate the answer and respond in EXACTLY this format:
    
    CLARITY: [score out of 10]
    TECHNICAL_DEPTH: [score out of 10]
    COMMUNICATION: [score out of 10]
    OVERALL: [score out of 10]
    
    STRENGTHS:
    [2-3 things the candidate did well]
    
    IMPROVEMENTS:
    [2-3 specific suggestions to improve the answer]
    
    IDEAL_ANSWER:
    [A brief example of what a strong answer would include]
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    
    return parse_evaluation(response.text)

def parse_evaluation(text):
    """Parse AI response into structured data"""
    
    result = {
        "clarity": 0,
        "technical_depth": 0,
        "communication": 0,
        "overall": 0,
        "strengths": "",
        "improvements": "",
        "ideal_answer": ""
    }
    
    lines = text.strip().split("\n")
    current_section = None
    section_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("CLARITY:"):
            try:
                result["clarity"] = int(line.split(":")[1].strip().split("/")[0])
            except:
                result["clarity"] = 7
                
        elif line.startswith("TECHNICAL_DEPTH:"):
            try:
                result["technical_depth"] = int(line.split(":")[1].strip().split("/")[0])
            except:
                result["technical_depth"] = 7
                
        elif line.startswith("COMMUNICATION:"):
            try:
                result["communication"] = int(line.split(":")[1].strip().split("/")[0])
            except:
                result["communication"] = 7
                
        elif line.startswith("OVERALL:"):
            try:
                result["overall"] = int(line.split(":")[1].strip().split("/")[0])
            except:
                result["overall"] = 7
                
        elif line == "STRENGTHS:":
            current_section = "strengths"
            section_lines = []
            
        elif line == "IMPROVEMENTS:":
            if current_section == "strengths":
                result["strengths"] = " ".join(section_lines)
            current_section = "improvements"
            section_lines = []
            
        elif line == "IDEAL_ANSWER:":
            if current_section == "improvements":
                result["improvements"] = " ".join(section_lines)
            current_section = "ideal_answer"
            section_lines = []
            
        else:
            if current_section:
                section_lines.append(line)
    
    # Save last section
    if current_section == "ideal_answer":
        result["ideal_answer"] = " ".join(section_lines)
    
    return result