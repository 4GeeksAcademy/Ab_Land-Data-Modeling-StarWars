import os
from flask_admin import Admin
from models import db, User, Character, Planet, Film, Favorites_Characters, Favorites_Planets, Favorites_Films, Natives_Planets, Appearance_Characters, Appearance_Planets
from flask_admin.contrib.sqla import ModelView


class User_MV(ModelView):
    column_auto_selected_related = True
    column_list = ['id', 'is_active', 'user_name', 'email',
                   'password', 'fav_char', 'fav_planet', 'fav_film']


class Character_MV(ModelView):
    column_auto_selected = True
    column_list = ['id', 'full_name', 'birth_year', 'gender', 'height_mts', 'weigth_kg',
                   'skin_tone', 'eye_color', 'hair_color', 'favorite_by', 'home_planet', 'appearance']


class Planet_MV(ModelView):
    column_auto_selected = True
    column_list = ['id', 'name', 'climate', 'terrain', 'population_count', 'gravity', 'diameter',
                   'water_surface', 'orvital_period', 'rotation_period', 'favorite_by', 'natives', 'appearance']


class Film_MV(ModelView):
    column_auto_selected = True
    column_list = ['id', 'title', 'episode', 'director', 'producer', 'release_date',
                   'opening_crawl', 'favorite_by', 'feature_char', 'feature_planet']


class Favorites_Characters_MV(ModelView):
    column_auto_selected = True
    column_list = ['id', 'user_id', 'user', 'character_id', 'character']


class Favorites_Planets_MV(ModelView):
    column_auto_selected = True
    column_list = ['id', 'user_id', 'user', 'planet_id', 'planet']


class Favorites_Films_MV(ModelView):
    column_auto_selected = True
    column_list = ['id', 'user_id', 'user', 'film_id', 'film']


class Natives_Planets_MV(ModelView):
    column_auto_selected = True
    column_list = ['id', 'character_id', 'character', 'planet_id', 'planet']


class Appearance_Characters_MV(ModelView):
    column_auto_selected = True
    column_list = ['id', 'character_id', 'character', 'film_id', 'film']


class Appearance_Planets_MV(ModelView):
    column_auto_selected = True
    column_list = ['id', 'planet_id', 'planet', 'film_id', 'film']


def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(User_MV(User, db.session))
    admin.add_view(Character_MV(Character, db.session))
    admin.add_view(Planet_MV(Planet, db.session))
    admin.add_view(Film_MV(Film, db.session))
    admin.add_view(Favorites_Characters_MV(Favorites_Characters, db.session))
    admin.add_view(Favorites_Planets_MV(Favorites_Planets, db.session))
    admin.add_view(Favorites_Films_MV(Favorites_Films, db.session))
    admin.add_view(Natives_Planets_MV(Natives_Planets, db.session))
    admin.add_view(Appearance_Characters_MV(Appearance_Characters, db.session))
    admin.add_view(Appearance_Planets_MV(Appearance_Planets, db.session))

    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))
