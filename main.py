from flask import Flask, Blueprint, render_template, redirect, url_for, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from pytz import timezone
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

db = SQLAlchemy()
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID,
                                                           client_secret=CLIENT_SECRET))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

interface = Blueprint('interface', __name__, template_folder='templates')

@interface.route('/')
def index():
  print(sp.current_user())
  return render_template('index.html')

@interface.route('/login')
def login():
  return render_template('login.html')

api = Blueprint('api', __name__)

@api.route('/api/v1/', methods=["GET"])
def apiV1():
  return "Hello World!"

@api.route('/api/v1/suggestion', methods=["POST"])
def suggestion():
    turno = request.form.get('turno')
    musica = request.form.get('musica')
    cantor = request.form.get('cantor')
    results = sp.search(q=musica, limit=20)
    for idx, track in enumerate(results['tracks']['items']):
        if track['artists'][0]['name'] == cantor:
          song = {
             "nome": track['name'], 
             "artista": track['artists'][0]['name'], 
             "album_url": track['album']['images'][0]['url'], 
             "song_url": track['external_urls']['spotify']
            }
          break
    sp.add_to_queue(song['song_url'])
    return jsonify(song)
    
app.register_blueprint(interface)
app.register_blueprint(api)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32))
    singer = db.Column(db.String(64))
    gender = db.Column(db.String(64))

db.init_app(app)
app.run("0.0.0.0", port=8080)
