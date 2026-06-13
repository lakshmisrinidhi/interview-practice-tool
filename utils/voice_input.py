def get_voice_input_html(question_index):
    """Returns HTML/JS component for browser-based voice input"""
    return f"""
    <div style="margin: 10px 0;">
        <button onclick="startRecording_{question_index}()" 
            id="recordBtn_{question_index}"
            style="background: #00ff88; color: black; border: none; 
                   padding: 10px 20px; border-radius: 10px; 
                   font-weight: bold; cursor: pointer; font-size: 16px;">
            🎤 Click to Record
        </button>
        <button onclick="stopRecording_{question_index}()" 
            id="stopBtn_{question_index}"
            style="background: #ff4444; color: white; border: none; 
                   padding: 10px 20px; border-radius: 10px; 
                   font-weight: bold; cursor: pointer; font-size: 16px;
                   display: none; margin-left: 10px;">
            ⏹️ Stop Recording
        </button>
        <span id="status_{question_index}" 
            style="margin-left: 15px; font-style: italic; color: #aaa;">
        </span>
        <p id="transcript_{question_index}" 
            style="margin-top: 10px; padding: 10px; 
                   background: #1a1a2e; border-radius: 8px;
                   border-left: 3px solid #00ff88; display: none;">
        </p>
    </div>

    <script>
    let recognition_{question_index} = null;

    function startRecording_{question_index}() {{
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
            document.getElementById('status_{question_index}').innerText = 
                '❌ Voice not supported. Use Chrome or Edge.';
            return;
        }}

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition_{question_index} = new SpeechRecognition();
        recognition_{question_index}.continuous = true;
        recognition_{question_index}.interimResults = true;
        recognition_{question_index}.lang = 'en-US';

        recognition_{question_index}.onstart = function() {{
            document.getElementById('status_{question_index}').innerText = '🔴 Recording...';
            document.getElementById('recordBtn_{question_index}').style.display = 'none';
            document.getElementById('stopBtn_{question_index}').style.display = 'inline';
        }};

        recognition_{question_index}.onresult = function(event) {{
            let transcript = '';
            for (let i = 0; i < event.results.length; i++) {{
                transcript += event.results[i][0].transcript;
            }};
            let transcriptEl = document.getElementById('transcript_{question_index}');
            transcriptEl.style.display = 'block';
            transcriptEl.innerText = '🎤 ' + transcript;
        }};

        recognition_{question_index}.onerror = function(event) {{
            document.getElementById('status_{question_index}').innerText = 
                '❌ Error: ' + event.error;
        }};

        recognition_{question_index}.onend = function() {{
            document.getElementById('status_{question_index}').innerText = '✅ Done! Copy text below into answer box.';
            document.getElementById('recordBtn_{question_index}').style.display = 'inline';
            document.getElementById('stopBtn_{question_index}').style.display = 'none';
        }};

        recognition_{question_index}.start();
    }}

    function stopRecording_{question_index}() {{
        if (recognition_{question_index}) {{
            recognition_{question_index}.stop();
        }}
    }}
    </script>
    """