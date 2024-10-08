#!/usr/bin/env python3
from flask import Flask, request, make_response
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower

app = Flask(__name__)  # Corrected to __name__
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes', methods=['GET'])
def get_all_heroes():
    heroes = Hero.query.all()
    
    response = [{
        'id': hero.id,
        'name': hero.name,
        'super_name': hero.super_name
    } for hero in heroes]

    return make_response(response, 200)

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    hero = Hero.query.filter(Hero.id == id).first()
    
    if hero:
        response = {
            'id': hero.id,
            'name': hero.name,
            'super_name': hero.super_name,
            'hero_powers': [{
                'hero_id': hp.hero_id,
                'id': hp.id,
                'power': {
                    'description': hp.power.description,
                    'id': hp.power.id,
                    'name': hp.power.name
                },  
                'power_id': hp.power_id,
                'strength': hp.strength
            } for hp in hero.hero_powers]
        }
        return make_response(response, 200)
    else:
        return make_response({'error': 'Hero not found'}, 404)

@app.route('/powers', methods=['GET'])
def get_all_powers():
    response = [{
        'description': power.description,
        'id': power.id,
        'name': power.name
    } for power in Power.query.all()]

    return make_response(response, 200)

@app.route('/powers/<int:id>', methods=['PATCH', 'GET'])
def get_power_by_id(id):
    power = Power.query.get(id)

    if request.method == 'GET':
        if power:
            response = {
                'description': power.description,
                'id': power.id,
                'name': power.name
            }
            return make_response(response, 200)
        else:
            return make_response({'error': 'Power not found'}, 404)

    elif request.method == 'PATCH':
        if power is None:
            return make_response({'error': 'Power not found'}, 404)

        if not request.is_json:
            return make_response({'error': 'Invalid request. Content-Type must be application/json.'}, 400)

        data = request.get_json()

        # Adjusted validation response
        if 'description' not in data or len(data['description']) < 20:
            return make_response({'errors': ['Description must be at least 20 characters long']}, 400)

        power.description = data['description']
        db.session.commit()

        response = {
            'description': power.description,
            'id': power.id,
            'name': power.name
        }
        return make_response(response, 200)  # Return 200 after a successful update

@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()

    if data['strength'] not in ['Strong', 'Weak', 'Average']:
        return make_response({'errors': ['Strength must be one of: Strong, Weak, Average']}, 400)

    hero = Hero.query.get(data['hero_id'])
    power = Power.query.get(data['power_id'])

    if not hero or not power:
        return make_response({'errors': ['Hero or Power not found']}, 404)

    hero_power = HeroPower(
        strength=data['strength'],
        power_id=data['power_id'],
        hero_id=data['hero_id']
    )

    db.session.add(hero_power)
    db.session.commit()

    response = {
        'id': hero_power.id,
        'hero_id': hero_power.hero_id,
        'power_id': hero_power.power_id,
        'strength': hero_power.strength,
        'hero': {
            'id': hero.id,
            'name': hero.name,
            'super_name': hero.super_name
        },
        'power': {
            'description': power.description,
            'id': power.id,
            'name': power.name
        }
    }

    return make_response(response, 201)  # Return 201 for resource creation

if __name__ == '__main__':  # Corrected to __main__
    app.run(port=5550, debug=True)
