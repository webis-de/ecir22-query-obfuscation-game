var polygon_counter = 1;
var drawing_permission = false;
var clicked_on_circle = false;
/*var delete_permission = false;


function deletePolygon(){
    delete_permission = true;
}

function selectPolygonToDelete(event){
    if (delete_permission == true) {
        event.target.remove();
        delete_permission = false;
    }
}*/


function draw(event){
    if (drawing_permission == true) {
        //console.log('results of x and y '+ x + ', ' + y);
        clicked_on_circle = drawPolygon(event);
        if (clicked_on_circle == false) {
            drawCircle(event);
        }
    }

}

function drawPolygon(event){
    var x, y = 0;
    clicked_on_circle = false;
    if (event.target.nodeName == 'circle') {
        console.log("You hit a circle");
        x = event.target.getAttribute('cx');
        y = event.target.getAttribute('cy');
        clicked_on_circle = true;
    }
    else {
        x = event.offsetX;
        y = event.offsetY;
    }
    var current_polygon = document.getElementById('polygon'+(polygon_counter));
    var svg = document.getElementById('canvas');
    var point = svg.createSVGPoint();
    point.x = x;
    point.y = y;
    current_polygon.points.appendItem(point);
    return clicked_on_circle;

}

function drawCircle(event) { 
	var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
	var svgNS = svg.namespaceURI;
	var circle = document.createElementNS(svgNS,'circle');

	var x = event.offsetX;
	var y = event.offsetY;

	circle.setAttribute('cx',x);
	circle.setAttribute('cy',y);
	circle.setAttribute('r',5);
	circle.setAttribute('fill','white');

	var canvas = document.getElementById('canvas');
	canvas.appendChild(circle);
    console.log('x and y '+ x + ', ' + y);
    return x, y;		
}

function addPolygon(event) {
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    var svgNS = svg.namespaceURI;
    var polygon = document.createElementNS(svgNS,'polygon');

    polygon.setAttribute('style', 'stroke: #cccccc; stroke-width: 1px');
    polygon.setAttribute('points', '');
    polygon.setAttribute('id', 'polygon'+ polygon_counter)
    var canvas = document.getElementById('canvas');
    canvas.insertAdjacentElement('afterbegin', polygon);
    //canvas.appendChild(polygon); 
    drawing_permission = true;
}

function endDrawing() {
    polygon_counter = polygon_counter + 1;
    drawing_permission = false;
}

function download() {
    var list_of_polygons = document.getElementsByTagName('polygon');
    text = '';
    console.log(list_of_polygons[0].outerHTML);
    for (i = 0; i < list_of_polygons.length; i++) {
        console.log(list_of_polygons[i].outerHTML);
        text += String(list_of_polygons[i].outerHTML + '\n');
        console.log(text);
    }

  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  element.setAttribute('download', 'polygons.txt');

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}
