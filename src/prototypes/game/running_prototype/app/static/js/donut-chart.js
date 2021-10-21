function draw_donut(data, color_scheme, key) {
        item = "#" + key + "_donut";
        var svg = d3.select(item),
            width = 70,
            height = 70,
            radius = Math.min(width, height) / 2,
            g = svg.append("g").attr("transform", "translate(" + (width / 2) + "," + (height / 2) + ")");

        var color = d3.scaleOrdinal(color_scheme);

        // Generate the pie
        var pie = d3.pie();
        pie.sort(null);

        // Generate the arcs
        var arc = d3.arc()
                    .innerRadius(30)
                    .outerRadius(radius);

        //Generate groups
        var arcs = g.selectAll("arc")
                    .data(pie(data))
                    .enter()
                    .append("g")
                    .attr("class", "arc")

        //Draw arc paths
        arcs.append("path")
            .attr("fill", function(d, i) {
                return color(i);
            })
        .attr("d", arc);
}

function draw_donut_charts(level) {
    factor = 1
    if (level == "") {
        index = 2;
        factor = 2;
        color_scheme = ['#ffffff','#4d4d4d'];
    } else if (level == "squid") {
        index = 0;
        color_scheme = ['#03B7DF','#4d4d4d'];
    } else {
        index = 1;
        color_scheme = ['#ff00ff','#4d4d4d'];
    }
    for (key in played_games_data) {
        data = [played_games_data[key][index],
                (played_games_data[key][3] * factor) - played_games_data[key][index]];
        draw_donut(data, color_scheme, key);
    }
}

draw_donut_charts("");