from dataclasses import dataclass
from app import db
from marshmallow import Schema, fields


@dataclass
class Pokemon(db.Model):
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rank: int = db.Column(db.Integer, nullable=False)
    name: str = db.Column(db.String, unique=True, nullable=False)
    type1: str = db.Column(db.String)
    type2: str = db.Column(db.String)
    total: int = db.Column(db.BigInteger)
    hp: int = db.Column(db.Integer)
    attack: int = db.Column(db.Integer)
    defense: int = db.Column(db.Integer)
    sp_atk: int = db.Column(db.Integer)
    sp_def: int = db.Column(db.Integer)
    speed: int = db.Column(db.Integer)
    generation: int = db.Column(db.Integer)
    legendary: bool = db.Column(db.Boolean)


class PokemonSchema(Schema):
    rank = fields.Integer(data_key="#", dump_only=True)
    name = fields.String(data_key="Name")
    type1 = fields.String(data_key="Type 1")
    type2 = fields.String(data_key="Type 2")
    total = fields.Integer(data_key="Total")
    hp = fields.Integer(data_key="HP")
    attack = fields.Integer(data_key="Attack")
    defense = fields.Integer(data_key="Defense")
    sp_atk = fields.Integer(data_key="Sp. Atk")
    sp_def = fields.Integer(data_key="Sp. Def")
    speed = fields.Integer(data_key="Speed")
    generation = fields.Integer(data_key="Generation")
    legendary = fields.Boolean(data_key="Legendary")


pokemon_schema = PokemonSchema()
pokemons_schema = PokemonSchema(many=True)
