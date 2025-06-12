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
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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


# GETs

@app.route('/users', methods=['GET'])
def get_users():
    users_query = User.query.all()
    users_serialized = []
    for user in users_query:
        if user.is_active is False:
            pass
        else:
            users_serialized.append(user.serialize())
    return jsonify({'msg': 'ok', 'GETTED': users_serialized}), 200


@app.route('/user/<int:id>')
def get_user_by(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({'msg': f'User_id:{id}, not found'}), 404
    user_serialized = user.serialize()
    return jsonify({'msg': 'ok', 'GETTED': user_serialized}), 200


@app.route('/characters', methods=['GET'])
def get_characters():
    characters_query = Character.query.all()
    character_serialized = list(
        map(lambda character: character.serialize(), characters_query))
    return jsonify({'msg': 'ok', 'GETTED': character_serialized}), 200


@app.route('/character/<int:id>', methods=['GET'])
def get_character_by(id):
    character = Character.query.get(id)
    if character is None:
        return jsonify({'msg': 'Character not found'}), 404
    character_serialized = character.serialize()

    favorite_by = []
    for favorite in character.favorite_by:
        favorite_by.append(favorite.user.serialize())
    character_serialized['favorite_by'] = favorite_by

    home_planet = []
    for home in character.home_planet:
        home_planet.append(home.planet.serialize())
    character_serialized['home_planet'] = home_planet

    appearances = []
    for appearance in character.appearance:
        appearances.append(appearance.film.serialize())
    character_serialized['appearances'] = appearances

    return jsonify({'msg': 'ok', 'GETTED': character_serialized}), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets_query = Planet.query.all()
    planets_serialized = list(
        map(lambda planet: planet.serialize(), planets_query))
    return jsonify({'msg': 'ok', 'GETTED': planets_serialized}), 200


@app.route('/planet/<int:id>', methods=['GET'])
def get_planet_by(id):
    planet = Planet.query.get(id)
    if planet is None:
        return jsonify({'msg': 'Planet not found'}), 404
    planet_serialized = planet.serialize()

    favorite_by = []
    for favorite in planet.favorite_by:
        favorite_by.append(favorite.user.serialize())
    planet_serialized['favorite_by'] = favorite_by

    natives = []
    for native in planet.natives:
        natives.append(native.character.serialize())
    planet_serialized['natives'] = natives

    appearances = []
    for appearance in planet.appearance:
        appearances.append(appearance.film.serialize())
    planet_serialized['appearances'] = appearances

    return jsonify({'mgs': 'ok', 'GETTED': planet_serialized}), 200


@app.route('/films', methods=['GET'])
def get_films():
    films_query = Film.query.all()
    films_serialized = list(map(lambda film: film.serialize(), films_query))
    return jsonify({'msg': 'ok', 'GETTED': films_serialized}), 200


@app.route('/film/<int:id>', methods=['GET'])
def get_film_by(id):
    film = Film.query.get(id)
    if film is None:
        return jsonify({'msg': 'Film not found'}), 404
    film_serialized = film.serialize()

    favorite_by = []
    for favorite in film.favorite_by:
        favorite_by.append(favorite.user.serialize())
    film_serialized['favorite_by'] = favorite_by

    feature_char = []
    for feature in film.feature_char:
        feature_char.append(feature.character.serialize())
    film_serialized['feature_char'] = feature_char

    feature_planet = []
    for feature in film.feature_planet:
        feature_planet.append(feature.planet.serialize())
    film_serialized['feature_planet'] = feature_planet

    return jsonify({'msg': 'ok', 'GETTED': film_serialized}), 200


@app.route('/user/<int:id>/favorites', methods=['GET'])
def get_favorites_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({'msg': f'User_id:{id}, not found'}), 404

    fav_char = []
    for favorite in user.fav_char:
        fav_char.append(
            {'reg_id': favorite.id, 'Character': favorite.character.serialize()})
    fav_planet = []
    for favorite in user.fav_planet:
        fav_planet.append(
            {'reg_id': favorite.id, 'Planet': favorite.planet.serialize()})
    fav_film = []
    for favorite in user.fav_film:
        fav_film.append(
            {'reg_id': favorite.id, 'Film': favorite.film.serialize()})
    favorites = [fav_char, fav_planet, fav_film]

    return jsonify({'msg': 'ok', 'GETTED': favorites}), 200


# POSTs

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

    return jsonify({'msg': 'ok', 'POSTED': new_user.serialize()}), 200


@app.route('/user/<int:user_id>/favorites/character/<character_id>', methods=['POST'])
def post_favorites_characters(user_id, character_id):
    user = User.query.get(user_id)
    if user is None or user.is_active is False:
        return jsonify({'msg': f'User_id:{user_id}, not found'}), 404
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({'msg': f'Character_id:{character_id}, not found'}), 404

    favorited = Favorites_Characters.query.filter_by(
        user_id=user_id, character_id=character_id).first()
    if favorited:
        return jsonify({'msg': f'Character: {character_id} already favorited'}), 400

    new_fav_char = Favorites_Characters()
    new_fav_char.user_id = user_id
    new_fav_char.character_id = character_id
    db.session.add(new_fav_char)
    db.session.commit()

    return jsonify({'msg': 'ok', 'POSTED': f'reg_id:{new_fav_char.id}, {new_fav_char}'}), 200


@app.route('/user/<int:user_id>/favorites/planet/<planet_id>', methods=['POST'])
def post_favorites_planets(user_id, planet_id):
    user = User.query.get(user_id)
    if user is None or user.is_active is False:
        return jsonify({'msg': f'User_id:{user_id}, not found'}), 404

    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({'msg': f'Planet_id: {planet_id}, not found'}), 404

    favorited = Favorites_Planets.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if favorited:
        return jsonify({'msg': f'Planet: {planet_id} already favorited'}), 400

    new_fav_planet = Favorites_Planets()
    new_fav_planet.user_id = user_id
    new_fav_planet.planet_id = planet_id
    db.session.add(new_fav_planet)
    db.session.commit()

    return jsonify({'msg': 'ok', 'POSTED': f'reg_id:{new_fav_planet.id}, {new_fav_planet}'}), 200


@app.route('/user/<int:user_id>/favorites/film/<film_id>', methods=['POST'])
def post_favorites_films(user_id, film_id):

    user = User.query.get(user_id)
    if user is None or user.is_active is False:
        return jsonify({'msg': f'User_id:{user_id}, not found'}), 404

    film = Film.query.get(film_id)
    if film is None:
        return jsonify({'msg': f'film_id:{film_id}, not fount'}), 404

    favorited = Favorites_Films.query.filter_by(
        user_id=user_id, film_id=film_id).first()
    if favorited:
        return jsonify({'msg': f'Film: {film_id} already favorited'}), 400

    new_fav_film = Favorites_Films()
    new_fav_film.user_id = user_id
    new_fav_film.film_id = film_id
    db.session.add(new_fav_film)
    db.session.commit()

    return jsonify({'msg': 'ok', 'POSTED': f'reg_id:{new_fav_film.id}, {new_fav_film}'}), 200


@app.route('/character', methods=['POST'])
def post_character():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'No body was retrive, add one'}), 400

    new_character = Character()

    required_fields = ['full_name']
    for field in required_fields:
        if field not in body:
            return jsonify({'msg': f'Missing field: {field}, required!'}), 400
        else:
            setattr(new_character, field, body[field])

    extra_fields = ['birth_year', 'gender', 'height_mts',
                    'weight_kg', 'skin_tone', 'eye_color', 'hair_color']
    fields_missing = []
    for field in extra_fields:
        if field in body:
            setattr(new_character, field, body[field])
        else:
            fields_missing.append(field)

    db.session.add(new_character)
    
    if 'home_planet' not in body:
        fields_missing.append('appearance')
    elif type(body['home_planet']) is not int:
        return jsonify({'mgs': 'home_planet must be a planet_id'}), 400
    
    if Planet.query.get(body['home_planet']) is None:
        return jsonify({'mgs': f'planet_id:{body['home_planet']} not found'}), 400
    else:
        new_reg_app_planet = Natives_Planets()
        new_reg_app_planet.character_id = new_character.id
        new_reg_app_planet.planet_id = body['home_planet']
        db.session.add(new_reg_app_planet)
            
    db.session.commit()

    return jsonify({'msg': 'ok', 'Filds_Missing': fields_missing, 'POSTED': new_character.serialize()}), 200


@app.route('/planet', methods=['POST'])
def post_planet():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'No body was retrive, add one'}), 400

    new_planet = Planet()

    required_fields = ['name']
    for field in required_fields:
        if field not in body:
            return jsonify({'msg': f'Missing field: {field}, required!'}), 400
        else:
            setattr(new_planet, field, body[field])

    extra_fields = ['climate', 'terrain', 'population_count', 'gravity',
                    'diameter', 'water_surface', 'orbital_period', 'rotation_period']
    fields_missing = []
    for field in extra_fields:
        if field in body:
            setattr(new_planet, field, body[field])
        else:
            fields_missing.append(field)

    db.session.add(new_planet)
    db.session.commit()

    return jsonify({'msg': 'ok', 'Filds_Missing': fields_missing, 'POSTED': new_planet.serialize()}), 200


@app.route('/film', methods=['POST'])
def post_film():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'No body was retrive, add one'}), 400

    new_film = Film()

    required_fields = ['title', 'episode']
    for field in required_fields:
        if field not in body:
            return jsonify({'msg': f'Missing field: {field}, required!'}), 400
        else:
            setattr(new_film, field, body[field])

    extra_fields = ['director', 'producer', 'release_date', 'opening_crawl']
    fields_missing = []
    for field in extra_fields:
        if field in body:
            setattr(new_film, field, body[field])
        else:
            fields_missing.append(field)
    db.session.add(new_film)

    feature_list=['feature_char','feature_planet']
    for feat in feature_list:
        if feat not in body:
            fields_missing.append(feat)
        elif type(body[feat]) is not list :
            return jsonify({'mgs': f'{feat} must be a list of ids'}), 400

    for app in body['feature_planet']:
        if Planet.query.get(app) is None:
            return jsonify({'msg':f'Planet_id: {app} not found'}), 400
        else:
            new_reg = Appearance_Planets()
            new_reg.planet_id = app
            new_reg.film_id = new_film.id
            db.session.add(new_reg)
    
    for app in body['feature_char']:
        if Character.query.get(app) is None:
            return jsonify({'msg':f'Character_id: {app} not found'}), 400
        else:
            new_reg = Appearance_Characters()
            new_reg.character_id = app
            new_reg.film_id = new_film.id
            db.session.add(new_reg)        

    db.session.commit()

    return jsonify({'msg': 'ok', 'Filds_Missing': fields_missing, 'POSTED': new_film.serialize()}), 200

# PUTs


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
    return jsonify({'msg': 'ok', 'PUT': updated_user_serialized}), 200


@app.route('/character/<int:id>', methods=['PUT'])
def put_character_by(id):
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'No body was retrive, add one'}), 400

    character = Character.query.get(id)
    if character is None:
        return jsonify({'msg': f'Character_id:{id}, not found'}), 404

    fields = ['full_name', 'birth_year', 'gender', 'height_mts',
              'weight_kg', 'skin_tone', 'eye_color', 'hair_color']
    fields_not_edited = []
    for field in fields:
        if field in body:
            setattr(character, field, body[field])
        else:
            fields_not_edited.append(field)

    db.session.commit()

    return jsonify({'msg': 'ok', 'Filds_not_edited': fields_not_edited, 'PUT': character.serialize()}), 200


@app.route('/planet/<int:id>', methods=['PUT'])
def put_planet_by(id):
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'No body was retrive, add one'}), 400

    planet = Planet.query.get(id)
    if planet is None:
        return jsonify({'msg': f'planet_id:{id}, not found'}), 404

    fields = ['name', 'climate', 'terrain', 'population_count', 'gravity',
              'diameter', 'water_surface', 'orbital_period', 'rotation_period']
    fields_not_edited = []
    for field in fields:
        if field in body:
            setattr(planet, field, body[field])
        else:
            fields_not_edited.append(field)

    db.session.commit()

    return jsonify({'msg': 'ok', 'Filds_not_edited': fields_not_edited, 'PUT': planet.serialize()}), 200


@app.route('/film/<int:id>', methods=['PUT'])
def put_film_by(id):
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'No body was retrive, add one'}), 400

    film = Film.query.get(id)
    if film is None:
        return jsonify({'msg': f'Film_id:{id}, not found'}), 404

    fields = ['title', 'episode', 'director',
              'producer', 'release_date', 'opening_crawl']
    fields_not_edited = []
    for field in fields:
        if field in body:
            setattr(film, field, body[field])
        else:
            fields_not_edited.append(field)

    db.session.commit()

    return jsonify({'msg': 'ok', 'Filds_not_edited': fields_not_edited, 'PUT': film.serialize()}), 200


# DELETEs

@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user_by(id):
    user = User.query.get(id)
    if user is None or user.is_active is False:
        return jsonify({'msg': f'User_id:{id}, not found'}), 404
    not user.is_active
    db.session.commit()
    return jsonify({'msg': 'ok', 'DELETED': f'USER: {user.user_name}'}), 200


@app.route('/character/<int:id>', methods=['DELETE'])
def delete_character_by(id):
    character = Character.query.get(id)
    if character is None:
        return jsonify({'msg': f'Character_id:{id}, not found'}), 404
    db.session.delete(character)
    db.session.commit()
    return jsonify({'msg': 'ok', 'DELETED': f'Character: {character.full_name}'}), 200


@app.route('/planet/<int:id>', methods=['DELETE'])
def delete_planet_by(id):
    planet = Planet.query.get(id)
    if planet is None:
        return jsonify({'msg': f'Planet_id:{id}, not found'}), 404
    db.session.delete(planet)
    db.session.commit()
    return jsonify({'msg': 'ok', 'DELETED': f'Planet: {planet.name}'}), 200


@app.route('/film/<int:id>', methods=['DELETE'])
def delete_film_by(id):
    film = Film.query.get(id)
    if film is None:
        return jsonify({'msg': f'Film_id:{id}, not found'}), 404

    db.session.delete(film)
    db.session.commit()
    return jsonify({'msg': 'ok', 'DELETE': f'Film: Episode {film.episode}'}), 200


# Favorites
# By_register
@app.route('/favorites/character/<int:reg_id>', methods=['DELETE'])
def delete_user_fav_char(reg_id):
    favorite = Favorites_Characters.query.get(reg_id)
    if favorite is None:
        return jsonify({'msg': f'Registre of Favorite_Characters: {reg_id} not found'}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'msg': 'ok', 'DELETED': f'Registre of Favorites_Characters: {reg_id}'}), 200


# By_filtering
@app.route('/user/<int:user_id>/favorites/character/<int:id>', methods=['DELETE'])
def delete_favorite_character_by(user_id, id):
    user = User.query.get(user_id)
    if user is None or user.is_active is False:
        return jsonify({'msg': f'User_id:{user_id}, not found'}), 404

    character = Character.query.get(id)
    if character is None:
        return jsonify({'msg': f'Character_id:{id}, not found'}), 404

    fav_char = Favorites_Characters.query.filter_by(
        user_id=user_id, character_id=id).first()
    if fav_char is None:
        return jsonify({'msg': f'Favorite register not found for user_id:{user_id} {user.user_name} and character_id:{id} {character.full_name}'}), 404

    db.session.delete(fav_char)
    db.session.commit()

    return jsonify({'msg': 'Favorite register deleted successfully', 'DELETED': f'Favorites_Characters_id: {fav_char.id}'}), 200


@app.route('/user/<int:user_id>/favorites/planet/<int:id>', methods=['DELETE'])
def delete_favorite_planet_by(user_id, id):
    user = User.query.get(user_id)
    if user is None or user.is_active is False:
        return jsonify({'msg': f'User_id:{user_id}, not found'}), 404

    planet = Planet.query.get(id)
    if planet is None:
        return jsonify({'msg': f'Planet_id:{id}, not found'}), 404

    fav_planet = Favorites_Planets.query.filter_by(
        user_id=user_id, planet_id=id).first()
    if fav_planet is None:
        return jsonify({'msg': f'Favorite register not found for user_id:{user_id} {user.user_name} and planet_id:{id} {planet.name}'}), 404

    db.session.delete(fav_planet)
    db.session.commit()

    return jsonify({'msg': 'Favorite register deleted successfully', 'DELETED': f'Favorites_Planets_id: {fav_planet.id}'}), 200


@app.route('/user/<int:user_id>/favorites/film/<int:id>', methods=['DELETE'])
def delete_favorite_film_by(user_id, id):
    user = User.query.get(user_id)
    if user is None or user.is_active is False:
        return jsonify({'msg': f'User_id:{user_id}, not found'}), 404

    film = Film.query.get(id)
    if film is None:
        return jsonify({'msg': f'Film_id:{id}, not found'}), 404

    fav_film = Favorites_Films.query.filter_by(
        user_id=user_id, film_id=id).first()
    if fav_film is None:
        return jsonify({'msg': f'Favorite register not found for user_id:{user_id} {user.user_name} and film_id:{id} Episode {film.episode}'}), 404

    db.session.delete(fav_film)
    db.session.commit()

    return jsonify({'msg': 'Favorite register deleted successfully', 'DELETED': f'Favorites_Films_id: {fav_film.id}'}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
