from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/test', methods=['POST'])
def testapi():
    data = request.get_json()
    print(data)
    return data
if __name__=='__main__':
    app.run(debug=True)