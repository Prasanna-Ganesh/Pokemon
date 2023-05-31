# Pokemon

## Usage

```python
1. Add Pokemon with name as a primary key.
2. Edit Pokemon information.
3. Delete Pokemon.
4. Show Pokemons 
5. Pagination is used in a List of Pokemon

In this application the pokemon data is fetched from a link 'https://coralvanda.github.io/pokemon_data.json' and then added into the database by calling the '/fetchpokemon/' API from the postman.
The routes created are:
  1.GET - http://127.0.0.1:5000/api/pokemon/fetchpokemon - Fetch all the pokemon from the given link and store it in the db
  2.GET - http://127.0.0.1:5000/api/pokemon/pokemons<int:id> - Get all the pokemons or Get the pokemon according to the rank(id)
  3.POST- http://127.0.0.1:5000/api/pokemon/insertpokemon - Insert Bulk pokemons using this url
  4.PUT - http://127.0.0.1:5000/api/pokemon/upsertpokemon - Update Bulk pokemons if the pokemon is in db if it is not in db it will add pokemon to the db
  5.DELETE - http://127.0.0.1:5000/api/pokemon/deletepokemon - Delete multiple pokemons by giving their name in the postman
  4.DELETE - http://127.0.0.1:5000/api/pokemon/deleteallpokemon - Delete all the pokemons present in the db

```


## Contact me

```
Email: prasanna.ganesh@annalect.com
```


## License
**Made by Prasanna Ganesh**


## Thanks for visiting
**Please help me to improve the project further and PFA**
