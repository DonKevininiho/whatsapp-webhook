from flask import Flask, request
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = 'Kev!nB@t122'  # your verify token
ACCESS_TOKEN = 'EAAJbehBwwNABPEEU6VVQLSn0PsYiZB2AQTuFKrTgvKVpU83vL0ZBoZAtoHTI7nZCyBWxK2jAa5m6QndLOSNzgUW0lXoJ2uXyh9NhyPdIuuWJEBSk05DIZA6r4BuOGN1OQZCJ6bdLZBjZC18g6ip0eymSx0DbYtusdLKOOP1mE55l32ZCgKjiJYrC4RcvcaMOc1jI6ofB5Q3QY1Bu4ZBVlpXlSiTjsDb8UvoMstgqVpUyT40sjvZBQZDZD'

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return 'Verification token mismatch', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    try:
        entry = data['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        messages = value.get('messages')
        
        if messages:
            message = messages[0]
            message_type = message['type']

            if message_type == 'audio':
                media_id = message['audio']['id']

                # Step 1: Get media URL
                url = f"https://graph.facebook.com/v18.0/{media_id}"
                headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
                response = requests.get(url, headers=headers)
                media_url = response.json()['url']

                # Step 2: Download media
                audio_data = requests.get(media_url, headers=headers)
                with open('voice.ogg', 'wb') as f:
                    f.write(audio_data.content)
                print("✅ Voice note downloaded!")

    except Exception as e:
        print("❌ Error:", e)

    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)