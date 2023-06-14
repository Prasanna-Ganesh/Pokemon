from flask import Blueprint, jsonify, request, url_for
from app.models import Pokemon, pokemons_schema
import requests
from datetime import datetime as dt, timezone
from app import db, app
from sqlalchemy.dialects.postgresql import insert


pokemonapi = Blueprint("pokemonapi", __name__, url_prefix="/api/v1")


class PokemonException(Exception):
    def __init__(self, message, code=400):
        self.message = message
        self.code = code


@pokemonapi.errorhandler(PokemonException)
def handle_scheduler_exception(e):
    app.logger.exception(e)
    return {"success": False, "error": e.message}, e.code


@pokemonapi.route("/syncpokemons/")
def fetchpokemon():
    url = "https://coralvanda.github.io/pokemon_data.json"
    response = requests.get(url)
    data = response.json()
    for pokemon in data:
        existing_pokemon = Pokemon.query.filter_by(name=pokemon["Name"]).first()
        if existing_pokemon:
            raise PokemonException(f"Pokemon data already present")
        new_pokemon = Pokemon(
            rank=pokemon["#"],
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


@pokemonapi.route("/pokemons/", methods=["GET"])
@pokemonapi.route("/pokemons/<int:id>/", methods=["GET"])
def get_pokemon(id=None):
    now = dt.now(timezone.utc)
    pokemons = Pokemon.query
    limit = request.args.get("limit", app.config.get("PAGE_LIMIT"), type=int)
    sort = request.args.get("sort", "id")  # Default sorting on Pokemon ID
    order = request.args.get("order", "asc")
    page_num = request.args.get("page", 1, type=int)
    search = request.args.get("search")
    type1 = request.args.get("type1")
    type2 = request.args.get("type2")
    generation = request.args.get("generation", 1, type=int)
    legendary = request.args.get("legendary")

    if id:
        pokemons = Pokemon.query.filter(Pokemon.id == id)

    if search:
        search_query = f"%{search}%"
        pokemons = pokemons.filter(Pokemon.name.ilike(search_query))

    if legendary:
        if legendary.lower() == "true":
            legendary = True
            pokemons = pokemons.filter(Pokemon.legendary == legendary)
        elif legendary.lower() == "false":
            legendary = False
            pokemons = pokemons.filter(Pokemon.legendary == legendary)

    if type1:
        pokemons = pokemons.filter(Pokemon.type1 == type1)

    if type2:
        pokemons = pokemons.filter(Pokemon.type2 == type2)

    if generation:
        pokemons = pokemons.filter(Pokemon.generation == generation)

    if not pokemons:
        raise PokemonException(f"Pokemon not found")

    pokemons = pokemons.order_by(getattr(getattr(Pokemon, sort), order)())
    allpokemons = pokemons.paginate(page=page_num, per_page=limit, error_out=False)

    if allpokemons.has_next:
        next_url = url_for(
            "pokemonapi.get_pokemon", page=allpokemons.next_num, _external=True
        )
    else:
        next_url = None
    return {
        "success": True,
        "pokemons": pokemons_schema.dump(allpokemons.items),
        "timestamp": now,
        "currentPage": allpokemons.page,
        "totalPages": allpokemons.pages,
        "totalCount": allpokemons.total,
        "next_page": next_url,
        "message": "Pokemon retrieved successfully.",
    }, 200


@pokemonapi.route("/pokemons/", methods=["POST"])
def bulk_insert_pokemon():
    pokemon_data = request.get_json()
    try:
        pokemon_records = []
        for data in pokemon_data:
            name = data.get("name").capitalize()
            pokemon_records.append(
                {
                    "rank": data.get("rank"),
                    "name": name,
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

        save = insert(Pokemon).values(pokemon_records)
        save = save.on_conflict_do_nothing()
        db.session.execute(save)
        db.session.commit()
        return (
            jsonify(
                {"success": True, "message": f"{len(pokemon_records)} records Inserted"}
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# @pokemonapi.route("/pokemons/", methods=["PUT"])
# def upsert_pokemon():
#     pokemon_datas = request.get_json()
#     pokemon_list = []

#     for pokemon_data in pokemon_datas:
#         name = pokemon_data.get("name")
#         type1 = pokemon_data.get("type1")
#         type2 = pokemon_data.get("type2")
#         pokemon_values = {
#             "name": name.capitalize(),
#             "rank": pokemon_data.get("rank"),
#             "type1": type1.capitalize(),
#             "type2": type2.capitalize(),
#             "total": pokemon_data.get("total"),
#             "hp": pokemon_data.get("hp"),
#             "attack": pokemon_data.get("attack"),
#             "defense": pokemon_data.get("defense"),
#             "sp_atk": pokemon_data.get("sp_atk"),
#             "sp_def": pokemon_data.get("sp_def"),
#             "speed": pokemon_data.get("speed"),
#             "generation": pokemon_data.get("generation"),
#             "legendary": pokemon_data.get("legendary"),
#         }
#         pokemon_list.append(pokemon_values)
#     try:
#         save = insert(Pokemon).values(pokemon_list)
#         update = save.on_conflict_do_update(
#             index_elements=[Pokemon.name],
#             set_=dict(
#                 rank=save.excluded.rank,
#                 type1=save.excluded.type1,
#                 type2=save.excluded.type2,
#                 total=save.excluded.total,
#                 hp=save.excluded.hp,
#                 attack=save.excluded.attack,
#                 defense=save.excluded.defense,
#                 sp_atk=save.excluded.sp_atk,
#                 sp_def=save.excluded.sp_def,
#                 speed=save.excluded.speed,
#                 generation=save.excluded.generation,
#                 legendary=save.excluded.legendary,
#             ),
#         )

#         db.session.execute(update)
#         db.session.commit()

#         return (
#             jsonify(
#                 {"success": True, "message": f"{len(pokemon_list)} records Updated"}
#             ),
#             200,
#         )
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "error": str(e)}), 500


@pokemonapi.route("/pokemons/<int:id>", methods=["PUT"])
@pokemonapi.route("/pokemons/", methods=["PUT"])
def add_pokemon(id=None):
    pokemon_data = request.get_json()

    if not pokemon_data:
        raise PokemonException("No data found", 404)

    values = []

    if id:
        pokemon = Pokemon.query.filter_by(id=id).first()
        if not pokemon:
            raise PokemonException(f"Pokemon with id {id} doesn't exist.", 404)

        new_item = {column: pokemon_data.get(column) or getattr(pokemon, column) for column in Pokemon.__table__.c.keys()}
        values.append(new_item)
    else:
        for item in pokemon_data:
            existing_pokemon = Pokemon.query.filter_by(name=item.get("name")).first()
            if existing_pokemon:
                new_item = {column: item.get(column) or getattr(existing_pokemon, column) for column in Pokemon.__table__.c.keys() if column != "id"}
            else:
                new_item = {column: item.get(column) for column in Pokemon.__table__.c.keys() if column != "id"}
            values.append(new_item)
    upsert = upsertinsert(values)

    return {"message": upsert}, 201


def upsertinsert(values):
    try:
        for value in values:
            insert_stmt = insert(Pokemon).values(value)
            update = {col.name: col for col in insert_stmt.excluded if col.name != "id"}

            upsert_statement = insert_stmt.on_conflict_do_update(
                index_elements=[Pokemon.name],
                set_=update,
            )

            db.session.execute(upsert_statement)
        db.session.commit()

        return {"success": True, "message": "Records updated."}
    except Exception as e:
        print(f"Error: {e}")

    
@pokemonapi.route("/pokemons/", methods=["DELETE"])
@pokemonapi.route("/pokemons/<int:id>", methods=["DELETE"])
def delete_pokemon(id=None):
    if id:
        pokemon = Pokemon.query.get(id)
        if not pokemon:
            raise PokemonException(f"Pokemon with ID {id} not found")
        db.session.delete(pokemon)
        db.session.commit()
        return jsonify({"success": True, "message": "Record Deleted"})
    deletePokemon = request.json
    names_to_delete = [name.capitalize() for name in deletePokemon]
    pokemons = Pokemon.query.filter(Pokemon.name.in_(names_to_delete)).delete()

    if not pokemons:
        raise PokemonException(f"Pokemon not found {deletePokemon}")
    db.session.commit()
    return (
        jsonify(
            {"success": True, "message": f"{len(names_to_delete)} records Deleted"}
        ),
        200,
    )
