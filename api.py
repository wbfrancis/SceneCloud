import os
from flask import Flask, request, jsonify
import jsonpickle
from flask_cors import CORS
from backend.movielist import movies
import backend.script_constructor as sc

import backend.make_wordcloud as wc

app = Flask(__name__, static_folder='./build', static_url_path='/')
CORS(app)

# db_drop_and_create_all()
# ENDPOINTS FOR RECIPES
# #####################
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/scripts')
def get_preuploaded_scripts():
    return jsonify({
        "success": True,
        "scripts": movies
    })

# upload new script and return script object
@app.route('/scripts', methods=['POST'])
def upload_script():
    f = request.files['file']
    title = request.form.get('title')
    script = sc.initialize_script(title, f)

    return jsonify({
        "success": True,
        "scriptObject": jsonpickle.encode(script),
        "characters": script.get_sorted_characters()
    })

# script_id=-1, script_obj=None, whole_script=False, action_lines=False, characters=[]
@app.route('/clouds', methods=['POST'])
def generate_clouds():
    data = request.args
    script_id = int(data.get('script_id'))

    if data.get('script_obj') == 'null':
        script_obj = sc.initialize_script(movies[script_id]['title'])
    else: script_obj = data.get('script_obj')

    whole_script = True if data.get('whole_script') == 'true' else False
    action_lines = True if data.get('action_lines') == 'true' else False
    if data.get('characters') and data.get('action_lines') is not '':
        characters = data.get('characters').split(',')
    else: characters = []

    clouds = wc.generateClouds(script_obj, whole_script, action_lines, characters)
    return jsonify({
        "success": True,
        "clouds": [clouds]
    })

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=os.environ.get('PORT', 80))