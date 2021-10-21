var used_forbidden_word = false;
var is_full_screen = false;
var highscore = 0;
var help = introduction;
var keyword_points = 0;

$('#menu_icon').on('click', function() {
    document.getElementById('menu_overlay').style.display = "block";
    document.getElementById('close_menu').style.display = "block";
    document.getElementById('menu_icon').style.display= "none";
    background_style("10px", "0.8");
});


$('#close_menu').on('click', function() {
    closeMenu();
});


$(".full_screen").on('click', function(e) {
    is_full_screen = true;
    document.getElementById("website_overlay").style.display = "block";
});


$(".full_screen").on('mouseover', function(e) {
    if (is_full_screen == true) {
        $(".full_screen")[0].style.cursor = "not-allowed";
        $(".full_screen")[1].style.cursor = "not-allowed";
    } else {
        $(".full_screen")[0].style.cursor = "pointer";
        $(".full_screen")[1].style.cursor = "pointer";
    }

});


$(".small_screen").on('click', function(e) {
    is_full_screen = false;
    document.getElementById("website_overlay").style.display = "none";
});


$(".small_screen").on('mouseover', function(e) {
    if (is_full_screen == false) {
        $(".small_screen")[0].style.cursor = "not-allowed";
        $(".small_screen")[1].style.cursor = "not-allowed";
    } else {
        $(".small_screen")[0].style.cursor = "pointer";
        $(".small_screen")[1].style.cursor = "pointer";
    }

});


/* Code for submitting query to server */
$("#search_form").on('keypress',function (e) {
   if (e.keyCode == 13) {
        $(".box")[0].style.display = "none";
        startSearch();
   }
});


$('#search_icon_container').on('click', function (e) {
    $(".box")[0].style.display = "none";
    startSearch();
});


$("#exit_game").on('click',function (e) {
    window.location.href = url_prefix + '/city';
});


function startSearch() {
    data = $("#search_form").val();
    var list_of_used_forbidden_words = [];
    var words = data.split(" ");
    // maybe add here if search is part of forbidden words than forbid it
    for (var i = 0; i < words.length; i++) {
            for (var j = 0; j < forbidden_words.length; j++) {
                if (words[i] == forbidden_words[j]) {
                    used_forbidden_word = true;
                    list_of_used_forbidden_words.push(words[i]);
                }
            }
    }
    if (list_of_used_forbidden_words.length > 2) {
        words = list_of_used_forbidden_words.slice(0, 2);
        words.push("...");
    } else {
        words = list_of_used_forbidden_words;
    }

   if (used_forbidden_word == false) {
        if (level == "chameleon") {
            keyword_points = computeKeywordPoints(data.split(" "));
        }
        data = JSON.stringify({searchQuery: data, originalQuery: query, queryCategory: category, selectedLevel: level});
        searchCall(data);
   } else {
        //Here add functionality if forbidden word was used
        $('.box')[0].style.display = "block";
        document.getElementById("alert_content").innerHTML = "Please reword your query. <br>" +
                                                                "Used forbidden words: " + words;
   }
   used_forbidden_word = false;
}

function computeKeywordPoints(query) {
    var list = document.getElementById("keywords_list").children;
    var points_used_keywords = 0;
    for (var i = 0; i < query.length; i++) {
        for (var j = 0; j < 10; j++) {
            if (query[i] == list[j].innerHTML) {
                points_used_keywords = points_used_keywords + (10 - j);
            }
        }
    }
    return (-10 * points_used_keywords);
}

function closeMenu() {
    document.getElementById('menu_overlay').style.display = "none";
    document.getElementById('close_menu').style.display = "none";
    background_style("", "1.0");
    document.getElementById('menu_icon').style.display= "block";
    document.getElementById('menu_icon').style.zIndex = "3";
}


function loadDynamicHTML() {
    //Sets the link to the pdf document
    document.getElementById('website_pdf').src = url_prefix + "/static/data/pdf_files/" + file_name + "#toolbar=1&navpanes=0&scrollbar=0";
    document.getElementById('zoomed_website_pdf').src = url_prefix + "/static/data/pdf_files/" + file_name + "#toolbar=1&navpanes=0&scrollbar=0";

    //Sets the colors for the selected level
    if (level == "chameleon") {
        let root = document.documentElement;
        root.style.setProperty("--main_mode_color", "#ff00ff");
        root.style.setProperty("--next_round", "#ffe6ff");
        root.style.setProperty("--progress_bar_list", "#ffe6ff");
        root.style.setProperty("--total_points", "#660066");
    }

    //Sets the point inside the total points display
    document.getElementById('total_points_game').innerHTML = points;

    //Takes care of the outlook of the progress bar
    progress_bar_list = document.getElementById('progress_bar');
    for (i=0; i < 120; i++){
        var node = document.createElement("LI");
        progress_bar_list.appendChild(node);
    }

    percentage = (parseFloat(game_round) / 5.0) * 100.0;
    document.getElementById('progress_percentage').innerHTML = percentage + "&#37;";

    var listItems = document.querySelectorAll('#progress_bar li');
    var stop_progress = 24 * parseInt(game_round);

    //Turns the part that is already done blue or red according to the selected level
    for (var i = 0; i < stop_progress - 24; i++) {
        if (level == "chameleon") {
            listItems[i].style.background = "linear-gradient(to right, #ff00ff 0%, #ff00ff 100%)";
        } else {
            listItems[i].style.background = "linear-gradient(to right, #03B7DF 0%, #03B7DF 100%)";
        }
    }

    //Animates the stripes that are turning blue
    var start = stop_progress - 24;
    var counter = 0;

    for (let j = start; j < start + 24; j++) {
        counter = counter + 1;
        delay_animation_progress_bar(j, listItems, counter);
    }

    //Takes care of the headline and the icon of the category in the game
    category_icon = document.getElementById('category_icon');
    category_headline = document.getElementById('category_header');
    category_headline.innerHTML = capitalizeFirstLetter(category);

    if (category == 'health') {
        category_icon.innerHTML = '<i class="fas fa-heartbeat category_icon"></i>';
    }
    if (category == 'personal') {
        category_icon.innerHTML = '<i class="fas fa-user-secret category_icon"></i>';
    }
    if (category == 'crime') {
        category_icon.innerHTML = '<i class="fas fa-bomb category_icon"></i>';
    }
    if (category == 'knowledge') {
        category_icon.innerHTML = '<i class="fas fa-book-open category_icon"></i>';
    }
    if (category == 'politics') {
        category_icon.innerHTML = '<i class="fas fa-landmark category_icon"></i>';
    }
    if (category == 'law') {
        category_icon.innerHTML = '<i class="fas fa-balance-scale category_icon"></i>';
    }

}

function delay_animation_progress_bar(j, listItems, counter) {
    setTimeout(function() {
        listItems[j].className = "progress";
    }, 30 * counter);
}


function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}


function searchCall(sendData) {
    document.getElementsByClassName('lds-ripple')[0].style.display = "inline-block";
    background_style("3px", "0.9");
    $.ajax({
        url: url_prefix + '/search',
        data: sendData,
        contentType: 'application/json;charset=UTF-8',
        type: 'POST',
        success: function(response) {
            document.getElementsByClassName('lds-ripple')[0].style.display = "none";
            background_style("", "1.0");
            searchFeedback(response);
        },
        error: function(error) {
            console.log(error);
        }
        });

    }

function searchFeedback(responseData) {
    var found_document = responseData['found_document'];

    if (found_document == false) {
        $('.box')[0].style.display = "block";
        document.getElementById("alert_content").innerHTML = "Sorry, the wanted document was not found. <br> Please try a different query.";
    }
    else {
        if (highscore >= responseData['total_points_round']) {
            $('.box')[0].style.display = "block";
            document.getElementById("alert_content").innerHTML = "This query is not worth more points <br> than you scored before.";
        } else {
            //if the level is chameleon then display the points for the used keywords
            if (level == "chameleon") {
                var chameleon_points = document.getElementsByClassName("chameleon_points");
                chameleon_points[0].style.display = "inline-block";
                chameleon_points[1].style.display = "block";
            }

            //Blur the background to show overlay for the display of the points for each round
            document.getElementById('points_overlay').style.display = "block";
            background_style("80px", "0.4");
            if (game_round == 5) {
                document.getElementById('next_button_text').innerHTML = "Exit";
                document.getElementById('continue_icon').innerHTML = "<i class='fas fa-sign-out-alt'></i>";
            }
            //Display the computed points and animate them as a counter
            var pt = parseInt(responseData['total_points_round']) + keyword_points;
            var points_dict = {'document_position': responseData['document_position'], 'number_related_documents': responseData['number_related_documents'],
            'average_position_related_documents': responseData['average_position_related_documents'],
             'query_length': responseData['query_length'], 'total_points_round': pt,
             'keywords_usage': keyword_points};

            //Animate the display of the total points
            update_users_count(points_dict);
            points_data = parseInt(points) + pt;
            document.getElementById('final_total_points').innerHTML = points;
            setTimeout(show_total_points, 1000, points_data);
            setTimeout(function() {$('#final_total_points_display').addClass('shadow-pulse'); }, 1600);
            setTimeout(function() {$('#continue_game').addClass('next'); $('#retry').addClass('next');}, 2200);

            //Set new highscore
            highscore = responseData['total_points_round'];
        }
    }
}

function background_style(blur_factor, opacity_factor) {
    document.getElementById('header').style.opacity = opacity_factor;
    document.getElementById('header').style.filter = "blur(" + blur_factor + ")";
    document.getElementById('gaming_container').style.opacity = opacity_factor;
    document.getElementById('gaming_container').style.filter = "blur(" + blur_factor + ")";
    document.getElementById('footer').style.opacity = opacity_factor;
    document.getElementById('footer').style.filter = "blur(" + blur_factor + ")";

}


function show_total_points(points_data) {
        data = {'final_total_points': points_data};
        update_users_count(data);
}


// Animation of increasing value for points
function update_users_count(points_dict) {
    $.each(points_dict, function( k, v ) {
        $('#' + k).animate({
            counter: v
        }, {
            duration: 600,
            easing: 'swing',
            step: function(now) {
                $(this).text(Math.ceil(now));
            },
            complete: update_users_count()
        });
    });
}


$('#retry').on('click', function() {
    // Make the pointsdisplay invisible again
    document.getElementById('points_overlay').style.display = "none";
    background_style("", "1.0");

    //Change innerhtml of skip query button
    $('#next_round').removeClass('skip');
    document.getElementById('next_round').style.background = "linear-gradient(to right, var(--main_mode_color) 50%, var(--main_mode_color) 50%)";
    document.getElementById('next_round').style.padding = "10px 30px 10px 30px !important";
    document.getElementById('next_round').innerHTML = "Take " + highscore + " points";
    document.getElementById('next_round').disabled = false;

    current_points = parseInt(points) + highscore;
    document.getElementById('total_points_game').innerHTML = current_points;
});


$("#continue_game").on('click',function (e) {
    points_round = parseInt(document.getElementById('total_points_round').innerHTML);
    accumulated_points = parseInt(points) + points_round;
    //update the total points in the db for the user
    update_points_data(points_round);
    start_next_game_round();
});


function update_points_data(points_round){
    sendData = JSON.stringify({accumulatedPoints: points_round, currentLevel: level, currentCategory: category,
                            originalQuery: query});
    $.ajax({
        url: url_prefix + '/updatePoints',
        data: sendData,
        contentType: 'application/json;charset=UTF-8',
        type: 'POST'
    });
}


function start_next_game_round() {
    //If the round is number five the game is now finished and we go back to the city
    if (game_round == 5) {
        window.location.href = url_prefix + '/city';
    } else {
        sendData = JSON.stringify({selectedCategory: category, selectedLevel: level});
       $.ajax({
        url: url_prefix + '/game',
        data: sendData,
        contentType: 'application/json;charset=UTF-8',
        type: 'POST',
        success: function(responseData) {
            random_query = responseData['query'];
            window.location.href = url_prefix + '/game/' + category + '/' + level + '/?query=' + random_query;
        },
        error: function(error) {
            console.log(error);
        }
        });
    }
}


$("#next_round").on('click',function (e) {
    update_points_data(highscore);
    start_next_game_round(points);
});

function computeTransformationProgressBar() {
	listItems = document.querySelectorAll('#progress_bar li');
	for (i=0; i < listItems.length; i++) {
	    var x = 15 + 14*(i + 1);
	    x = String(x) + "px";
	    var Progresstransformation = "translate(" + x + ", 0px) skew(-35deg)";
	    listItems[i].style.transform = Progresstransformation;
    }
}


function changeIntroInDB() {
    sendData = JSON.stringify({"intro": false});
    $.ajax({
        url: url_prefix + '/changeIntroData',
        data: sendData,
        contentType: 'application/json;charset=UTF-8',
        type: 'POST'
    });
}

function changedOutlook() {
    document.getElementById('intro_text').innerHTML = "The task: <br>You are supposed to retrieve a specific website with a search engine. <br>This search engine has access to the web of our time but to protect it's users <br>it only allows queries that obfuscate their private information need. <br>Your task now is to help users to obfuscate the original search query that belongs to the wanted website. <br>For that, you are shown the website, the original search query, and a list of auxiliary words. <br> Note that you can use any words or phrases for the task, except the ones that make up the original query.";
    document.getElementById('icon_container').innerHTML = "<i id='next_icon' class='far fa-arrow-alt-circle-right continue'></i>";
    document.getElementById('intro_overlay').style.display = "block";
    document.getElementById('header').style.opacity = 0.2;
    document.getElementById('gaming_container').style.opacity = 0.2;
    document.getElementById('footer').style.opacity = 0.2;
    document.getElementById('menu_icon').style.opacity = 0.2;
    $('#header').css('pointer-events', 'none');
    $('#gaming_container').css('pointer-events', 'none');
    $('#footer').css('pointer-events', 'none');
    $('#menu_icon').css('pointer-events', 'none');
}

function introOverlay(input) {
    if (input === true) {
        changedOutlook();
    }
}

function displayEndMessage() {
    console.log("Hello from display message");
    changedOutlook();
    document.getElementById('intro_text').innerHTML = "Now you know how everything works.<br> If you ever need help to remember the rules, have a look at the menu.<br> You can find it in the upper left corner.";
    if (introduction === true) {
        document.getElementById('icon_container').innerHTML = "<span id='end' class='closure'>Start Game <span><i id='play_icon' class='fas fa-play continue'></i></span></span>";
    } else {
        document.getElementById('icon_container').innerHTML = "<span id='continue_normal' class='closure'>Continue<span><i id='play_icon' class='fas fa-play continue'></i></span></span>";
    }
}

function playIntro(input) {
        //document.getElementById('search_form').placeholder = "soldiers vehicle borrowing advantages";
        var intro = introJs();
        intro.setOptions({
            overlayOpacity: 0.8,
            exitOnOverlayClick: false,
            steps: [
            {
                element: '#website',
                intro: "This is a website that you are supposed to find.",
                position: 'right'
            },
            {
                element: '#query',
                intro: "This is the original search query you are supposed to obfuscate. <br> Remember, you can't use any of those words for your own search query!",
                position: 'left'
            },
            {
                element: '#keywords_list',
                intro: "Here is a list of words that may help you.",
                position: 'left'
            },
            {
                element: '#search_input',
                intro: "Finally, this is the place where you enter your obfuscated search queries.",
                position: 'top'
            },
            {
                element: '#points_overlay',
                intro: "If your query retrieved the wanted documents, you will receive points. Four different factors make up your final score. In total, you can receive max. 500 points.",
                position: 'right'
            },
            {
                element: '#document_pos_intro',
                intro: "First, you will get points for the ranking of the wanted document. The ranking indicates how relevant the website is for your query. This means that the higher the website is ranked by the search engine, the more points you will receive. At most, you can get 200 points.",
                position: 'left'
            },
            {
                element: '#num_related_intro',
                intro: "Here you get points for the number of websites your query retrieved that are related to the original search query. The more websites the search engine finds that would also have been found with the original query, the more points you receive. Here you can get at most 150 points.",
                position: 'left'
            },
            {
                element: '#pos_related_intro',
                intro: "Here you get points for the average ranking position of the related websites that were found. The higher the ranking is of those websites, the more points you will receive. At most, you can get 100 points.",
                position: 'left'
            },
            {
                element: '#length_intro',
                intro: "Finally, you will get points for the length of your query. The fewer words you use the more points you will get. If your query is as long or shorter than the original search query, you get a full score. Otherwise, you receive fewer points. The highest score you can achieve here is 50.",
                position: 'left'
            }
            ]
        });
        intro.onchange(function(element) {
            if(element.id === 'points_overlay') {
                console.log("I was called");
                document.getElementById('points_overlay').style.display = "block";
                background_style("80px", "0.4");
            }
       });
            intro.start().oncomplete(function() {
            document.getElementById('points_overlay').style.display = "none";
            background_style("", "1.0");
            //if (introduction === true) {
                changeIntroInDB();
                displayEndMessage();
            //}
            });
             intro.onexit(function() {
                document.getElementById('points_overlay').style.display = "none";
                background_style("", "1.0");
                //if (introduction === true) {
                    changeIntroInDB();
                    displayEndMessage();
                //}
            });
}

$("body").on("click", "#next_icon", function() {
    console.log("I am click");
    if (help === true) {
        document.getElementById('intro_overlay').style.display = "none";
        document.getElementById('header').style.opacity = 1;
        document.getElementById('gaming_container').style.opacity = 1;
        document.getElementById('footer').style.opacity = 1;
        document.getElementById('menu_icon').style.opacity = 1;
        $('#header').css('pointer-events', 'all');
        $('#gaming_container').css('pointer-events', 'all');
        $('#footer').css('pointer-events', 'all');
        $('#menu_icon').css('pointer-events', 'all');
        playIntro(help);
    }
});


$("body").on("click", "#end", function() {
    window.location.href = url_prefix + "/city";
});

$("body").on("click", "#continue_normal", function() {
            document.getElementById('intro_overlay').style.display = "none";
        document.getElementById('header').style.opacity = 1;
        document.getElementById('gaming_container').style.opacity = 1;
        document.getElementById('footer').style.opacity = 1;
        document.getElementById('menu_icon').style.opacity = 1;
        $('#header').css('pointer-events', 'all');
        $('#gaming_container').css('pointer-events', 'all');
        $('#footer').css('pointer-events', 'all');
        $('#menu_icon').css('pointer-events', 'all');
});

$("#help").on('click', function(e) {
    help = true;
    closeMenu();
    introOverlay(help);
});


loadDynamicHTML();
introOverlay(introduction);
computeTransformationProgressBar();
setTimeout(function() {document.getElementById('next_round').disabled = false;}, 60000);

