document$.subscribe(function () {

    document.querySelectorAll("div.threatActor-tools").forEach(function (element) {
        fetch("../01_attachements/data/threatActor-tools.json")
            .then(response => response.json())
            .then(data => {
                // Create the chart and append it to the element
                const chart = createEdgeBundlingChart(data);
                element.innerHTML = ''; // Clear the div before appending the chart
                element.appendChild(chart);
            })
            .catch(error => console.error("Failed to load data", error));
    });


    function createEdgeBundlingChart(data) {
        const width = 1000;
        const radius = width / 2;
        const colorin = "#00f";
        const colorout = "#f00";
        const colornone = "#ccc";


        const svg = d3.create("svg")
            .attr("viewBox", [-width / 2, -width / 2, width, width])
            .attr("width", width)
            .attr("height", width)
            .attr("style", "max-width: 100%; height: auto; font: 10px sans-serif;");

        // Create a radial tree layout
        const tree = d3.cluster()
            .size([2 * Math.PI, radius - 100]);

        // Convert the data into a hierarchy
        const root = d3.hierarchy(data, function (d) { return d.children; });

        // Compute the tree layout
        tree(root);

        // Create the line generator for links
        const line = d3.radialLine()
            .curve(d3.curveBundle.beta(0.85))
            .radius(d => d.y)
            .angle(d => d.x);

        // Define the bilink function to create links
        bilink(root);

        // Draw the links on the graph
        const link = svg.append("g")
            .attr("stroke", colornone)
            .attr("fill", "none")
            .selectAll("path")
            .data(root.leaves().flatMap(leaf => leaf.outgoing))
            .join("path")
            .style("mix-blend-mode", "multiply")
            .attr("d", ([i, o]) => line(i.path(o)))
            .each(function (d) { d.path = this; });

        // Draw the nodes on the graph
        svg.append("g")
            .selectAll("text")
            .data(root.leaves())
            .join("text")
            .attr("transform", d => `
                rotate(${d.x * 180 / Math.PI - 90})
                translate(${d.y},0)
                rotate(${d.x >= Math.PI ? 180 : 0})
            `)
            .attr("text-anchor", d => d.x < Math.PI ? "start" : "end")
            .text(d => d.data.id)
            .attr("fill", colornone)
            .style("font-size", 10)
            .style("user-select", "none")
            .on("mouseover", overed)
            .on("mouseout", outed);

        // Define the overed function
        function overed(event, d) {
            link.style("mix-blend-mode", null);
            console.log(d);
            console.log(d3.selectAll(d.incoming.map(d => d.path)));
            d3.select(event.currentTarget).attr("font-weight", "bold");
            d3.selectAll(d.incoming.map(d => d.path)).attr("stroke", colorin).raise();
            d3.selectAll(d.incoming.map(([d]) => d.text)).attr("fill", colorin).attr("font-weight", "bold");
            d3.selectAll(d.outgoing.map(d => d.path)).attr("stroke", colorout).raise();
            d3.selectAll(d.outgoing.map(([, d]) => d.text)).attr("fill", colorout).attr("font-weight", "bold");
        }

        // Define the outed function
        function outed(event, d) {
            link.style("mix-blend-mode", "multiply");
            d3.select(event.currentTarget).attr("font-weight", null);
            d3.selectAll(d.incoming.map(d => d.path)).attr("stroke", null).lower();
            d3.selectAll(d.incoming.map(([d]) => d.text)).attr("fill", null).attr("font-weight", null);
            d3.selectAll(d.outgoing.map(d => d.path)).attr("stroke", null).lower();
            d3.selectAll(d.outgoing.map(([, d]) => d.text)).attr("fill", null).attr("font-weight", null);
        }
        // Return the SVG node
        return svg.node();
    }

    function bilink(root) {
        const map = new Map(root.leaves().map(d => [d.data.id, d]));
        for (const d of root.leaves()) {
            d.outgoing = d.data.relations.map(id => [d, map.get(id)]);
            d.incoming = [];
        }
        for (const d of root.leaves()) {
            for (const o of d.outgoing) {
                o[1].incoming.push(o);
            }
        }
    }

});