from flask import Flask, request

VERIFY_TOKEN = "Kev!nB@t122"  # Must match the token you enter on Meta

app = Flask(__name__)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ WEBHOOK VERIFIED")
            return challenge, 200
        else:
            print("❌ Verification failed")
            return "Verification failed", 403

    elif request.method == "POST":
        data = request.json
        print("📩 Received POST data:", data)
        return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)