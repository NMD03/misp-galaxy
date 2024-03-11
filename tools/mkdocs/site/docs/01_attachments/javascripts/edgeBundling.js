document$.subscribe(function () {

    document.querySelectorAll("div.tidal").forEach(function (element) {
        // fetch("../01_attachements/data/test.json")
        fetch("../01_attachments/data/tidal.json")
            .then(response => response.json())
            .then(data => {
                // Create the chart and append it to the element
                const chart = createEdgeBundlingChart(data);
                element.innerHTML = ''; // Clear the div before appending the chart
                element.appendChild(chart);
            })
            .catch(error => console.error("Failed to load data", error));
    });


    function createEdgeBundlingChart(inputData) {
        const width = 1000;
        const radius = width / 2;
        const colorin = "#00f";
        const colorout = "#f00";
        const colornone = "#ccc";
        const innerRadius = radius - 150; // Radius for inner nodes
        const outerRadius = radius - 50; // Radius for outer nodes
        const nodeColor = "#888";

        const data = hierarchy(inputData);
        console.log(data);

        const svg = d3.create("svg")
            .attr("viewBox", [-width / 2, -width / 2, width, width])
            .attr("width", width)
            .attr("height", width)
            .attr("style", "max-width: 100%; height: auto; font: 10px sans-serif;");

        // Create a radial tree layout
        const tree = d3.cluster()
            .size([2 * Math.PI, innerRadius]);


        const root = tree(bilink(d3.hierarchy(data)
            .sort((a, b) => d3.ascending(a.height, b.height) || d3.ascending(a.data.name, b.data.name))));

        // Assign radii to nodes based on their category (inner or outer)
        root.leaves().forEach(node => {
            node.data.radius = node.outgoing.length > 0 || node.incoming.length > 0 ? innerRadius : outerRadius;
        });

        console.log(root);
        // Define the line generator for links
        const line = d3.radialLine()
            .curve(d3.curveBundle.beta(0.85))
            .radius(d => d.y) // Access the stored radius
            .angle(d => d.x);

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


        // const calculateRadius = d => d.outgoing.length > 0 || d.incoming.length > 0 ? innerRadius : outerRadius;

        // Generalized node rendering to include positioning based on node type (inner or outer)
        const renderNodes = (nodes, radiusCalc) => {
            return nodes
                .join("g")
                .attr("transform", d => {
                    const calculatedRadius = radiusCalc(d);
                    const rotation = d.x * 180 / Math.PI - 90;
                    const angle = d.x < Math.PI ? rotation : rotation; // Adjust angle for outer circle
                    return `rotate(${angle}) translate(${calculatedRadius},0)`;
                })
                .append("text")
                .attr("dy", "0.31em")
                .attr("x", d => d.x < Math.PI ? 6 : -6)
                .attr("text-anchor", d => d.x < Math.PI ? "start" : "end")
                .attr("transform", d => d.x >= Math.PI ? "rotate(180)" : null)
                .attr("fill", nodeColor)
                .text(d => d.data.name)
                .each(function (d) { d.text = this; })
                .on("mouseover", overed)
                .on("mouseout", outed)
                .call(text => text.append("title").text(d => `${id(d)}
                    ${d.outgoing.length} outgoing
                    ${d.incoming.length} incoming`));
        };

        // Render inner nodes
        renderNodes(svg.append("g").selectAll().data(root.leaves().filter(d => d.outgoing.length > 0 || d.incoming.length > 0)), d => innerRadius);

        // Render outer nodes
        renderNodes(svg.append("g").selectAll().data(root.leaves().filter(d => d.outgoing.length === 0 && d.incoming.length === 0)), d => outerRadius);

        // const zoom = d3.zoom()
        //     .scaleExtent([1, 8]) // Set the scale limits
        //     .on('zoom', (event) => {
        //         svg.attr('transform', event.transform);
        //     });

        // svg.call(zoom);



        // Define the overed function
        function overed(event, d) {
            link.style("mix-blend-mode", null);
            console.log(d);
            // console.log(d3.selectAll(d.incoming.map(d => d.path)));
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
            d3.selectAll(d.incoming.map(([d]) => d.text)).attr("fill", nodeColor).attr("font-weight", null);
            d3.selectAll(d.outgoing.map(d => d.path)).attr("stroke", null).lower();
            d3.selectAll(d.outgoing.map(([, d]) => d.text)).attr("fill", nodeColor).attr("font-weight", null);
        }
        // Return the SVG node
        return svg.node();
    }

    function id(node) {
        return `${node.parent ? id(node.parent) + ";" : ""}${node.data.name}`;
    }

    function bilink(root) {
        console.log(root);
        const map = new Map(root.leaves().map(d => [id(d), d]));
        for (const d of root.leaves()) d.incoming = [], d.outgoing = d.data.relations.map(i => [d, map.get(i)]);
        for (const d of root.leaves()) for (const o of d.outgoing) o[1].incoming.push(o);
        return root;
    }

    function hierarchy(data, delimiter = ";") {
        let root;
        const map = new Map;
        data.forEach(function find(data) {
            const { name } = data;
            if (map.has(name)) return map.get(name);
            const i = name.lastIndexOf(delimiter);
            map.set(name, data);
            if (i >= 0) {
                find({ name: name.substring(0, i), children: [] }).children.push(data);
                data.name = name.substring(i + 1);
            } else {
                root = data;
            }
            return data;
        });
        return root;
    }

});