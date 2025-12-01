from flask import Flask, request, jsonify
from flask_cors import CORS

from aes import aes_encrypt, aes_decrypt
from sbox import generate_sbox

app = Flask(__name__)
CORS(app)

@app.post("/encrypt")
def encrypt():
    data = request.json
    text = data["text"]
    key = data["key"]
    mod = data["modified"]
    result = aes_encrypt(text, key, mod)
    return jsonify({"cipher": result})

@app.post("/decrypt")
def decrypt():
    data = request.json
    cipher = data["cipher"]
    key = data["key"]
    mod = data["modified"]
    result = aes_decrypt(cipher, key, mod)
    return jsonify({"plain": result})

@app.get("/sbox")
def show_sbox():
    mod = request.args.get("m") == "1"
    return jsonify(generate_sbox(mod))

if __name__ == "__main__":
    app.run(port=5000, debug=True)
