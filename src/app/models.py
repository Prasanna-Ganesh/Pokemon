from dataclasses import dataclass
from app import db, app

# from marshmallow import Schema, fields
# import requests


@dataclass
class Pokemon(db.Model):
    id: int = db.Column(db.Integer, nullable=False, name="#")
    name: str = db.Column(db.String, primary_key=True, nullable=False, name="Name")
    type1: str = db.Column(db.String, name="Type 1")
    type2: str = db.Column(db.String, name="Type 2")
    total: int = db.Column(db.BigInteger, name="Total")
    hp: int = db.Column(db.Integer, name="HP")
    attack: int = db.Column(db.Integer, name="Attack")
    defense: int = db.Column(db.Integer, name="Defence")
    sp_atk: int = db.Column(db.Integer, name="Sp. Atk")
    sp_def: int = db.Column(db.Integer, name="Sp. Def")
    speed: int = db.Column(db.Integer, name="Speed")
    generation: int = db.Column(db.Integer, name="Generation")
    legendary: bool = db.Column(db.Boolean, name="Legendary")


with app.app_context():
    db.create_all()


# class PokemonSchema(Schema):
#     id = fields.Integer(data_key='#', dump_only=True)
#     name = fields.String(data_key='Name')
#     type1 = fields.String(data_key='Type 1')
#     type2 = fields.String(data_key='Type 2')
#     total = fields.Integer(data_key='Total')
#     hp = fields.Integer(data_key='HP')
#     attack = fields.Integer(data_key='Attack')
#     defense = fields.Integer(data_key='Defense')
#     sp_atk = fields.Integer(data_key='Sp. Atk')
#     sp_def = fields.Integer(data_key='Sp. Def')
#     speed = fields.Integer(data_key='Speed')
#     generation = fields.Integer(data_key='Generation')
#     legendary = fields.Boolean(data_key='Legendary')


# pokemon_schema = PokemonSchema()
# response = requests.get('https://coralvanda.github.io/pokemon_data.json')
# pokemon_data = response.json()

# for pokemon in pokemon_data:
#     new_pokemon = pokemon_schema.load(pokemon)
#     db.session.add(new_pokemon)

# db.session.commit()
