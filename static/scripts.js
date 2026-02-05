async function updateState() {
    let res = await fetch(state_url);
    let gamestate = await res.json();

    res = await fetch(env_template_url);
    const environment_template = await res.text();

    res = await fetch(party_template_url);
    const party_template = await res.text();

    gamestate.forEach((data, idx) => {
        
        let index = idx+1;

        let $environment = $(environment_template);

        let env_key = `env_${index}`;
        $environment.attr("id", env_key);

        let partySize = data.party_count;

        $environment.find("#trainer").html(`Environment ${index}: ${data.player_name}`);
        $environment.find("#trainer-party").html(`Party: ${partySize}/6`);

        $environment.find("#current_reward").html(`Current Reward: ${data.total_reward}`);

        Object.keys(data.events).forEach(key => {
            let $milestone = $environment.find(`#${key}`);
            if ($milestone) {
                if (data.events[key] == true) {
                    $milestone.addClass("complete");
                } else {
                    $milestone.removeClass("complete");
                }
            }
        });

        if (partySize == 0)
        {
            $environment.find("#party").append("<p>No pokemon in Party</p>");
        }
        else 
        {
            for (let i = 0; i < partySize; i++) {
                let $pokemonDiv = $(party_template);
                if ($pokemonDiv)
                {
                    if (i < partySize) {
                        let pokemon = data.pokemon[i];
                        $pokemonDiv.find(".image").attr("src",`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${pokemon.species.id}.png`);
                        $pokemonDiv.find(".image").attr("alt",`Image of ${pokemon.species.name}`);
                        $pokemonDiv.find(".name").html(pokemon.name);
                        $pokemonDiv.find(".species").html(pokemon.species.name);
                        $pokemonDiv.find(".level").html(`Lvl: ${pokemon.level}`);
                        $pokemonDiv.find(".hp").html(`HP: ${pokemon.hp}/${pokemon.max_hp}`);
                        $pokemonDiv.find(".exp").html(`Exp: ${pokemon.exp}/${pokemon.next_level_exp}`);
                        for (let j = 0; j < 4; j++) {
                            let $moveDiv = $pokemonDiv.find(`.move-${j+1}`);
                            if (pokemon.moves[j].move.id > 0) {                    
                                $moveDiv.html(`${pokemon.moves[j].move.name} (PP: ${pokemon.moves[j].pp})`);
                                $moveDiv.removeClass("hidden");
                            } else {
                                $moveDiv.addClass("hidden");
                            }
                        }
                        $pokemonDiv.removeClass("hidden");
                    } else {
                        $pokemonDiv.addClass("hidden");
                    }
                }
                $environment.find("#party").append($pokemonDiv);
            }
        }

        let $env = $(`#${env_key}`);
        if ($env.length > 0) {
            $env.replaceWith($environment);
        } else {
            $("#app").append($environment);   
        } 
    });

    document.getElementById("status").innerText = JSON.stringify(gamestate, null, 2);
}

setInterval(updateState, 5000);