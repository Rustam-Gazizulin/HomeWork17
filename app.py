# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from setup_db import db

from models import Movie, Genre, Director
from schemas import movies_schema, movie_schema

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 3}

app.app_context().push()
db.init_app(app)

api = Api(app)
movie_ns = api.namespace('movies')


@movie_ns.route('/')
class MovieView(Resource):

    def get(self):
        movie_genre_and_director = db.session.query(Movie.id, Movie.title, Movie.description, Movie.rating,
                                                    Movie.trailer,
                                                    Genre.name.label('genre'),
                                                    Director.name.label('director')).join(Genre).join(Director)

        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id:
            movie_genre_and_director = movie_genre_and_director.filter(Movie.director_id == director_id)
        if genre_id:
            movie_genre_and_director = movie_genre_and_director.filter(Movie.genre_id == genre_id)

        all_movies = movie_genre_and_director.all()

        return movies_schema.dump(all_movies), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return f'Новый объект с id {new_movie.id} создан', 201


@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid: int):
        movie = db.session.query(Movie.id, Movie.title, Movie.description, Movie.rating, Movie.trailer,
                                 Genre.name.label('genre'),
                                 Director.name.label('director')).join(Genre).join(Director).filter(
            Movie.id == uid).first()
        if movie:
            return movie_schema.dump(movie)
        return "File not found", 404

    def patch(self, uid: int):
        movie = db.session.query(Movie).get(uid)
        if not movie:
            return "File not found", 404

        req_json = request.json
        if 'title' in req_json:
            movie.title = req_json['title']
        elif 'description' in req_json:
            movie.description = req_json['description']
        elif 'trailer' in req_json:
            movie.trailer = req_json['trailer']
        elif 'year' in req_json:
            movie.year = req_json['year']
        elif 'rating' in req_json:
            movie.rating = req_json['rating']
        elif 'genre_id' in req_json:
            movie.genre_id = req_json['genre_id']
        elif 'director_id' in req_json:
            movie.director_id = req_json['director_id']
        db.session.add(movie)
        db.session.commit()
        return f'Объект с id {movie.id} обновлен', 204

    def put(self, uid: int):
        movie = db.session.query(Movie).get(uid)
        if not movie:
            return "File not found", 404

        req_json = request.json

        movie.title = req_json['title']
        movie.description = req_json['description']
        movie.trailer = req_json['trailer']
        movie.year = req_json['year']
        movie.rating = req_json['rating']
        movie.genre_id = req_json['genre_id']
        movie.director_id = req_json['director_id']

        db.session.add(movie)
        db.session.commit()
        return f'Объект с id {movie.id} обновлен', 204

    def delete(self, uid: int):
        movie = db.session.query(Movie).get(uid)
        if not movie:
            return "File not found", 404
        db.session.delete(movie)
        db.session.commit()
        return f'Объект с id {movie.id} удален', 204


if __name__ == '__main__':
    app.run(debug=True)
