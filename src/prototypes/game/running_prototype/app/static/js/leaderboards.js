$('#menu_icon').on('click', function() {
    document.getElementById('close_menu').style.display = "inline";
    document.getElementById('menu_overlay').style.display = "block";
    document.getElementById('leaderboards_container').style.filter = "blur(10px)";
    document.getElementById('leaderboards_container').style.pointerEvents = "none";
    var leaderboard_header = document.getElementsByClassName('leaderboard_header');
    for (i = 0; i < leaderboard_header.length; i++) {
        leaderboard_header[i].style.top = "-90px";
    }
});

$('#close_menu').on('click', function() {
    document.getElementById('close_menu').style.display = "none";
    document.getElementById('menu_overlay').style.display = "none";
    document.getElementById('leaderboards_container').style.filter = "";
    document.getElementById('leaderboards_container').style.pointerEvents = "auto";
        var leaderboard_header = document.getElementsByClassName('leaderboard_header');
    for (i = 0; i < leaderboard_header.length; i++) {
        leaderboard_header[i].style.top = "160px";
    }
});


function set_focus_on_user() {
    cookie_id = getCookie('user_id');
    user_entry = document.getElementsByClassName('user_id');
    for (i = 0; i < user_entry.length; i++) {
        if (cookie_id == String(user_entry[i].classList[1])) {
            parent = user_entry[i].parentElement.parentElement;
            scrollParentToChild(parent, user_entry[i]);
            parent_id = parent.parentElement.parentElement.id;
            user_entry[i].parentElement.style.color = "#05131B";
            if (parent_id == "squid") {
                user_entry[i].parentElement.style.backgroundColor = "#03B7DF";
            }
            else if (parent_id == "chameleon") {
                user_entry[i].parentElement.style.backgroundColor = "#ff00ff";
            }
            else {
                user_entry[i].parentElement.style.backgroundColor = "white";
            }

        }
    }

}

function scrollParentToChild(parent, child, parentParent) {  //use .board instaed of list - then maybe it works better
      // What can you see?
      var parentViewableArea = {
        height: parent.clientHeight,
        width: parent.clientWidth
      };

      // Where is the child
      var childRect = child.getBoundingClientRect();
      // Is the child viewable?
      var isViewable = (childRect.bottom <= parentViewableArea.height);
      // if you can't see the child try to scroll parent
      if (!isViewable) {
            // scroll by offset relative to parent
            over_parent = parent.parentElement.parentElement;

            var overParentViewableArea = {
                height: over_parent.clientHeight,
                width: over_parent.clientWidth
            };
            scroll_var = childRect.bottom - overParentViewableArea.height;
            $("#" + over_parent.id).animate({ scrollTop: scroll_var }, '200');
      }
 }


function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for(var i = 0; i <ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

set_focus_on_user();


