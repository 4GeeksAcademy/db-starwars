import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorites, TipoEnum

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

CURRENT_USER_ID = 1  # hardcoded until auth is implemented

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

# ─── PEOPLE ───────────────────────────────────────────────────────

@app.route("/people", methods=["GET"])
def get_people():
    people = Character.query.all()
    return jsonify([p.serialize() for p in people]), 200

@app.route("/people/<int:people_id>", methods=["GET"])
def get_person(people_id):
    person = db.session.get(Character, people_id)
    if not person:
        return jsonify({"error": "Character not found"}), 404
    return jsonify(person.serialize()), 200

# ─── PLANETS ──────────────────────────────────────────────────────

@app.route("/planets", methods=["GET"])
def get_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200

@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_planet(planet_id):
    planet = db.session.get(Planet, planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

# ─── USERS ────────────────────────────────────────────────────────

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200

@app.route("/users/favorites", methods=["GET"])
def get_user_favorites():
    user = db.session.get(User, CURRENT_USER_ID)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify([f.serialize() for f in user.favoritos]), 200

# ─── FAVORITE PLANETS ─────────────────────────────────────────────

@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_favorite_planet(planet_id):
    planet = db.session.get(Planet, planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    existing = Favorites.query.filter_by(user_id=CURRENT_USER_ID, planet_id=planet_id).first()
    if existing:
        return jsonify({"error": "Already in favorites"}), 400

    fav = Favorites(user_id=CURRENT_USER_ID, tipo=TipoEnum.PLANET, planet_id=planet_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.serialize()), 201

@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_favorite_planet(planet_id):
    fav = Favorites.query.filter_by(user_id=CURRENT_USER_ID, planet_id=planet_id).first()
    if not fav:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Favorite deleted"}), 200

# ─── FAVORITE PEOPLE ──────────────────────────────────────────────

@app.route("/favorite/people/<int:people_id>", methods=["POST"])
def add_favorite_people(people_id):
    person = db.session.get(Character, people_id)
    if not person:
        return jsonify({"error": "Character not found"}), 404

    existing = Favorites.query.filter_by(user_id=CURRENT_USER_ID, character_id=people_id).first()
    if existing:
        return jsonify({"error": "Already in favorites"}), 400

    fav = Favorites(user_id=CURRENT_USER_ID, tipo=TipoEnum.CHARACTER, character_id=people_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.serialize()), 201

@app.route("/favorite/people/<int:people_id>", methods=["DELETE"])
def delete_favorite_people(people_id):
    fav = Favorites.query.filter_by(user_id=CURRENT_USER_ID, character_id=people_id).first()
    if not fav:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Favorite deleted"}), 200

# ─── RUN ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3001)), debug=True)