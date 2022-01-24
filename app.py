from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Int()
    genre_id = fields.Int()
    genre = fields.Str()
    director_id = fields.Int()
    director = fields.Str()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


movie_schema = MovieSchema()
genre_schema = GenreSchema()
director_schema = DirectorSchema()

api = Api(app)
movie_ns = api.namespace('movies')
genre_ns = api.namespace('genres')
director_ns = api.namespace('directors')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        #  возвращает список всех фильмов, так же возвращает фильмы с определенным режиссером и жанром по запросу.
        genre_id = request.args.get('genre_id')
        director_id = request.args.get('director_id')
        result = Movie.query

        if director_id is not None:
            result = result.filter(Movie.director_id == director_id)
        if genre_id is not None:
            result = result.filter(Movie.genre_id == genre_id)
        if director_id is not None and genre_id is not None:
            result = result.filter(Movie.genre_id == genre_id, Movie.director_id == director_id)
        all_movie = result.all()

        return movie_schema.dump(all_movie, many=True), 200

    def post(self):
        # добавляет кино в фильмотеку.
        req_json = request.json
        new_movie = Movie(**req_json)

        with db.session.begin():
            db.session.add(new_movie)
        return "", 201


@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid: int):
        # возвращает подробную информацию о фильме.
        movie = Movie.query.get(uid)

        if not movie:
            return "", 404

        return movie_schema.dump(movie)

    def delete(self, uid: int):
        # удаляет выбранный фильм.
        movie = Movie.query.get(uid)

        if not movie:
            return "", 404

        db.session.delete(movie)
        db.session.commit()

        return "", 204


@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        # возвращает список всех жанров

        all_genres = Genre.query.all()
        return genre_schema.dump(all_genres, many=True), 200

    def post(self):
        req_json = request.json
        new_genre = Movie(**req_json)

        with db.session.begin():
            db.session.add(new_genre)
        return "", 201


@genre_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid: int):
        # Возвращает фильмы определенного жанра по запросу

        genre = Genre.query.get(uid)

        if not genre:
            return "", 404

        return genre_schema.dump(genre)

    def delete(self, uid: int):
        # удаляет выбранный жанр.
        genre = Genre.query.get(uid)

        if not genre:
            return "", 404

        db.session.delete(genre)
        db.session.commit()

        return "", 204

    def put(self, uid: int):
        # обновление сущности по идентификатору
        genre = Genre.query.get(uid)
        req_json = request.json
        genre.name = req_json.get("name")
        db.session.add(genre)
        db.session.commit()
        return "", 204


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        all_directors = Director.query.all()
        return director_schema.dump(all_directors, many=True)

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)

        with db.session.begin():
            db.session.add(new_director)
        return "", 201


@director_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid: int):
        # Возвращает фильмы с определенным режиссером по запросу
        director = Director.query.get(uid)

        if not director:
            return "", 404

        return director_schema.dump(director)

    def delete(self, uid: int):
        # удаляет выбранный режиссер.
        director = Director.query.get(uid)

        if not director:
            return "", 404

        db.session.delete(director)
        db.session.commit()

        return "", 204

    def put(self, uid: int):
        # обновление сущности по идентификатору
        director = Director.query.get(uid)
        req_json = request.json
        director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
