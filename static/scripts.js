var envPositions = [];

async function updateState() {
    let res = await fetch(state_url);
    let gamestate = await res.json();

    res = await fetch(env_template_url);
    const environment_template = await res.text();

    res = await fetch(party_template_url);
    const party_template = await res.text();

    $(".environments-banner").html(`Environments (${gamestate.length})`);

    gamestate.forEach((data, idx) => {

        let index = idx + 1;

        let env_key = `env-${index}`;
        let $environment = $(`#${env_key}`);
        if ($environment.length === 0) {
            $environment = $(environment_template.replaceAll('env-0', env_key));
            $environment.attr("id", env_key);
            $environment.attr("data-index", idx);
            $("#app").append($environment);
        }

        let partySize = data.party_count;

        if (data.in_battle) {
            $environment.removeClass("bg-primary-subtle");
            $environment.removeClass("bg-warning-subtle");
            $environment.addClass("bg-danger-subtle");

            $environment.removeClass("border-primary");
            $environment.removeClass("border-warning");
            $environment.addClass("border-danger");
        } else if (data.in_dialog) {
            $environment.removeClass("bg-primary-subtle");
            $environment.removeClass("bg-danger-subtle");
            $environment.addClass("bg-warning-subtle");

            $environment.removeClass("border-primary");
            $environment.removeClass("border-danger");
            $environment.addClass("border-warning");
        } else {
            $environment.removeClass("bg-danger-subtle");
            $environment.removeClass("bg-warning-subtle");
            $environment.addClass("bg-primary-subtle");

            $environment.removeClass("border-danger");
            $environment.removeClass("border-warning");
            $environment.addClass("border-primary");
        }

        $environment.find(".location").html(`${data.map_name}: ${data.x},${data.y}`);

        $environment.find(".trainer").html(`Environment ${index}: ${data.player_name}`);
        $environment.find(".trainer-party").html(`Party: ${partySize}/6`);

        $environment.attr("data-score", data.total_reward);
        $environment.find(".current-reward").html(`Current Reward: ${data.total_reward}`);

        let completed = 0;
        Object.keys(data.events).forEach(key => {
            let $milestone = $environment.find(`#${key}`);
            if ($milestone) {
                if (data.events[key] == true) {
                    $milestone.addClass("text-decoration-line-through");
                    completed++;
                } else {
                    $milestone.removeClass("text-decoration-line-through");
                }
            }
        });
        $environment.find(".objectives-count").html(`Completed Objectives: ${completed}`);

        for (let i = 0; i < 6; i++) {
            let slot_key = `env-${index}-slot-${i}`;
            let $pokemonDiv = $(`#${slot_key}`);
            if ($pokemonDiv.length === 0) {
                $pokemonDiv = $(party_template.replaceAll("env-0-slot-0", slot_key));
                $environment.find(".party").append($pokemonDiv);
            }
            if (i < partySize) {
                let pokemon = data.pokemon[i];
                $pokemonDiv.find(".image").attr("src", `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${pokemon.species.id}.png`);
                $pokemonDiv.find(".image").attr("alt", `Image of ${pokemon.species.name}`);
                $pokemonDiv.find(".name").html(pokemon.name);
                $pokemonDiv.find(".species").html(pokemon.species.name);
                $pokemonDiv.find(".level").html(`Lvl: ${pokemon.level}`);
                $pokemonDiv.find(".hp").html(`HP: ${pokemon.hp}/${pokemon.max_hp}`);
                $pokemonDiv.find(".exp").html(`Exp: ${pokemon.exp}/${pokemon.next_level_exp}`);
                for (let j = 0; j < 4; j++) {
                    let $moveDiv = $pokemonDiv.find(`.move-${j + 1}`);
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
    });

    reorderEnvironments();

    document.getElementById("status").innerText = JSON.stringify(gamestate, null, 2);
}

function reorderEnvironments() {
    let environments = Array.from(document.querySelectorAll('.environment'));

    if (envPositions.length == 0) {
        environments.forEach((environment, idx) => {
            envPositions[idx] = environment.getBoundingClientRect();
        });
    }

    // 2. SORT – reorder DOM
    environments.sort((a, b) => {
        return parseFloat(b.dataset.score) - parseFloat(a.dataset.score)
    });

    // 3. LAST – record new positions & invert
    environments.forEach((environment, idx) => {
        
        let origIdx = environment.dataset.index;
        const originalPositioon = envPositions[origIdx];        
        const newPosition = envPositions[idx];

        //console.log(`Environment: ${environment.getAttribute("id")}   Reward: ${environment.dataset.score}    LEFT: ${originalPositioon.left} -> ${newPosition.left}    TOP: ${originalPositioon.top} -> ${newPosition.top}`);

        const dx = newPosition.left - originalPositioon.left;
        const dy = newPosition.top - originalPositioon.top;

        // Invert
        environment.style.transform = `translate(${dx}px, ${dy}px)`;
    });
}

async function toggleQuit() {
    let res = await fetch(quit_toggle_url);
    if (res.ok) {
        let $quitbutton = $("#quit-button");
        let $image = $quitbutton.find("i");

        //Get value
        var data = await res.json();
        var quitting = data.quitting;

        if (quitting) {
            // Set check to toggle
            $quitbutton.removeClass("btn-danger");
            $quitbutton.addClass("btn-success");

            $image.removeClass('bi-x-lg');
            $image.addClass('bi-check-lg');
        } else {
            // Set x to toggle
            $quitbutton.removeClass("btn-success");
            $quitbutton.addClass("btn-danger");

            $image.removeClass('bi-check-lg');
            $image.addClass('bi-x-lg');
        }
        $("#quit-button").attr("data-quitting", quitting);
    }
}

updateState();
setInterval(updateState, 5000);