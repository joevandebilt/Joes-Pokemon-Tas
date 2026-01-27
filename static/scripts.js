async function updateState() {
    const res = await fetch(state_url);
    const data = await res.json();

    document.getElementById("status").innerText = JSON.stringify(data, null, 2);

    let partySize = data.party_count;

    document.getElementById("trainer").innerText = data.player_name;
    document.getElementById("trainer-party").innerText = `${data.player_name}'s Party: ${partySize}/6`;

    for (let i = 0; i < 6; i++) {
        let pokemonDiv = document.getElementById(`party-${i+1}`);
        if (pokemonDiv)
        {
            if (i < partySize) {
                let pokemon = data.pokemon[i];
                pokemonDiv.getElementsByClassName("image")[0].src = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${pokemon.species.id}.png`;
                pokemonDiv.getElementsByClassName("image")[0].alt = `Image of ${pokemon.species.name}`;
                pokemonDiv.getElementsByClassName("name")[0].innerText = `${pokemon.name} / ${pokemon.species.name}`;
                pokemonDiv.getElementsByClassName("level")[0].innerText = `Level: ${pokemon.level}`;
                pokemonDiv.getElementsByClassName("hp")[0].innerText = `HP: ${pokemon.hp}/${pokemon.max_hp}`;
                pokemonDiv.getElementsByClassName("exp")[0].innerText = `EXP: ${pokemon.exp}/${pokemon.next_level_exp}`;
                for (let j = 0; j < 4; j++) {
                    let moveDiv = pokemonDiv.getElementsByClassName(`move-${j+1}`)[0];
                    if (pokemon.moves[j].move.id > 0) {                    
                        moveDiv.innerText = `${pokemon.moves[j].move.name} (PP: ${pokemon.moves[j].pp})`;
                        moveDiv.classList.remove("hidden");
                    } else {
                        moveDiv.classList.add("hidden");
                    }
                }
                pokemonDiv.classList.remove("hidden");
            } else {
                pokemonDiv.classList.add("hidden");
            }
        }
    }
}

setInterval(updateState, 5000);