from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
import os
import re

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    followed_users = db.Column(db.Integer, nullable=False)
    users_following_me = db.Column(db.Integer, nullable=False)

    created_events = db.relationship('Event', backref='user', lazy=True)
    signedup_events = db.relationship('Signedup_events', backref='user', lazy=True)

    def validate_email(self, email):
        regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(regex, email) is not None

    def set_email(self, email):
        if not self.validate_email(email):
            raise ValueError("Invalid email address")
        self.email = email
    
    def set_password(self, password):
        # Genera un salt único para el usuario
        self.salt = os.urandom(32)
        # Aplica el hash a la contraseña junto con el salt
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), self.salt, 100000)
        # Almacena el hash en la base de datos
        self.password = hashed_password

    def check_password(self, password):
        # Aplica el mismo hash a la contraseña proporcionada junto con el salt almacenado
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), self.salt, 100000)
        # Compara el hash generado con el hash almacenado en la base de datos
        return hashed_password == self.password

    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "followed_users": self.followed_users,
            "users_following_me": self.users_following_me,
        }
    
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(240), nullable=False)
    type = db.Column(db.Enum('nature', 'party', 'culture', 'relax', 'family', 'sport', name='event_type_enum'), nullable=False, index=True)
    date = db.Column(db.Integer, nullable=False)
    place = db.Column(db.String(240), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(750), nullable=False)
    language = db.Column(db.Enum('spanish', 'catalan', 'english', 'german', 'french'), nullable=False)
    gender = db.Column(db.Enum('female_only', 'queer_only', 'all_genders', 'no_preferences', name='gender_selection_enum'), nullable=False)
    price_type = db.Column(db.Enum('free', 'paid'), nullable=False)
    price = db.Column(db.Integer)
    min_age = db.Column(db.Integer)
    max_age = db.Column(db.Integer)
    min_people = db.Column(db.Integer)
    max_people = db.Column(db.Integer)
    lgtbi = db.Column(db.Boolean(), nullable=False)
    pet_friendly = db.Column(db.Boolean(), nullable=False)
    kid_friendly = db.Column(db.Boolean(), nullable=False)

    def validate_date(self, date_str):
        try:
            # Intenta analizar la cadena de fecha en un objeto datetime
            datetime.strptime(date_str, '%d-%m-%Y')
            return True
        except ValueError:
            return False

    def set_date(self, date_str):
        if not self.validate_date(date_str):
            raise ValueError("Invalid date format. Date should be in the format 'DD-MM-YYYY'")
        self.date = datetime.strptime(date_str, '%d-%m-%Y')

    __table_args__ = (
    db.CheckConstraint('min_age >= 0', name='event_min_age_positive'),
    db.CheckConstraint('max_age >= min_age', name='event_max_age_greater_than_min_age'),
    db.CheckConstraint('min_people >= 0', name='event_min_people_positive'),
    db.CheckConstraint('max_people >= min_people', name='event_max_people_greater_than_min_people')
    )

    def validate_age_range(self):
        # Verifica que min_age sea menor o igual que max_age
        if self.min_age is not None and self.max_age is not None:
            if self.min_age > self.max_age:
                raise ValueError("min_age must be less than or equal to max_age")

    def validate_people_range(self):
        # Verifica que min_people sea menor o igual que max_people
        if self.min_people is not None and self.max_people is not None:
            if self.min_people > self.max_people:
                raise ValueError("min_people must be less than or equal to max_people")

    def save(self):
        # Antes de guardar el evento, valida los rangos de edad y personas
        self.validate_age_range()
        self.validate_people_range()
        # Guarda el evento en la base de datos
        db.session.add(self)
        db.session.commit()
        
    def __repr__(self):
        return f'<Event {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "user_owner": self.user_owner,
            "name": self.name,
            "type": self.type,
            "date": self.date,
            "place": self.place,
            "duration": self.duration,
            "description": self.description,
            "language": self.language,
            "gender": self.gender,
            "price_type": self.price_type,
            "price": self.price,
            "min_age": self.min_age,
            "max_age": self.max_age,
            "min_people": self.min_people,
            "max_people": self.max_people,
            "lgtbi": self.lgtbi,
            "pet_friendly": self.pet_friendly,
            "kid_friendly": self.kid_friendly,
        }

class Signedup_events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    
    def __repr__(self):
        return f'<Signedup_events {self.user_id}>'

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_id": self.event_id,
        }