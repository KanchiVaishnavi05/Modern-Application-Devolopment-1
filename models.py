from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'general' or 'creator'
    status = db.Column(db.Boolean)  
 

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50))
    artist = db.Column(db.String(100))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    songs = db.relationship('Song', backref='album', lazy=True)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False,unique=True)
    lyrics = db.Column(db.Text)
    duration = db.Column(db.String(10))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    ratings = db.relationship('Rating', backref='song', lazy=True)
    

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)

class Playlist(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String,db.ForeignKey('user.username'), nullable=False)
    playlist_name = db.Column(db.String,nullable=False)
    playlist_description = db.Column(db.String,nullable=True)
    
class Songlist(db.Model):
    id = db.Column(db.Integer,primary_key=True) 
    username = db.Column(db.String,db.ForeignKey('user.username'))  
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'))
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
