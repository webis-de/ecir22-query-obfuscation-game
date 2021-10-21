function draw_donut(data, color_scheme, key, categories) {
		var width = 300;
		var height = 300;
		var radius = 140;
		var margin = {top: 90, right: 20, bottom: 30, left: 20};

		var svg = d3.select("#piecharts").append("svg")
			.attr("width", width + margin.top + margin.bottom)
			.attr("height", height + margin.left + margin.right)
			.append("g")
			.attr("transform", "translate(" + (width + margin.top + margin.bottom) / 2 + "," + (height + margin.left + margin.right) / 2 + ")");

    	svg.append("text")
            .attr("x", 0)
            .attr("y", 0 - (height/2))
            .attr("text-anchor", "middle")
            .style("font-size", "28px")
            .text(key);

        var div = d3.select("body")
            .append("div")
            .attr("class", "tooltip");

		var arc = d3.svg.arc()
				.outerRadius(radius);

		var pie = d3.layout.pie()
				.sort(null);

		var g = svg.selectAll(".fan")
				.data(pie(data))
				.enter()
				.append("g")
				.attr("class", "fan")
				.on("mousemove",function(d, i){
                var mouseVal = d3.mouse(this);
                    div.style("display","none");
                    div
                        .html(categories[i] + ": " + d.data)
                        .style("left", (d3.event.pageX+12) + "px")
                        .style("top", (d3.event.pageY-10) + "px")
                        .style("opacity", 1)
                        .style("display","block");
                })
                .on("mouseout",function(){div.html(" ").style("display","none");});

		g.append("path")
			.attr("d", arc)
			.attr("fill", function(d, i){ return color_scheme[i]; });
}

function draw_donut_charts() {
        color_scheme = ['#03B7DF', '#ff00ff', '#103b56'];
        categories = ["Level Squid", "Level Chameleon", "Total Number of Queries"];
    for (key in played_games_data) {
        data = [played_games_data[key][0], played_games_data[key][1],
                (played_games_data[key][3] * 2) - played_games_data[key][0] - played_games_data[key][1]];
        draw_donut(data, color_scheme, key, categories);
    }
}

draw_donut_charts();