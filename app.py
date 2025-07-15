from flask import Flask, request
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = 'Kev!nB@t122'
ACCESS_TOKEN = 'EAAJbehBwwNABPEEU6VVQLSn0PsYiZB2AQTuFKrTgvKVpU83vL0ZBoZAtoHTI7nZCyBWxK2jAa5m6QndLOSNzgUW0lXoJ2uXyh9NhyPdIuuWJEBSk05DIZA6r4BuOGN1OQZCJ6bdLZBjZC18g6ip0eymSx0DbYtusdLKOOP1mE55l32ZCgKjiJYrC4RcvcaMOc1jI6ofB5Q3QY1Bu4ZBVlpXlSiTjsDb8UvoMstgqVpUyT40sjvZBQZDZD'

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return 'Verification token mismatch', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print("📦 Incoming webhook payload:", data, flush=True)

        entry = data.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})
        messages = value.get('messages')

        if not messages:
            print("ℹ️ No 'messages' field found.", flush=True)
            return "OK", 200

        message = messages[0]
        message_type = message.get('type')
        print("📨 Message type:", message_type, flush=True)

        if message_type == 'audio':
            media_id = message['audio']['id']
            print("🔊 Voice note media ID:", media_id, flush=True)

            # Step 1: Get media URL
            url = f"https://graph.facebook.com/v18.0/{media_id}"
            headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
            response = requests.get(url, headers=headers)
            media_url = response.json().get('url')
            print("🔗 Media URL:", media_url, flush=True)

            # Step 2: Download media
            audio_data = requests.get(media_url, headers=headers)
            with open('/tmp/voice.ogg', 'wb') as f:
                f.write(audio_data.content)
            print("✅ Voice note downloaded to /tmp/voice.ogg", flush=True)

            # Step 3: Transcribe audio with Whisper
            try:
                with open("/tmp/voice.ogg", 'rb') as f:
                    files = {'file': f}
                    headers = {
                        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
                    }
                    data = {"model": "whisper-1", "response_format": "json", "language": "en"}
                    response = requests.post(
                        "https://api.openai.com/v1/audio/transcriptions",
                        headers=headers,
                        files=files,
                        data=data
                    )
                    result = response.json()
                    print("📨 Whisper API response:", result, flush=True)
                    transcription = result.get("text")
                    if transcription:
                        print("📝 Transcription:", transcription, flush=True)
                    else:
                        print("❗ No transcription text found in response.", flush=True)
            except Exception as e:
                print("❌ Whisper API Error:", e, flush=True)

        else:
            print("ℹ️ Message is not an audio file.", flush=True)

    except Exception as e:
        print("❌ Webhook error:", e, flush=True)

    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)