from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData()

db = SQLAlchemy(metadata=metadata)

class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'  # Corrected to __tablename__

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    super_name = db.Column(db.String, nullable=False)

    # Relationship to HeroPower
    powers = association_proxy('hero_powers', 'power', creator=lambda power_obj: HeroPower(power=power_obj))
    hero_powers = db.relationship('HeroPower', back_populates='hero', cascade='all, delete-orphan')

    # Serialization rules
    serialize_rules = ('-hero_powers.hero', '-hero_powers.power')

    def __repr__(self):  # Corrected to __repr__
        return f'<Hero {self.id} - {self.name}>'

class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'  # Corrected to __tablename__

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    # Relationship to HeroPower
    hero_powers = db.relationship('HeroPower', back_populates='power', cascade='all, delete-orphan')
    heroes = association_proxy('hero_powers', 'hero', creator=lambda hero_obj: HeroPower(hero=hero_obj))

    # Serialization rules
    serialize_rules = ('-hero_powers.power',)

    @validates('description')
    def validate_length(self, key, value):
        if len(value) < 20:
            raise ValueError('Description must be at least 20 characters long')
        return value

    @validates('name')
    def validate_name(self, key, value):
        if not value:
            raise ValueError('Name cannot be empty')
        return value

    def __repr__(self):  # Corrected to __repr__
        return f'<Power {self.id} - {self.name}>'

class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'  # Corrected to __tablename__

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)

    # Relationships back to Hero and Power
    hero = db.relationship('Hero', back_populates='hero_powers')
    power = db.relationship('Power', back_populates='hero_powers')

    # Serialization rules
    serialize_rules = ('-hero.hero_powers', 'power.hero_powers')

    VALID_STRENGTHS = ['Strong', 'Weak', 'Average']

    @validates('strength')
    def validate_strength(self, key, value):
        if value not in self.VALID_STRENGTHS:
            raise ValueError('Strength must be one of: Strong, Weak, Average')
        return value

    def __repr__(self):  # Corrected to __repr__
        return f'<HeroPower {self.id} - Strength: {self.strength}>'
