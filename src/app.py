import os
from flask import request, jsonify
from flask_app.wsgi import create_app
from src.wyl import validate_post_data

app = create_app()
app.secret_key = os.urandom(32)

@app.route('/', methods=['GET'])
def hello():
    return 'Hello World!'


@app.route('/api', methods=['GET', 'POST'])
def api():
    """
    /api entpoint
    GET - returns json= {'status': 'test'}
    POST -  {
            name - str not null
            age - int optional
            }
    :return:
    """
    if request.method == 'GET':
        return jsonify({'status': 'test'})
    elif request.method == 'POST':
        if validate_post_data(request.json):
            return jsonify({'status': 'OK'})
        else:
            return jsonify({'status': 'bad input'}), 400


def main():
    app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    print(app.url_map)
    main()
