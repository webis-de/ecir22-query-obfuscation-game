function drawBarChart(data, mode) {
    var margin = {top: 90, right: 20, bottom: 30, left: 90},
        width = 730 - margin.left - margin.right,
        height = 420 - margin.top - margin.bottom;

    var x0 = d3.scale.ordinal()
        .rangeRoundBands([0, width], .1);

    var x1 = d3.scale.ordinal();

    var y = d3.scale.linear()
        .range([height, 0]);

    var color = d3.scale.ordinal()
        .range(["#ff00ff", "#03B7DF" , "white"]);

    var xAxis = d3.svg.axis()
        .scale(x0)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");
        //.tickFormat(d3.format(".2s"));

    if (mode == "points") {
        var svg = d3.select("#barcharts").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .attr("id", "points")
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    } else {
        var svg = d3.select("#barcharts").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .attr("id", "queries")
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    }

    var dates_data = d3.keys(data[0]).filter(function(key) { return key !== "date"; });

    data.forEach(function(d) {
        d.points = dates_data.map(function(name) { return {name: name, value: +d[name]}; });
    });

    x0.domain(data.map(function(d) { return d.date; }));
    x1.domain(dates_data).rangeRoundBands([0, x0.rangeBand()]);
    y.domain([0, d3.max(data, function(d) { return d3.max(d.points, function(d) { return d.value; }); })]);

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    if (mode == "points") {
        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("Points");

        svg.append("text")
            .attr("x", (width / 2))
            .attr("y", 0 - (margin.top / 2))
            .attr("text-anchor", "middle")
            .style("font-size", "28px")
            .text("Points");
    } else {
        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("Number of Queries");

        svg.append("text")
            .attr("x", (width / 2))
            .attr("y", 0 - (margin.top / 2))
            .attr("text-anchor", "middle")
            .style("font-size", "28px")
            .text("Number of obfuscated Queries");
    }

    var divTooltip = d3.select("body").append("div").attr("class", "tooltip");

    var state = svg.selectAll(".groups")
        .data(data)
        .enter().append("g")
        .attr("class", "groups")
        .attr("transform", function(d) { return "translate(" + x0(d.date) + ",0)"; });

    state.selectAll("rect")
        .data(function(d) { return d.points; })
        .enter().append("rect")
        .attr("width", x1.rangeBand() - 2)
        .attr("x", function(d) { return x1(d.name); })
        .attr("y", function(d) { return y(d.value); })
        .attr("height", function(d) { return height - y(d.value); })
        .style("fill", function(d) { return color(d.name); })
        .on("mousemove",function(d, i){
                var mouseVal = d3.mouse(this);
                    divTooltip.style("display","none");
                    divTooltip
                        .html(d.name + ": " + d.value)
                        .style("left", (d3.event.pageX+12) + "px")
                        .style("top", (d3.event.pageY-10) + "px")
                        .style("opacity", 1)
                        .style("display","block");
                })
        .on("mouseout",function(){divTooltip.html(" ").style("display","none");});
}


drawBarChart(data_points, "points");
drawBarChart(data_queries, "queries");