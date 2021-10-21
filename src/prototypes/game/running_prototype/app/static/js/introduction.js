$('#game').on('click', function() {
    changeIntroInDB();
});

$('#play').on('click', function() {
    window.location.href = url_prefix + "/city";
});

$('#introduction').on('click', function() {
    playIntro();
});

$('#next_icon').on('click', function() {
    window.location.href = url_prefix + "/city";
});

function changeIntroInDB() {
    sendData = JSON.stringify({"intro": false});
    $.ajax({
        url: url_prefix + '/changeIntroData',
        data: sendData,
        contentType: 'application/json;charset=UTF-8',
        type: 'POST',
        success: function(responseData) {
            window.location.href = url_prefix + "/city";
        },
        error: function(error) {
            console.log(error);
        }
    });
}

function showIntroOption() {
    if (provide_introduction === false) {
        document.getElementById("introduction").style.display = "none";
        document.getElementById("game").style.display = "none";
        document.getElementById("play").style.display = "inline-block";
    }
}


function playIntro() {
    document.getElementById("header").style.display = "none";
    document.getElementById("button_container").style.display = "none";
    let root = document.documentElement;
    root.style.setProperty("--opacity_setting", "0.5");
    document.getElementById("story_container").style.display = "block";
}

showIntroOption()

