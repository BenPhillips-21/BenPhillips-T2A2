from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Column, Integer, String, Float
import os
import psycopg2

app = Flask(__name__)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://ben:amigo@localhost:5432/bookclub"
app.config['JWT_SECRET_KEY'] = 'friend'


db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

@app.cli.command('db_create')
def db_create(): 
    db.create_all()
    print('Database created successfully')

@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped successfully')

@app.cli.command('db_seed')    
def db_seed():
    books = [
        Book(
        title='King James Bible',
        genre='Religion',
        author='Various',
        synopsis="The Old Testament tells the story of God's chosen people, the Hebrews. The New Testament tells of Jesus' birth, life, ministry, death and resurrection, the growth of the early Christian Church, and predictions of the second coming of Jesus.",
        publication_year=1611),
        Book(
        title='The Lord of the Rings',
        genre='High Fantasy',
        author='JRR Tolkien',
        synopsis='In order to defeat the dark lord Sauron, Frodo Baggins is tasked with destroying the one ring',
        publication_year=1954),
        Book(
        title='Dracula',
        genre='Gothic Horror',
        author='Bram Stoker',
        synopsis='Follows the story of Count Dracula, a vampire from Transylvania, as he seeks to spread his curse and terrorize Victorian England.',
        publication_year=1954),
    ]

    db.session.add_all(books)
    db.session.commit()

    test_user = User(
        username='Booklover69',
        email='Booklover69@gmail.com',
        password='ilovebooks')

    db.session.add(test_user)
    db.session.commit()
    print('Database seeded successfully')

    
@app.route("/books", methods=["GET"])
def books():
    books_list = Book.query.all()
    result = books_schema.dump(books_list)
    return jsonify(result)

@app.route("/register", methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test: 
        return jsonify(message="that email already exists"), 409
    else:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User created successfully"), 201

@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']

    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login successful!", access_token=access_token)
    else:
        return jsonify(message="Email or password incorrect"), 401

    # database models
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Book(db.Model):
    __tablename__ = "books"

    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False, unique=True)
    genre = db.Column(db.String, nullable=False)
    synopsis = db.Column(db.String, nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'email', 'password', 'is_admin')

class BookSchema(ma.Schema):
    class Meta:
        fields = ('book_id', 'title', 'author', 'genre', 'synopsis', 'publication_year')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

book_schema = BookSchema()
books_schema = BookSchema(many=True)


if __name__ == "__main__":
    app.run(debug=True)