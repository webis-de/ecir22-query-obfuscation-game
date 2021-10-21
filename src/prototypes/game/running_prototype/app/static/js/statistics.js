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
});

function background_style(blur_factor, opacity_factor) {
    document.getElementById('header').style.opacity = opacity_factor;
    document.getElementById('header').style.filter = "blur(" + blur_factor + ")";
    document.getElementById('stats_container').style.opacity = opacity_factor;
    document.getElementById('stats_container').style.filter = "blur(" + blur_factor + ")";

}