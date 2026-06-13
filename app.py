import streamlit as st
from dotenv import load_dotenv
import os
import pdfplumber
import plotly.graph_objects as go
from utils.skill_extractor import extract_skills
from utils.question_generator import generate_questions
from utils.answer_evaluator import evaluate_answer
from utils.star_checker import check_star_method
from database.database import save_session, get_all_sessions, get_session_count

load_dotenv()

st.set_page_config(
    page_title="Interview Practice Tool",
    page_icon="🎯",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px;
        background: #1a1a2e;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 2px solid #00ff88;
    }
    .feature-card {
        background: #1a1a2e;
        padding: 15px;
        border-radius: 8px;
        border-left: 3px solid #00ff88;
        margin: 8px 0;
    }
    .stButton>button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## My Progress")
    st.markdown("---")

    sessions = get_all_sessions()
    total = get_session_count()

    col1, col2 = st.columns(2)
    col1.metric("Sessions Done", total)
    if sessions:
        best = max(s[4] for s in sessions)
        col2.metric("Best Score", f"{best:.1f}/10")

    if sessions:
        dates = [f"Session {i+1}" for i in range(len(sessions))]
        scores = [s[4] for s in sessions]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=scores,
            mode="lines+markers",
            line=dict(color="#00ff88", width=2),
            marker=dict(size=8, color="#00ff88"),
            fill="tozeroy",
            fillcolor="rgba(0,255,136,0.1)"
        ))
        fig.update_layout(
            title="Score over time",
            yaxis=dict(range=[0, 10], gridcolor="#333"),
            xaxis=dict(gridcolor="#333"),
            height=250,
            margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white", size=11)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Recent Sessions")
        for s in reversed(sessions[-5:]):
            score = s[4]
            emoji = "🟢" if score >= 7 else "🟡" if score >= 5 else "🔴"
            st.markdown(f"{emoji} {s[1]} | {s[2]} | {score:.1f}/10")
    else:
        st.info("Complete a session to see your scores here.")

    st.markdown("---")
    st.markdown("### Quick Tips")
    tips = [
        "Use STAR format for behavioral questions",
        "Give numbers and results when possible",
        "Keep answers between 1-2 minutes",
        "Practice speaking out loud",
        "Don't memorize — understand"
    ]
    for tip in tips:
        st.markdown(f"• {tip}")

# Header
st.markdown("""
<div class="main-header">
    <h2>🎯 Interview Practice Tool</h2>
    <p>Upload your resume, get questions based on your skills, and improve your answers</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.markdown('<div class="feature-card">📄 Reads your resume</div>', unsafe_allow_html=True)
col2.markdown('<div class="feature-card">❓ Generates questions</div>', unsafe_allow_html=True)
col3.markdown('<div class="feature-card">📊 Scores your answer</div>', unsafe_allow_html=True)
col4.markdown('<div class="feature-card">📈 Tracks progress</div>', unsafe_allow_html=True)

st.markdown("---")

# Step 1
st.header("Step 1 — Upload Your Resume")
st.write("Upload your resume as a PDF. The tool will read it and generate questions based on your skills.")

uploaded_file = st.file_uploader("Select your resume (PDF)", type="pdf")

if uploaded_file is not None:
    with open(f"resumes/{uploaded_file.name}", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"Uploaded: {uploaded_file.name}")

    with pdfplumber.open(f"resumes/{uploaded_file.name}") as pdf:
        resume_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                resume_text += text

    st.session_state["resume_text"] = resume_text

    with st.expander("See extracted text from your resume"):
        st.text_area("", resume_text, height=250)

    # Step 2
    st.header("Step 2 — Skills Found")
    skills = extract_skills(resume_text)

    if skills:
        st.write(f"Found {len(skills)} skills in your resume:")
        cols = st.columns(4)
        for i, skill in enumerate(skills):
            cols[i % 4].success(f"✅ {skill}")
        st.session_state["skills"] = skills
    else:
        st.warning("No skills detected. Make sure your resume clearly lists your technologies.")
        skills = []

    st.markdown("---")

    # Step 3
    st.header("Step 3 — Pick Interview Type")
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Technical**\nQuestions about your projects, code, and skills")
    with col2:
        st.info("**HR**\nQuestions about yourself, teamwork, and goals")

    mode = st.radio("Which type of interview do you want to practice?", ["Technical", "HR"])
    num_questions = st.slider("How many questions do you want?", min_value=3, max_value=10, value=5)

    st.markdown("---")

    if st.button("Start Practice Session", type="primary", use_container_width=True):
        with st.spinner("Generating questions from your resume..."):
            try:
                questions = generate_questions(resume_text, skills, mode, num_questions)
                st.session_state["questions"] = questions
                st.session_state["mode"] = mode
                st.session_state["current_q"] = 0
                st.session_state["evaluations"] = []
                st.session_state["star_scores"] = []
                st.success("Questions ready! Scroll down.")
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")

    # Interview
    if "questions" in st.session_state and st.session_state["questions"]:
        questions = st.session_state["questions"]
        current_q = st.session_state.get("current_q", 0)

        st.markdown("---")

        col1, col2, col3 = st.columns([2, 1, 1])
        col1.header(f"Question {current_q + 1} of {len(questions)}")
        col2.metric("Type", st.session_state.get("mode", "Technical"))
        col3.metric("Done", f"{len(st.session_state.get('evaluations', []))}/{len(questions)}")

        st.progress(current_q / len(questions))
        st.markdown(f"### {questions[current_q]}")
        st.markdown("---")

        # Voice
        st.markdown("#### Answer by voice or type below")
        st.caption("Voice works in Chrome and Edge browsers only")

        voice_html = f"""
        <div style="margin: 10px 0;">
            <button onclick="startRec()" id="recBtn"
                style="background:#00ff88;color:black;border:none;
                       padding:10px 20px;border-radius:8px;
                       font-weight:bold;cursor:pointer;font-size:15px;">
                🎤 Record Answer
            </button>
            <button onclick="stopRec()" id="stopBtn"
                style="background:#ff4444;color:white;border:none;
                       padding:10px 20px;border-radius:8px;
                       font-weight:bold;cursor:pointer;font-size:15px;
                       display:none;margin-left:10px;">
                ⏹️ Stop
            </button>
            <span id="status" style="margin-left:15px;color:#aaa;font-style:italic;"></span>
            <p id="transcript" style="margin-top:10px;padding:10px;
                background:#1a1a2e;border-radius:8px;
                border-left:3px solid #00ff88;
                color:white;display:none;">
            </p>
        </div>
        <script>
        let recog = null;
        let finalTranscript = '';
        function startRec() {{
            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SR) {{ document.getElementById('status').innerText='Not supported. Use Chrome or Edge.'; return; }}
            recog = new SR();
            recog.continuous = true;
            recog.interimResults = true;
            recog.lang = 'en-US';
            finalTranscript = '';
            recog.onstart = () => {{
                document.getElementById('status').innerText='Listening...';
                document.getElementById('recBtn').style.display='none';
                document.getElementById('stopBtn').style.display='inline';
            }};
            recog.onresult = (e) => {{
                finalTranscript = '';
                for(let i=0;i<e.results.length;i++) {{
                    finalTranscript += e.results[i][0].transcript;
                }}
                let el = document.getElementById('transcript');
                el.style.display='block';
                el.innerText= finalTranscript;
            }};
            recog.onend = () => {{
                document.getElementById('status').innerText='Done! Your answer is in the box below.';
                document.getElementById('recBtn').style.display='inline';
                document.getElementById('stopBtn').style.display='none';
                const textAreas = window.parent.document.querySelectorAll('textarea');
                if (textAreas.length > 0) {{
                    let ta = textAreas[textAreas.length - 1];
                    let nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLTextAreaElement.prototype, 'value').set;
                    nativeInputValueSetter.call(ta, finalTranscript);
                    ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
            }};
            recog.start();
        }}
        function stopRec() {{ if(recog) recog.stop(); }}
        </script>
        """

        st.components.v1.html(voice_html, height=150)

        default_answer = st.session_state.get(f"voice_answer_{current_q}", "")

        answer = st.text_area(
            "Your answer:",
            height=200,
            placeholder="Type here or use the mic above. Try to be specific and give examples.",
            key=f"answer_{current_q}",
            value=default_answer
        )

        col1, col2 = st.columns(2)
        with col1:
            evaluate_btn = st.button("Check My Answer", type="primary", use_container_width=True)
        with col2:
            star_btn = st.button("Check STAR Format", type="secondary", use_container_width=True)

        if evaluate_btn:
            if answer.strip():
                with st.spinner("Checking your answer..."):
                    try:
                        evaluation = evaluate_answer(
                            questions[current_q],
                            answer,
                            st.session_state["resume_text"]
                        )
                        st.session_state[f"eval_{current_q}"] = evaluation
                        evals = st.session_state.get("evaluations", [])
                        if len(evals) <= current_q:
                            evals.append(evaluation)
                        st.session_state["evaluations"] = evals
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please write or speak your answer first.")

        if star_btn:
            if answer.strip():
                with st.spinner("Checking STAR format..."):
                    try:
                        star = check_star_method(answer)
                        st.session_state[f"star_{current_q}"] = star
                        stars = st.session_state.get("star_scores", [])
                        if len(stars) <= current_q:
                            stars.append(star["star_score"])
                        st.session_state["star_scores"] = stars
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please write or speak your answer first.")

        # Scores
        if f"eval_{current_q}" in st.session_state:
            eval = st.session_state[f"eval_{current_q}"]
            st.markdown("---")
            st.header("Your Scores")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Clarity", f"{eval['clarity']}/10")
            col2.metric("Technical", f"{eval['technical_depth']}/10")
            col3.metric("Communication", f"{eval['communication']}/10")
            col4.metric("Overall", f"{eval['overall']}/10")

            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"**What you did well:**\n\n{eval['strengths']}")
            with col2:
                st.warning(f"**What to improve:**\n\n{eval['improvements']}")
            st.info(f"**A stronger answer would include:**\n\n{eval['ideal_answer']}")

        # STAR
        if f"star_{current_q}" in st.session_state:
            star = st.session_state[f"star_{current_q}"]
            st.markdown("---")
            st.header("STAR Format Check")
            st.write("Good interview answers usually follow: Situation → Task → Action → Result")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if star["situation"]["present"]:
                    st.success(f"✅ Situation\n\n{star['situation']['explanation']}")
                else:
                    st.error(f"❌ Situation\n\n{star['situation']['explanation']}")
            with col2:
                if star["task"]["present"]:
                    st.success(f"✅ Task\n\n{star['task']['explanation']}")
                else:
                    st.error(f"❌ Task\n\n{star['task']['explanation']}")
            with col3:
                if star["action"]["present"]:
                    st.success(f"✅ Action\n\n{star['action']['explanation']}")
                else:
                    st.error(f"❌ Action\n\n{star['action']['explanation']}")
            with col4:
                if star["result"]["present"]:
                    st.success(f"✅ Result\n\n{star['result']['explanation']}")
                else:
                    st.error(f"❌ Result\n\n{star['result']['explanation']}")

            st.metric("STAR Score", f"{star['star_score']}/10")
            st.info(f"Tip: {star['tip']}")

        st.markdown("---")

        if f"eval_{current_q}" in st.session_state:
            if current_q < len(questions) - 1:
                if st.button("Next Question →", type="primary", use_container_width=True):
                    st.session_state["current_q"] = current_q + 1
                    st.rerun()
            else:
                save_session(
                    st.session_state.get("mode", "Technical"),
                    st.session_state.get("evaluations", []),
                    st.session_state.get("star_scores", [])
                )
                st.balloons()
                st.success("You finished all the questions! Great work.")

                evals = st.session_state.get("evaluations", [])
                if evals:
                    avg = sum(e["overall"] for e in evals) / len(evals)
                    st.markdown("---")
                    st.header("Session Summary")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Questions Done", len(evals))
                    col2.metric("Average Score", f"{avg:.1f}/10")
                    col3.metric("Interview Type", st.session_state.get("mode", "Technical"))

                st.info("Check the sidebar to see how your scores are improving.")

                if st.button("Practice Again", type="primary", use_container_width=True):
                    for key in ["questions", "current_q", "evaluations", "star_scores"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()