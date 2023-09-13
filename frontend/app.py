from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tn/<string:tnId>')
def tn(tnId: str):
    return render_template('tn.html', tnId=tnId)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
