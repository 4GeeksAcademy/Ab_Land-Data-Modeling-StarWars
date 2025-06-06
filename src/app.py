"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Film, Favorites_Characters, Favorites_Planets, Favorites_Films, Natives_Planets, Appearance_Characters, Appearance_Planets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

#GETs

@app.route('/users',methods=['GET'])
def get_users():
    users_query = User.query.all()
    users_serialized = []
    for user in users_query:
        users_serialized.append(user.serialize())
    return jsonify ({'msg':'ok', 'GETTED': users_serialized}), 200

@app.route('/user/<int:id>')
def get_user_by(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({'msg': f'User_id:{id}, not found'}), 404
    user_serialized = user.serialize()
    return jsonify( {'msg': 'ok', 'GETTED':user_serialized}), 200

@app.route('/characters',methods=['GET'])
def get_characters():
    characters_query = Character.query.all()
    character_serialized = list(map(lambda character: character.serialize(), characters_query ))
    return jsonify ({'msg':'ok', 'GETTED': character_serialized}), 200

@app.route('/character/<int:id>', methods=['GET'])
def get_character_by(id):
    character = Character.query.get(id)
    if character is None:
        return jsonify({'msg': 'Character not found'}), 404
    character_serialized = character.serialize()
    return jsonify({'msg':'ok', 'GETTED':character_serialized}), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets_query = Planet.query.all()
    planets_serialized = list(map(lambda planet: planet.serialize(), planets_query))
    return jsonify( {'msg': 'ok', 'GETTED': planets_serialized}), 200

@app.route('/planet/<int:id>', methods=['GET'])
def get_planet_by(id):
    planet = Planet.query.get(id)
    if planet is None:
        return jsonify({'msg': 'Planet not found'}), 404
    planet_serialized = planet.serialize()
    return jsonify({'mgs': 'ok', 'GETTED':planet_serialized}), 200

@app.route('/films', methods=['GET'])
def get_films():
    films_query = Film.query.all()
    films_serialized = list(map(lambda film: film.serialize(), films_query))
    return jsonify( {'msg': 'ok', 'GETTED':films_serialized}), 200

@app.route('/film/<int:id>', methods=['GET'])
def get_film_by(id):
    film = Film.query.get(id)
    if film is None:
        return jsonify({'msg': 'Film not found'}), 404
    film_serialized = film.serialize()
    return jsonify({'msg': 'ok', 'GETTED': film_serialized}), 200

@app.route('/user/<int:id>/favorites', methods=['GET'])
def get_favorites_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({'msg': f'User_id:{id}, not found'}), 404
    fav_char = []
    for favorite in user.fav_char:
        fav_char.append({'reg_id':favorite.id , 'Character':favorite.character.serialize()})
    fav_planet = []    
    for favorite in user.fav_planet:
        fav_planet.append({'reg_id': favorite.id, 'Planet':favorite.planet.serialize()})
    fav_film = []    
    for favorite in user.fav_film:
        fav_film.append({'reg_id': favorite.id, 'Film':favorite.film.serialize()}) 
    favorites = [fav_char,fav_planet,fav_film]       

    return jsonify({'msg': 'ok', 'GETTED': favorites}), 200    

#POSTs
@app.route('/user', methods=['POST'])
def post_user():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'No body was retrive, add one'}), 400
    
    required_fields = ['user_name', 'email', 'password']
    for field in required_fields:
        if field not in body:
            return jsonify({'msg': f'Missing field: {field}, required!'}), 400
        
    new_user = User()
    new_user.user_name = body['user_name']
    new_user.email = body['email']
    new_user.password = body['password']
    new_user.is_active = True
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg':'ok', 'POSTED': new_user.serialize()}), 200

@app.route('/user/<int:user_id>/favorites/character/<character_id>', methods=['POST'])
def post_favorites_character(user_id,character_id):
    user = User.query.get(user_id)
    if user is None or user.is_active is False:
        return jsonify({'msg': f'User_id:{user_id}, not found'}), 404
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({'msg': f'Character_id:{character_id}, not found'}), 404
    new_fav_char = Favorites_Characters()
    new_fav_char.user_id = user_id
    new_fav_char.character_id = character_id
    db.session.add(new_fav_char)
    db.session.commit()
    print(new_fav_char)
    
    return jsonify({'msg':'ok', 'POSTED': f'reg_id:{new_fav_char.id}, {new_fav_char}'}), 200

#PUTs
@app.route('/user/<int:id>', methods=['PUT'])
def put_user_by(id):
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'No body was retrive, add one'}), 400 
    user = User.query.get(id)
    if user is None:
        return jsonify({'msg': f'User_id:{id}, not found'}), 404    
    if 'user_name' in body:
        user.user_name = body['user_name']
    if 'email' in body:
        user.email = body['email']
    if 'password' in body:
        user.password = body['password']
    db.session.commit()     
    updated_user_serialized = user.serialize()  
    return jsonify({'msg':'ok', 'PUT':updated_user_serialized}), 200  

#DELETEs
@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user_by(id):    
    user = User.query.get(id)
    if user is None or user.is_active is False:
        return jsonify({'msg': f'User_id:{id}, not found'}), 404
    not user.is_active
    db.session.commit()
    return jsonify({'msg':'ok', 'DELETED':f'USER: {user.user_name}'}), 200

@app.route('/user/<int:user_id>/favorites/character/<int:reg_id>',methods=['DELETE'])
def delete_user_fav_char(user_id,reg_id):
    user = User.query.get(user_id)
    if user is None or user.is_active is False:
        return jsonify({'msg': f'User_id:{user_id}, not found'}), 404
    favorite = Favorites_Characters.query.get(reg_id)
    if favorite is None:
        return jsonify({'msg': f'Registre of Favorite_Characters not found'}), 404
    db.session.delete()
    db.session.commit()
    return jsonify({'msg':'ok', 'DELETED':f'Registre of favorite {reg_id}'}), 200

@app.route('/user/<int:user_id>/favorites/planet/<int:reg_id>',methods=['DELETE'])
def delete_user_fav_planet(user_id,reg_id):
    user = User.query.get(user_id)
    if user is None or user.is_active is False:
        return jsonify({'msg': f'User_id:{user_id}, not found'}), 404
    favorite = Favorites_Planets.query.get(reg_id)
    if favorite is None:
        return jsonify({'msg': f'Registre of Favorite_Planets not found'}), 404
    db.session.delete()
    db.session.commit()
    return jsonify({'msg':'ok', 'DELETED':f'Registre of favorite {reg_id}'}), 200

@app.route('/user/<int:user_id>/favorites/film/<int:reg_id>',methods=['DELETE'])
def delete_user_fav_film(user_id,reg_id):
    user = User.query.get(user_id)
    if user is None or user.is_active is False:
        return jsonify({'msg': f'User_id:{user_id}, not found'}), 404
    favorite = Favorites_Films.query.get(reg_id)
    if favorite is None:
        return jsonify({'msg': f'Registre of Favorite_Films not found'}), 404
    db.session.delete()
    db.session.commit()
    return jsonify({'msg':'ok', 'DELETED':f'Registre of favorite {reg_id}'}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
