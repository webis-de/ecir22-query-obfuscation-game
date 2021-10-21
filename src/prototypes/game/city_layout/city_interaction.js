
/*onmousemove = function(e){
console.log("mouse location:", e.clientX, e.clientY);
     document.getElementById("x_value").innerHTML = e.clientX;
    document.getElementById("y_value").innerHTML = e.clientY;
}*/

// Find your root SVG element

var svg = document.getElementById("canvas");

// Create an SVGPoint for future math
var pt = svg.createSVGPoint();

// Get point in global SVG space
function cursorPoint(evt){
  pt.x = evt.clientX; pt.y = evt.clientY;
  return pt.matrixTransform(svg.getScreenCTM().inverse());
}

svg.addEventListener('mousemove',function(evt){
  var loc = cursorPoint(evt);
  // Use loc.x and loc.y here
  document.getElementById("x_value").innerHTML = loc.x;
    document.getElementById("y_value").innerHTML = loc.y;
},false);