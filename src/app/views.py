from flask import Blueprint, jsonify, request
from app.models import Pokemon
import requests
from datetime import datetime as dt, timezone
from app import db, app
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert


pokemonapi = Blueprint("pokemonapi", __name__, url_prefix="/api/pokemon")


class PokemonException(Exception):
    def __init__(self, message, code=400):
        self.message = message
        self.code = code


@pokemonapi.errorhandler(PokemonException)
def handle_scheduler_exception(e):
    app.logger.exception(e)
    return {"success": False, "error": e.message}, e.code


@pokemonapi.route("/fetchpokemon/")
def fetchpokemon():
    url = "https://coralvanda.github.io/pokemon_data.json"
    response = requests.get(url)
    data = response.json()
    for pokemon in data:
        existing_pokemon = Pokemon.query.filter_by(name=pokemon["Name"]).first()
        if existing_pokemon:
            return "Pokemon data already present"
        new_pokemon = Pokemon(
            id=pokemon["#"],
            name=pokemon["Name"],
            type1=pokemon["Type 1"],
            type2=pokemon["Type 2"],
            total=pokemon["Total"],
            hp=pokemon["HP"],
            attack=pokemon["Attack"],
            defense=pokemon["Defense"],
            sp_atk=pokemon["Sp. Atk"],
            sp_def=pokemon["Sp. Def"],
            speed=pokemon["Speed"],
            generation=pokemon["Generation"],
            legendary=pokemon["Legendary"],
        )
        db.session.add(new_pokemon)
    db.session.commit()
    return "Data stored successfully!"


@pokemonapi.route("/pokemons/<int:id>/", methods=["GET"])
def get_pokemon(id=None):
    now = dt.now(timezone.utc)
    pokemons = Pokemon.query
    limit = int(request.args.get("limit", app.config.get("PAGE_LIMIT")))
    sort = request.args.get("sort", "id")  # Default sorting on Pokemon ID
    order = request.args.get("order", "asc")
    page_num = request.args.get("page", 1, type=int)
    search = request.args.get("search")
    generation = request.args.get("generation")
    legendary = request.args.get("legendary")

    if id:
        pokemons = Pokemon.query.filter(Pokemon.id == id)

    if search:
        search_query = f"%{search}%"
        pokemons = pokemons.filter(Pokemon.name.ilike(search_query))

    if generation:
        pokemons = pokemons.filter(Pokemon.generation == generation)

    if legendary:
        legendary = legendary.lower() == "true"
        pokemons = pokemons.filter(Pokemon.legendary == legendary)

    pokemons = pokemons.order_by(getattr(getattr(Pokemon, sort), order)())
    pokemons = pokemons.paginate(page=page_num, per_page=limit, error_out=False)
    allpokemon = pokemons.items

    return {
        "success": True,
        "pokemons": allpokemon,
        "timestamp": now,
        "currentPage": pokemons.page,
        "totalPages": pokemons.pages,
        "totalCount": pokemons.total,
        "message": "Pokemon retrieved successfully.",
    }


@pokemonapi.route("/pokemon/", methods=["POST"])
def bulk_insert_pokemon():
    pokemon_data = request.get_json()
    try:
        pokemon_records = []
        for data in pokemon_data:
            pokemon_records.append(
                {
                    "id": data.get("id"),
                    "name": data.get("name").capitalize(),
                    "type1": data.get("type1").capitalize(),
                    "type2": data.get("type2").capitalize(),
                    "total": data.get("total"),
                    "hp": data.get("hp"),
                    "attack": data.get("attack"),
                    "defense": data.get("defense"),
                    "sp_atk": data.get("sp_atk"),
                    "sp_def": data.get("sp_def"),
                    "speed": data.get("speed"),
                    "generation": data.get("generation"),
                    "legendary": data.get("legendary"),
                }
            )

        statement = insert(Pokemon).values(pokemon_records)
        statement = statement.on_conflict_do_nothing()
        db.session.execute(statement)
        db.session.commit()
        return jsonify(
            {"success": True, "message": f"{len(pokemon_records)} records Inserted"}
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@pokemonapi.route("/pokemon/", methods=["PUT"])
def upsert_pokemon():
    pokemon_data = request.get_json()
    try:
        for record in pokemon_data:
            if "name" in record:
                record["name"] = record["name"].capitalize()
            if "type1" in record and record["type1"] is not None:
                record["type1"] = record["type1"].capitalize()
            if "type2" in record and record["type2"] is not None:
                record["type2"] = record["type2"].capitalize()

        save = insert(Pokemon).values(pokemon_data)
        update = save.on_conflict_do_update(
            constraint="pokemon_pkey", set_=save.excluded
        )

        db.session.execute(update)
        db.session.commit()

        return jsonify(
            {"success": True, "message": f"{len(pokemon_data)} records Updated"}
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


"""{
        'id': save.excluded.id,
        'type1':save.excluded.type1,
        'type2':save.excluded.type2,
        'total':save.excluded.total,
        'hp':save.excluded.hp,
        'attack':save.excluded.attack,
        'defense':save.excluded.defense,
        'sp_atk':save.excluded.sp_atk,
        'sp_def':save.excluded.sp_def,
        'speed':save.excluded.speed,
        'generation':save.excluded.generation,
        'legendary':save.excluded.legendary,
        }
    
@pokeman_api.route("/", methods=["PUT"])
def upsert():
    pokemon_datas = request.json.get
    values = []
    for pokemon_data in pokemon_datas:
        pokemon_values = {
            'name': pokemon_data.get('name'),
            'rank': pokemon_data.get('rank'),
            'type1': pokemon_data.get('type1'),
            'type2': pokemon_data.get('type2'),
            'total': pokemon_data.get('total'),
            'hp': pokemon_data.get('hp'),
            'attack': pokemon_data.get('attack'),
            'defense': pokemon_data.get('defense'),
            'sp_atk': pokemon_data.get('sp_atk'),
            'sp_def': pokemon_data.get('sp_def'),
            'speed': pokemon_data.get('speed'),
            'generation': pokemon_data.get('generation'),
            'legendary': pokemon_data.get('legendary')
        }
        values.append(pokemon_values)
    insert_stmt = insert(Pokemon).values(values)
    update_stmt = insert_stmt.on_conflict_do_update(
        index_elements=['name'],
        set_={
            'id': insert_stmt.excluded.id,
            'type1': insert_stmt.excluded.type1,
            'type2': insert_stmt.excluded.type2,
            'total': insert_stmt.excluded.total,
            'hp': insert_stmt.excluded.hp,
            'attack': insert_stmt.excluded.attack,
            'defense': insert_stmt.excluded.defense,
            'sp_atk': insert_stmt.excluded.sp_atk,
            'sp_def': insert_stmt.excluded.sp_def,
            'speed': insert_stmt.excluded.speed,
            'generation': insert_stmt.excluded.generation,
            'legendary': insert_stmt.excluded.legendary
        }
    )
    db.session.execute(update_stmt)
    db.session.commit()
    return {
            "success": True,
            "message": "Pokemon updated successfully"
        }, 200"""


@pokemonapi.route("/pokemon/", methods=["DELETE"])
def delete_pokemon():
    deletePokemon = request.json
    names_to_delete = [name.capitalize() for name in deletePokemon]
    pokemons = Pokemon.query.filter(Pokemon.name.in_(names_to_delete)).delete()

    if not pokemons:
        raise PokemonException(f"Pokemon not found {deletePokemon}")
    db.session.commit()
    return jsonify(
        {"success": True, "message": f"{len(names_to_delete)} records Deleted"}
    )


@pokemonapi.route("/allpokemon/", methods=["DELETE"])
def delete_all_pokemon():
    delete_all = delete(Pokemon)
    db.session.execute(delete_all)
    db.session.commit()

    return jsonify({"success": True, "message": "All records deleted"})
