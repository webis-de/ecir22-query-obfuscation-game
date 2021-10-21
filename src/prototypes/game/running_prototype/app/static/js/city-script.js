var game_started = false;
var selected_level = "";
var play_intro = introduction;


$("#blue_level").on("click", function(e) {
    playSquidLevel();
});


/*
Change the colors of the city outline according to the level and change the
displayed donut charts according to the data
*/
function playSquidLevel() {
    set_game_data_to_default();
    game_started = true;
    selected_level = "squid";
    let root = document.documentElement;
    root.style.setProperty("--mode_color", "#03B7DF");
    root.style.setProperty("--polygon_stroke", "#03B7DF");
    for (key in played_games_data) {
        d3.select("#" + key + "_donut").selectAll("*").remove();
    }
    draw_donut_charts(selected_level);
}


$("#red_level").on("click", function(e) {
    set_game_data_to_default();
    game_started = true;
    selected_level = "chameleon";
    let root = document.documentElement;
    root.style.setProperty("--mode_color", "#ff00ff");
    root.style.setProperty("--polygon_stroke", "#ff00ff");
    for (key in played_games_data) {
        d3.select("#" + key + "_donut").selectAll("*").remove();
    }
    draw_donut_charts(selected_level);
});


//Set the points and played game rounds back to zero for the next game
function set_game_data_to_default() {
    $.ajax({
        url: url_prefix + '/reset',
        data: {},
        contentType: 'application/json;charset=UTF-8',
        type: 'GET'
    });
}


// Hover effect for the polygons
$(".district").on("mouseover", function(e) {
    if (game_started == true) {
        this.style.cursor = "pointer";
        classes = this.classList;
        selected_category = classes[classes.length - 1];
        city_elements = $(".district");
        for (i = 0; i < city_elements.length; i ++) {
            element_classes = city_elements[i].classList;
            if (element_classes[element_classes.length - 1] != selected_category) {
                city_elements[i].style.opacity = "0.6";
                city_elements[i].style.strokeWidth = "1px";
            }
            if (element_classes[element_classes.length - 1] == selected_category) {
                city_elements[i].style.opacity = "1.0";
            }
            if (city_elements[i].nodeName == "polygon" && element_classes[element_classes.length - 1] == selected_category) {
                city_elements[i].style.strokeWidth = "4px";
            }
        }
        this.style.opacity = "1.0";
    }
});


$("polygon").on("mouseout", function(e) {
    if (game_started == true) {
        all_polygons = $("polygon");
        for (i = 0; i < all_polygons.length; i++) {
            all_polygons[i].style.strokeWidth = "1px";
            all_polygons[i].style.opacity = "1.0";
        }

        city_elements = $(".district");
        for (i = 0; i < city_elements.length; i ++) {
            city_elements[i].style.opacity = "1.0";
        }
    }
});


// Starts a game round when user clicks on a district of the city
$(".district").on( "click", function(e) {
    //add to data on which category the user clicked
    if (game_started == true) {
        var classes = this.classList;
        if (classes.length >= 2) {
          var selected_category = classes[classes.length - 1];
        }
        data = JSON.stringify({selectedCategory: selected_category, round: 0, totalPoints: 0, selectedLevel: selected_level});
        startNewGame(data);
    }
});


function startNewGame(sendData) {
       $.ajax({
            url: url_prefix + '/game',
            data: sendData,
            contentType: 'application/json;charset=UTF-8',
            type: 'POST',
            success: function(response) {
                selected_category = response['category'];
                random_query = response['query'];
                level = response['level'];
                //console.log(level)
                window.location.href = url_prefix + '/game/' + selected_category + '/' + level + '/?query=' + random_query;
            },
            error: function(error) {
                console.log(error);
            }
            });
}


$('#menu_icon').on('click', function() {
    document.getElementById('close_menu').style.display = "inline";
    document.getElementById('menu_overlay').style.display = "block";
    document.getElementById('game_name_container').style.filter = "blur(10px)";
    document.getElementById('game_name_container').style.pointerEvents = "none";
    document.getElementById('city_container').style.filter = "blur(10px)";
    document.getElementById('city_container').style.pointerEvents = "none";
    document.getElementById('level_selection_container').style.filter = "blur(10px)";
    document.getElementById('level_selection_container').style.pointerEvents = "none";
});

function closeMenu() {
    document.getElementById('close_menu').style.display = "none";
    document.getElementById('menu_overlay').style.display = "none";
    document.getElementById('game_name_container').style.filter = "";
    document.getElementById('game_name_container').style.pointerEvents = "auto";
    document.getElementById('city_container').style.filter = "";
    document.getElementById('city_container').style.pointerEvents = "auto";
    document.getElementById('level_selection_container').style.filter = "";
    document.getElementById('level_selection_container').style.pointerEvents = "auto";
}


$('#close_menu').on('click', function() {
    closeMenu();
});

function playSecondLevelIntro() {
    var intro = introJs();
    intro.setOptions({
        overlayOpacity: 0.8,
        exitOnOverlayClick: false,
        steps: [
        {
            element: '#level_selection_container',
            intro: "Congrats, you finished 5 queries!!! <br> Now you can play in a second mode. The level 'Squid' is the level you played the whole time. <br>" +
                    "The new level 'Chameleon' is mostly the same except that you receive a point deduction if you use any of the help-words. " +
                    "The higher the word is in the list, the more points you will loose." +
                    "Therefore, you have to be even more creative. <br> Good luck!",
        }
        ]
    });
    intro.start().oncomplete(function() {
        updateIntro();
    });
}

function updateIntro() {
    $.ajax({
        url: url_prefix + '/updateIntro',
        contentType: 'application/json;charset=UTF-8',
        type: 'POST'
    });
}


function displaySecondLevel() {
    if (second_level == true) {
        document.getElementById('level_selection_container').style.display = "inline-block";
    } else {
        playSquidLevel();
    }

    if (level_introduction === true) {
        playSecondLevelIntro();
    }
}


$("#help").on("click", function(e) {
    sendData = JSON.stringify({"intro": true});
    $.ajax({
        url: url_prefix + '/changeIntroData',
        data: sendData,
        contentType: 'application/json;charset=UTF-8',
        type: 'POST',
        success: function(response) {
            play_intro = true;
            closeMenu();
            playIntro();
        }
    });
});


function playIntro() {
    if (play_intro === true) {
        var intro = introJs();
        intro.setOptions({
            overlayOpacity: 0.8,
            exitOnOverlayClick: false,
            steps: [
            {
                element: '#introoverlay',
                intro: "This is the city we are living in. <br> The districts represent different categories of search queries. <br> To start a game, just click on one of them. "
            }
            ]
        });
        intro.start().oncomplete(function() {
            data = JSON.stringify({selectedCategory: "crime", round: 0, totalPoints: 0, selectedLevel: "squid"});
            startNewGame(data);
        });
    }
}

displaySecondLevel();
playIntro();



