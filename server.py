from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/message', methods=['POST'])
def hello_message():
    data = request.get_json()
    if data and 'message' in data and data['message'] == 'hello':
        return jsonify(response="Hello back!")
    else:
        return jsonify(error="Expected 'hello' message"), 400

if __name__ == '__main__':
    app.run(debug=True, port=8000)