from flask import Flask
import huya

app = Flask(__name__)
@app.route('/')
def home():
    return 'Home Page Route'
@app.route('/huya/<room_id>')
def huyaapi(room_id):
    return huya.huya(room_id)


if __name__ == '__main__':
    app.run(debug=True)
