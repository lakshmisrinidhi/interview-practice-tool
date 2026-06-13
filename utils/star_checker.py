from google import genai
import os

def check_star_method(answer):
    """Check if answer follows STAR method"""
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = f"""
    Analyze if this interview answer follows the STAR method.
    
    Answer:
    {answer}
    
    Check for these components:
    - Situation: Does it describe the context/background?
    - Task: Does it explain the responsibility/challenge?
    - Action: Does it describe specific actions taken?
    - Result: Does it mention the outcome/impact?
    
    Respond in EXACTLY this format:
    SITUATION: [YES or NO] - [one line explanation]
    TASK: [YES or NO] - [one line explanation]
    ACTION: [YES or NO] - [one line explanation]
    RESULT: [YES or NO] - [one line explanation]
    STAR_SCORE: [score out of 10]
    TIP: [one specific tip to improve the STAR structure]
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    
    return parse_star(response.text)

def parse_star(text):
    """Parse STAR analysis response"""
    
    result = {
        "situation": {"present": False, "explanation": ""},
        "task": {"present": False, "explanation": ""},
        "action": {"present": False, "explanation": ""},
        "result": {"present": False, "explanation": ""},
        "star_score": 0,
        "tip": ""
    }
    
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("SITUATION:"):
            content = line.replace("SITUATION:", "").strip()
            result["situation"]["present"] = "YES" in content.upper()
            result["situation"]["explanation"] = content.split("-", 1)[-1].strip() if "-" in content else content
            
        elif line.startswith("TASK:"):
            content = line.replace("TASK:", "").strip()
            result["task"]["present"] = "YES" in content.upper()
            result["task"]["explanation"] = content.split("-", 1)[-1].strip() if "-" in content else content
            
        elif line.startswith("ACTION:"):
            content = line.replace("ACTION:", "").strip()
            result["action"]["present"] = "YES" in content.upper()
            result["action"]["explanation"] = content.split("-", 1)[-1].strip() if "-" in content else content
            
        elif line.startswith("RESULT:"):
            content = line.replace("RESULT:", "").strip()
            result["result"]["present"] = "YES" in content.upper()
            result["result"]["explanation"] = content.split("-", 1)[-1].strip() if "-" in content else content
            
        elif line.startswith("STAR_SCORE:"):
            try:
                result["star_score"] = int(line.replace("STAR_SCORE:", "").strip().split("/")[0])
            except:
                result["star_score"] = 5
                
        elif line.startswith("TIP:"):
            result["tip"] = line.replace("TIP:", "").strip()
    
    return result