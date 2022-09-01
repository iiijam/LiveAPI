from flask import Flask, request, render_template
from flask_cors import CORS, cross_origin
import huya
import douyu

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/huya/<room_id>')
@cross_origin()
def huyaapi(room_id):
    return huya.huya(room_id)


@app.route('/douyu/<room_id>')
@cross_origin()
def douyuapi(room_id):
    douyu_room = douyu.DouYu(room_id)
    details = request.args.get('details', 'enable')
    full = request.args.get('full', 'enable')
    return douyu_room.douyu(full=full, details=details)


if __name__ == '__main__':
    app.run(debug=True)
