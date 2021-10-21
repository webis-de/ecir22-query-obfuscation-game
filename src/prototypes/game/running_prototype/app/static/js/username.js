$('#user_input').on('click', function() {
    document.getElementById('username_form').focus();
    document.getElementById('username_form').style.boxShadow = "0px 0px 15px 0px #99ffcc";
});


$('#submit_button').on('click', function() {
    document.getElementById('notification').style.display = "none";
    document.getElementById('submit_button').style.margin = "80px 0px 0px 0px";
    document.getElementById('taken_error').style.display = "none";
    document.getElementById('length_error').style.display = "none";
    document.getElementById('empty_error').style.display = "none";
    updateUsername();
});


function updateUsername() {
    name = $("#username_form").val();
    if (name.length == 0) {
        document.getElementById('empty_error').style.display = "block";
        var el = document.getElementById('user_input');
        el.classList.remove('standard');
        el.classList.add('fix');
    }
    else if (name.length <= 23) {
        data = JSON.stringify({newName: name});
        $.ajax({
            url: url_prefix + '/changeUsername',
            data: data,
            contentType: 'application/json;charset=UTF-8',
            type: 'POST',
            success: function(response) {
                var el = document.getElementById('user_input');
                el.classList.remove('standard');
                el.classList.add('fix');
                document.getElementById('username_form').value = "";
                if (response['success'] == false) {
                    document.getElementById('taken_error').style.display = "block";
                }
                else {
                    document.getElementById('notification').style.display = "block";
                    document.getElementById('submit_button').style.margin = "55px 0px 0px 0px";
                    personalize_greetings(name);
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    } else {
        document.getElementById('length_error').style.display = "block";
    }
}

function personalize_greetings(name) {
    document.getElementById('header').innerHTML ="<p>Welcome " + name + "</p>";
}

$('#menu_icon').on('click', function() {
    document.getElementById('menu_overlay').style.display = "block";
    document.getElementById('close_menu').style.display = "block";
    document.getElementById('menu_icon').style.display= "none";
    background_style("10px", "0.8");
});


$('#close_menu').on('click', function() {
    document.getElementById('menu_overlay').style.display = "none";
    document.getElementById('close_menu').style.display = "none";
    background_style("", "1.0");
    document.getElementById('menu_icon').style.display= "block";
    document.getElementById('menu_icon').style.zIndex = "3";
});

function background_style(blur_factor, opacity_factor) {
    document.getElementById('header').style.opacity = opacity_factor;
    document.getElementById('header').style.filter = "blur(" + blur_factor + ")";
    document.getElementById('input_container').style.opacity = opacity_factor;
    document.getElementById('input_container').style.filter = "blur(" + blur_factor + ")";

}

personalize_greetings(username);