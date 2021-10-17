import base64
from datetime import datetime
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
from cryptography.fernet import Fernet
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash
from app import db

def encrypt(data, postkey):
    return Fernet(postkey).encrypt(bytes(data, 'utf-8'))

def decrypt(data, postkey):
    return Fernet(postkey).decrypt(data).decode("utf-8")

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    registered_on = db.Column(db.DateTime, nullable=False)
    last_logged_in = db.Column(db.DateTime, nullable=True)
    current_logged_in = db.Column(db.DateTime, nullable=True)

    # Crypto Key for user posts
    postkey = db.Column(db.BLOB)
    pinkey = db.Column(db.String(100), nullable=False)

    blogs = db.relationship('Post')

    def __init__(self, username, password, pinkey):
        self.username = username
        self.password = generate_password_hash(password)
        self.postkey = base64.urlsafe_b64encode(scrypt(password, str(get_random_bytes(32)), 32, N=2
                                                       ** 14, r=8, p=1))
        self.pinkey = pinkey
        self.registered_on = datetime.now()
        self.last_logged_in = None
        self.current_logged_in = None

class Post(db.Model):
    __tablename__ = 'posts'     # name of the table in the db

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, db.ForeignKey(User.username), nullable=True)
    created = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.Text, nullable=False, default=False)
    body = db.Column(db.Text, nullable=False, default=False)

    def __init__(self, username, title, body, postkey):
        self.username = username
        self.created = datetime.now()
        self.title = encrypt(title, postkey)
        self.body = encrypt(body, postkey)

    def update_post(self, title, body, postkey):
        self.title = encrypt(title, postkey)
        self.body = encrypt(body, postkey)
        db.session.commit()

    def view_post(self, postkey):
        self.title = Fernet.decrypt(self.title, postkey)
        self.body = Fernet.decrypt(self.body, postkey)


def init_db():
    db.drop_all()
    db.create_all()
    new_user = User(username='user1@test.com', password='password123', pinkey='BFB5S34STBLZCOB22K6PPYDCMZMH46OJ')
    db.session.add(new_user)
    db.session.commit()
