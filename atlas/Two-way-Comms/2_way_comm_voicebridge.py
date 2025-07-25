# -*- coding: utf-8 -*-
"""2 way comm VoiceBridge.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/156PVwB51ZVI3pHfVcpsL9i--swpxtLtQ
"""

# 🔧 Install dependencies
!pip install -q transformers torchaudio accelerate spacy git+https://github.com/openai/whisper.git soundfile
!python -m spacy download en_core_web_sm

# 📚 Imports
import whisper
import spacy
import os
import base64
import re
import time
import soundfile as sf
from IPython.display import Javascript, display, Audio
from google.colab import files, output
from base64 import b64decode

# 🎤 JS for button-controlled recording
record_js = """
let recorder, stream;
const audioChunks = [];

async function startRecording() {
  stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  recorder = new MediaRecorder(stream);

  recorder.ondataavailable = event => {
    if (event.data.size > 0) audioChunks.push(event.data);
  };

  recorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks);
    const reader = new FileReader();
    reader.readAsDataURL(audioBlob);
    reader.onloadend = () => {
      const base64data = reader.result.split(',')[1];
      google.colab.kernel.invokeFunction('notebook.save_audio', [base64data], {});
    };
  };

  recorder.start();
  document.getElementById('status').textContent = '🎙 Recording... Click stop when done.';
}

function stopRecording() {
  recorder.stop();
  stream.getTracks().forEach(track => track.stop());
  document.getElementById('status').textContent = '⏳ Processing audio...';
}

const controls = `
  <div>
    <button onclick="startRecording()">🎤 Start Recording</button>
    <button onclick="stopRecording()">🛑 Stop</button>
    <p id="status"></p>
  </div>
`;
document.body.innerHTML = controls;
"""

# 🧠 NLP analysis
def analyze_and_alert(text):
    doc = nlp(text)
    alert, triggers, entities, phrases = False, [], [], []

    for ent in doc.ents:
        if ent.label_ in important_labels:
            entities.append((ent.text, ent.label_))
            alert = True

    for token in doc:
        if token.text.lower() in trigger_words:
            triggers.append(token.text.lower())
            alert = True

    for phrase in ATC_PHRASES:
        if re.search(phrase, text.lower()):
            phrases.append(phrase)
            alert = True

    return alert, triggers, entities, phrases

# 📥 Mic recording callback
output.register_callback('notebook.save_audio', lambda data: open("input_audio.wav", "wb").write(b64decode(data)))

# 📥 Wait for mic input
def wait_for_file(filename, timeout=30):
    print("⌛ Waiting for audio file...")
    start = time.time()
    while not os.path.exists(filename):
        elapsed = int(time.time() - start)
        if elapsed > timeout:
            print("❌ Timeout: No mic audio received.")
            return False
        print(f"  ...{elapsed}s", end="\r")
        time.sleep(1)
    print("✅ Audio file received!")
    return True


# 🧠 Load models
whisper_model = whisper.load_model("base")
nlp = spacy.load("en_core_web_sm")

# 📘 Triggers & Patterns
trigger_words = { "descend", "maintain", "contact", "traffic", "approach", "runway", "heading", "climb", "turn",
                  "left", "right", "direct", "altitude", "speed", "cleared", "hold", "pattern", "report",
                  "position", "cross", "taxi", "exit", "wind", "visibility", "cloud", "pressure", "qnh", "ils",
                  "visual", "vector", "mayday", "pan-pan", "emergency", "divert", "fuel", "minimum", "squawk",
                  "declare", "assistance", "immediately", "unable", "jettison", "zero", "one", "two", "three",
                  "four", "five", "six", "seven", "eight", "nine", "hundred", "thousand", "point", "decimal" }

important_labels = {"ORG", "GPE", "LOC", "FAC", "DATE", "TIME", "CARDINAL", "QUANTITY"}

ATC_PHRASES = [
    r"cleared (to land|for takeoff|for approach)",
    r"(maintain|climb|descend) to (flight level|altitude) \w+",
    r"line up and wait",
    r"contact (tower|approach|center) on \d+\.\d+",
    r"hold short of (runway|taxiway) \w+",
    r"taxi to (runway|gate) \w+ via \w+",
    r"report (established|downwind|base|final)",
    r"expect (approach|landing) clearance at \d+",
    r"cleared (visual|ILS) approach (runway \w+)",
    r"turn (left|right) heading \d+",
    r"reduce speed to \d+ knots",
    r"traffic (\d+ o'clock|(left|right)) (\d+ miles) (north|south|east|west)",
    r"(mayday|pan-pan) (repeat mayday|pan-pan)",
    r"squawk \d+",
    r"declare (fuel|other) emergency",
    r"request (priority|immediate) landing",
    r"unable to (comply|maintain)",
    r"request (lower|higher) altitude",
    r"engine (failure|problem)",
    r"request (vectors|assistance) to nearest airport"
]

def get_audio(label):
    mode = input(f"🔘 [{label}] Type 'mic' or 'upload': ").strip().lower()

    if mode == 'mic':
        print(f"🎤 [{label}] Press start/stop to record:")
        display(Javascript(record_js))
        if not wait_for_file("input_audio.wav", timeout=30):
            print("❌ Mic input failed.")
            return None
        filename = f"{label.lower()}_audio.wav"
        os.rename("input_audio.wav", filename)

    elif mode == 'upload':
        uploaded = files.upload()
        if not uploaded:
            print("❌ Upload failed.")
            return None
        filename = list(uploaded.keys())[0]
        new_filename = f"{label.lower()}_audio.wav"
        os.rename(filename, new_filename)
        print(f"✅ Uploaded as {new_filename}")
        filename = new_filename

    else:
        print("⚠️ Invalid mode.")
        return None

    return filename

# 📊 Main interaction
def two_way_comm():
    atc_audio = get_audio("ATC")
    pilot_audio = get_audio("Pilot")

    for label, audio_file in [("ATC", atc_audio), ("Pilot", pilot_audio)]:
      if not audio_file:
        print(f"❌ No audio for {label}")
        continue # Fixed: Indentation was incorrect here, causing issues later on

      result = whisper_model.transcribe(audio_file, language="en")
      text = result["text"].strip()
      alert, triggers, entities, phrases = analyze_and_alert(text)

      print(f"\n🗣 {label} Says:")
      print(f"📝 Text: {text}")
      print(f"📌 Language: {result.get('language', 'unknown')}")

      if triggers or entities or phrases:
          print("🔎 Highlights:")
          if triggers: print("Trigger Words:", ", ".join(triggers))
          if entities: print("Entities:", ", ".join(f"{e[0]} ({e[1]})" for e in entities))
          if phrases: print("ATC Phrases:", ", ".join(phrases))
      else:
          print("✅ No critical elements found.")

      if alert:
          print("🚨 ALERT: Critical content detected.")
      display(Audio(audio_file))

    # 🔁 Check agreement
    print("\n🔁 Checking for communication alignment...") # Fixed: Indentation should align with the for loop
    atc_text = whisper_model.transcribe(atc_audio)["text"].lower()
    pilot_text = whisper_model.transcribe(pilot_audio)["text"].lower()
    if any(w in atc_text and w not in pilot_text for w in trigger_words):
        print("❗️ Mismatch Detected: Pilot may have missed instructions.")
    else:
        print("✅ Communication Confirmed.")

# ▶️ Run system
two_way_comm()