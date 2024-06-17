from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Album, Song, Playlist, Songlist, Rating
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Change this to a random secret key
db.init_app(app)

with app.app_context():
        db.create_all()
# Routes and Views



# Home route
@app.route('/')
def home():
    return render_template('login_register_page.html')



@app.route('/all_dashboard')
def all_dashboard():
    user_id = session['user_id']
    albums = Album.query.order_by(Album.date_created.desc()).all()
    user = User.query.get(user_id)
    
    if user.role == 'creator' and user.status:
        albums_creator = Album.query.filter(Album.creator_id == user_id).order_by(Album.date_created.desc()).all()
        return render_template('creator_dashboard.html', albums=albums_creator, creator=user)
    if user.role == 'creator' and not user.status:
        return render_template('black_creator.html')
    
    elif user.role == 'admin':
        cre = User.query.filter(User.role == 'creator').all()
        gen = User.query.filter(User.role == 'general').all()
        songs = Song.query.all()
        n_genre = db.session.query(Album.genre).distinct().count()
        return render_template('admin_dashboard.html',albums=albums, n_c = len(cre), n_g = len(gen), n_a = len(albums), songs=songs, n_s = len(songs), n_genre=n_genre)
    else:    
        return render_template('general_user_dashboard.html', albums=albums)



# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        new_user = User(username=username, password=password, role=role, status=True)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')



# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            # For simplicity, store user ID in session
            session['user_id'] = user.id
    
            return redirect(url_for('all_dashboard'))
        else:
            return render_template('login.html')    
    else:
        return render_template('login.html')
    

        
# Creator Dashboard route
@app.route('/creator_dashboard')
def creator_dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        print(user_id)
        user = User.query.get(user_id)
        
        if user and user.role == 'creator':
            albums = Album.query.filter_by(creator_id=user_id).all()
            return render_template('creator_dashboard.html', albums=albums, creator=user)

    return redirect(url_for('login'))



# Create Album route
@app.route('/create_album', methods=['GET', 'POST'])
def create_album():
    
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)

    if request.method == 'GET':
        return render_template('create_album.html', user=user)
    
    if request.method == 'POST':
        name = request.form['name']
        genre = request.form['genre']
        artist = request.form['artist']
        
        if 'user_id' in session:
            user_id = session['user_id']
            user = User.query.get(user_id)
            
            if user and user.role == 'creator':
                new_album = Album(name=name, genre=genre, artist=artist,creator_id = user_id)
                db.session.add(new_album)
                db.session.commit()
                
                return redirect(url_for('creator_dashboard'))

    return render_template('create_album.html', user=user)



# Delete album route 
@app.route('/delete_album/<int:album_id>', methods=['GET', 'POST'])
def delete_album(album_id):

    #get album with id as album_id
    album = Album.query.get(album_id)
    #get the songs in the album
    songs = Song.query.filter(Song.album_id == album_id).all()
    if len(songs) > 0:
        for song in songs:
            delete_song(album.id,song.id)
    if album:
        db.session.delete(album)
        db.session.commit()
    return redirect(url_for('creator_dashboard'))



# Edit album route 
@app.route('/edit_album/<int:album_id>', methods=['GET', 'POST'])
def edit_album(album_id):

    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)

    if request.method == 'GET':
        print('get method')
        if user and user.role == 'creator':
            album = Album.query.get(album_id)
            album_name = album.name
            return render_template('edit_album.html', user=user, album=album, album_name = album_name)
    
    if request.method == 'POST':
        name = request.form['name']
        genre = request.form['genre']
        artist = request.form['artist']
        
        if 'user_id' in session:
            user_id = session['user_id']
            user = User.query.get(user_id)
            
            if user and user.role == 'creator':
                album = Album.query.get(album_id)
                if name:
                    album.name = name
                if genre:
                    album.genre = genre
                if artist:
                    album.artist = artist

                db.session.commit()
                
                return redirect(url_for('creator_dashboard'))

    return render_template('edit_album.html', user=user, album=album)



@app.route('/get_songs/<int:album_id>',methods=['GET','POST'])
def get_songs(album_id):
    songs = Song.query.filter(Song.album_id == album_id).all()
    album = Album.query.get(album_id)
    user_id = session['user_id']
    user = User.query.get(user_id)
    if user.role == 'general':
        genre_list = []
        albums_all = Album.query.all()
        for album in albums_all:
            if album.genre not in albums_all:
                genre_list.append(album.genre)
        playlist_ = Playlist.query.filter(Playlist.username == user.username).all()
        playlist_name = []
        for playlist in playlist_:
            if playlist.playlist_name not in playlist_name:
                playlist_name.append(playlist.playlist_name)
        rating = []
        for song in songs:
            individual_rating = Rating.query.filter_by(user_id=user_id, song_id=song.id).first()
            if individual_rating:
                rating.append(individual_rating.rating)
        
        return render_template('general_album_songs.html',album = album,songs = songs, playlist_name = playlist_name, rating=rating)
    return render_template('creator_songs.html',album = album,songs = songs)



# Create Song route
@app.route('/create_song/<int:album_id>', methods=['GET', 'POST'])
def create_song(album_id):
    album = Album.query.get(album_id)
    if request.method == 'GET' and album:
        return render_template('create_song.html',album_id =album_id, album = album )
    if request.method == 'POST' and album:
        name = request.form['name']
        lyrics = request.form['lyrics']
        duration = request.form['duration']
        
        if 'user_id' in session:
            user_id = session['user_id']
            user = User.query.get(user_id)
            
            if user and user.role == 'creator' and album.creator_id == user_id:
                new_song = Song(name=name, lyrics=lyrics, duration=duration, album_id=album.id)
                db.session.add(new_song)
                db.session.commit()
                
                return redirect(url_for('get_songs',album_id = album_id))

    return render_template('create_song.html', album=album)



# Create Song route
@app.route('/edit_song/<int:song_id>', methods=['GET', 'POST'])
def edit_song(song_id):

    song = Song.query.filter_by(id=song_id).first()
    album_list = Album.query.filter_by(creator_id = session['user_id'])
    album = Album.query.get(song.album_id)
    if request.method == 'GET':
        return render_template('edit_song.html', song = song, album_list = album_list, album=album)
    
    if request.method == 'POST' and song:
        name = request.form['name']
        lyrics = request.form['lyrics']
        duration = request.form['duration']
        # album_name = request.form['album_name']
        # print(album_name)
          
        if 'user_id' in session:
            user_id = session['user_id']
            user = User.query.get(user_id)
            
            if user and user.role == 'creator':

                if name:
                    song.name = name

                if lyrics:
                    song.lyrics = lyrics

                if duration:
                    song.duration = duration

                # if album_name:
                #     album = Album.query.filter(Album.name == album_name, Album.creator_id == user.id).first()
                #     album_id = album.id
                #     song.album_id = album_id
                db.session.commit()
                
                return redirect(url_for('get_songs',album_id = song.album_id))

    # return render_template('create_song.html', album=album)



# Delete Song route
@app.route('/delete_song/<int:album_id>/<int:song_id>', methods=['GET', 'POST'])
def delete_song(album_id, song_id):
    song = Song.query.get(song_id)
    if song:
        ratings = Rating.query.filter(Rating.song_id == song.id).all()
        songlists = Songlist.query.filter(Songlist.song_id == song.id).all()
        for rating in ratings:
            db.session.delete(rating)
        for songlist in songlists:
            db.session.delete(songlist)
        db.session.delete(song)
        db.session.commit()

        user_id = session['user_id']    
        user = User.query.get(user_id)
        if user.role == 'admin':  
            return redirect(url_for('all_dashboard'))
        
        return redirect(url_for('get_songs',album_id = album_id))



# Rate Song route
@app.route('/rate/<int:song_id>', methods=['GET', 'POST'])
def rate(song_id):
    song = Song.query.get(song_id)
    if request.method == 'POST':
        rating = request.form["rating"]
        user_id = session['user_id']
        existing = Rating.query.filter_by(user_id=user_id, song_id=song_id).first()
        if existing:
            existing.rating = rating
        else:
            rating = Rating(user_id=user_id, song_id=song_id, rating = rating)
            db.session.add(rating)
        db.session.commit()
        return redirect(url_for('get_songs', album_id = song.album_id))



# show lyrics 
@app.route('/show_lyrics/<int:song_id>')
def show_lyrics(song_id):
    song = Song.query.get(song_id)
    user_id = session['user_id']
    user = User.query.get(user_id)
    return render_template('lyrics.html', song = song)



@app.route('/show_creators')
def show_creators():
    creators = User.query.filter(User.role == 'creator')
    return render_template('creator_status.html', creators = creators)



@app.route('/blacklist/<int:user_id>')
def blacklist(user_id):
    creator = User.query.get(user_id)
    creator.status = False
    db.session.commit()
    creators = User.query.filter(User.role == 'creator')
    return render_template('creator_status.html', creators = creators)



@app.route('/whitelist/<int:user_id>')
def whitelist(user_id):
    creator = User.query.get(user_id)
    creator.status = True
    db.session.commit()
    creators = User.query.filter(User.role == 'creator')
    return render_template('creator_status.html', creators = creators)



@app.route('/all_dashboard/create_playlist',methods = ['GET','POST'])
def create_playlist():
    if request.method == "GET":
        return render_template('create_playlist.html')
    elif request.method == "POST":
        playlist_name = request.form['playlist_name']
        playlist_description = request.form['playlist_description']  
        # print(playlist_name, playlist_description)  
        user_id = session['user_id']
        user = User.query.get(user_id)
        new_playlist = Playlist(username = user.username,playlist_name = playlist_name,playlist_description=playlist_description)
        db.session.add(new_playlist)
        db.session.commit()
        return render_template('create_playlist.html')



@app.route('/all_dashboard/playlists',methods = ['GET','POST'])
def show_playlists():
    user_id = session['user_id']
    user_playlists = Playlist.query.filter_by(username=User.query.get(user_id).username).all()  # Fetch playlists for the logged-in user
    return render_template('playlists.html', playlists=user_playlists)



@app.route('/all_dashboard/playlists/<int:playlist_id>',methods = ['GET','POST'])
def show_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)  # Fetch playlist with the given playlist_id
    songlist = Songlist.query.filter(Songlist.playlist_id == playlist.id).all()
    songs_pl = []
    for row in songlist:
        songs_pl.append(Song.query.get(row.song_id))
    return render_template('fav.html', songs_pl = songs_pl, pl_id = playlist_id)



@app.route('/add_to_playlist/<int:song_id>', methods = ['POST','GET'])
def add_to_playlist(song_id):
    if request.method == 'POST':
        playlist_name = request.form['playlist_name']
        user_id= session['user_id']
        user = User.query.get(user_id)
        pl = Playlist.query.filter_by(username = user.username, playlist_name = playlist_name).first()
        pl_id = pl.id

        # see if the song already in playlist
        existing = Songlist.query.filter_by(username = user.username, playlist_id =pl_id, song_id = song_id).first()
        if not existing:
            pl_song = Songlist(username = user.username, playlist_id =pl_id, song_id = song_id)
            db.session.add(pl_song)
            db.session.commit()
        return redirect(url_for('all_dashboard'))



# remove a song from songlist with playlist-id
@app.route('/remove_from_playlist/<int:playlist_id>/<int:song_id>', methods = ['POST','GET'])
def remove_from_playlist(playlist_id, song_id):

    user_id= session['user_id']
    user = User.query.get(user_id)
    songlist = Songlist.query.filter_by(username = user.username, playlist_id = playlist_id, song_id = song_id).first()
    db.session.delete(songlist)
    db.session.commit()

    return redirect(url_for('show_playlist', playlist_id = playlist_id))
    


# search for a keyword in songs
@app.route('/search', methods = ['POST','GET'])
def search():
    user_id= session['user_id']
    user = User.query.get(user_id)
    songs = Song.query.all()
    albums = Album.query.all()
    q = request.args.get("q")
    if q:
        results = Song.query.join(Album).filter(Song.name.icontains(q) | Album.name.icontains(q) | Album.artist.icontains(q) | Album.genre.icontains(q)).limit(100).all()
        print(results)
    else:
        results = []
    return render_template("searchResult.html", results = results, songs = songs, albums = albums)

@app.route('/get_search', methods = ['POST','GET'])
def get_search(): 
    return render_template("searchPage.html")


@app.route('/statistics')
def homepage():
    ratingList = Rating.query.all()
    songList = Song.query.all()
    rating_of_song = dict()
    for rating_song in ratingList:
        if rating_song.song_id not in rating_of_song.keys():
            for song in songList:
                if song.id == rating_song.song_id:
                    rating_of_song[song.name] = [rating_song.rating]
        else:
            for song in songList:
                if song.id == rating_song.song_id:
                    rating_of_song[song.name].append(rating_song.rating)
    
    for (key,value) in rating_of_song.items():
        tot_rating = 0
        for num in value:
            tot_rating += num
        rating_of_song[key] =  tot_rating/len(value)    
    print(rating_of_song)    
    labels = rating_of_song.keys()
    data = rating_of_song.values()
    labels = list(labels)
    data = list(data)
    print(labels,data)

    query_result = db.session.query(User.username, func.count(Playlist.id).label('playlist_count')) \
        .outerjoin(Playlist, User.username == Playlist.username) \
        .group_by(User.username) \
        .all()

    # Unpack the result into labels1 and values1
    labels1, values1 = zip(*query_result)
    labels1,values1 = list(labels1),list(values1)
    print(labels1,values1)
    query_result2 = db.session.query(Album.name, func.count(Song.id).label('song_count')) \
        .outerjoin(Song, Album.id == Song.album_id) \
        .group_by(Album.name) \
        .all()

    # Unpack the result into labels2 and values2
    labels2, values2 = zip(*query_result2)
    labels2,values2 = list(labels2),list(values2)

    return render_template('bar.html',labels = labels, data=data, labels1 = labels1, values1 = values1,labels2 = labels2, values2 = values2)


if __name__ == '__main__':
    
    app.run(debug=True)

