from flask import Flask, request, jsonify, render_template_string
import os, datetime, requests

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
TRIAL_START = datetime.date(2026, 11, 21)
TRIAL_DAYS = 7
WHATSAPP_NUMBER = "2630000000000"

HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ELION FOR ARDA</title>
<style>body{font-family:Arial;padding:20px;max-width:600px;margin:auto;background:#f4f4f4}
.box{background:white;padding:20px;border-radius:12px}
button{background:#25D366;color:white;border:none;padding:12px 20px;border-radius:8px;font-size:16px;width:100%;margin-top:10px}
input{width:100%;padding:12px;border-radius:8px;border:1px solid #ccc}
#chat{white-space:pre-wrap;background:#eef;padding:12px;border-radius:8px;margin-top:12px;min-height:100px}
.wa{display:block;text-align:center;background:#25D366;color:white;padding:12px;border-radius:8px;text-decoration:none;margin-top:10px;font-weight:bold}
</style></head><body><div class="box">
<h2>ELION FOR ARDA 🌾</h2><p id="trial"></p>
<input id="q" placeholder="Ask about Pivot, Maize, Fertilizer...">
<button onclick="ask()">Ask ELION</button>
<div id="chat">Ask me anything about ARDA farming...</div>
<a class="wa" href="https://wa.me/2630000000000?text=Hi ELION" target="_blank">Chat on WhatsApp</a>
</div><script>
async function ask(){
let q=document.getElementById('q').value;
document.getElementById('chat').innerText='Thinking...';
let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
let d=await r.json(); document.getElementById('chat').innerText=d.answer;
if(d.audio){let a=new Audio(d.audio); a.play();}
}
fetch('/trial').then(r=>r.json()).then(d=>{document.getElementById('trial').innerText=d.message});
</script></body></html>
"""

def trial_check():
    today = datetime.date.today()
    days_left = TRIAL_DAYS - (today - TRIAL_START).days
    return days_left

def clean_text(t):
    return t.replace("**","").replace("---","").replace("###","").replace("|","").strip()

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/health")
def health():
    return jsonify({"status":"ok"})

@app.route("/trial")
def trial():
    left = trial_check()
    if left < 0:
        return jsonify({"message":"Trial ended. Contact ELION to activate."})
    return jsonify({"message":f"7-Day Trial - {left} days left"})

@app.route("/ask", methods=["POST"])
def ask():
    if trial_check() < 0:
        return jsonify({"answer":"Trial ended on 28 Nov. Contact ELION to activate full access."})
    data = request.get_json() or {}
    q = data.get("question","")
    if not q:
        return jsonify({"answer":"Ask me about Pivot, Maize, Fertilizer for ARDA."})
    prompt = f"""You are ELION for ARDA Zimbabwe. Answer in simple clear English, no markdown, no stars, no dashes, no pipes. Short answer under 120 words.
    For ARDA Pivot Maize: Pivot irrigation, 30 to 45 days trial info, 20 to 30 minutes per session, 120kg Nitrogen total, 60kg at planting plus 60kg at V6, 30kg Phosphorus, 30kg Potassium.
    Question: {q}"""
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":prompt}],"temperature":0.3}, timeout=20)
        ans = r.json()["choices"][0]["message"]["content"]
        return jsonify({"answer":clean_text(ans)})
    except Exception as e:
        return jsonify({"answer":"For ARDA Pivot Maize: Use Pivot irrigation, 120kg Nitrogen total, 60kg at planting plus 60kg at V6, 30kg Phosphorus, 30kg Potassium. Water 20 to 30 minutes per session."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
