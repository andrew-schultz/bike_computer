import * as d3 from "d3";
import { useEffect, useRef } from "react";


const BarPlot = ({
    uuid,
    graphType,
}) => {
    const ref = useRef();

    const margin = { top: 30, right: 20, bottom: 70, left: 30 },
    width = 600 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

    useEffect(()=> {
        // append the svg object to the body of the page
        const mainSvg = d3
            .select(ref.current)
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

    }, [])

    const update = (uuid, graphType) => {
        const url = `${uuid}_${graphType}.csv`

        // old axis & bars
        var svg = d3.select("#barchart").select("svg").select("g");
        svg.selectAll("g").remove();

        // tooltip
        var tooltip = d3.select('body').select('.barChartToolTip')
        if (tooltip.empty()) {
            tooltip = d3.select("body").append("div")
            .attr("class", "barChartToolTip")
            .style("opacity", 0)
            .style("position", 'absolute');
        }

        d3.csv(url).then( (data) => {
            // X axis
            const keys = Object.keys(data[0])
            const x = d3.scaleTime([new Date(data[0].timestamp * 1000), new Date(data[data.length - 1].timestamp * 1000)], [0, width])

            svg.append("g")
                .attr("transform", `translate(0, ${height})`)
                .call(d3.axisBottom(x))
                .selectAll("text")
                .attr("transform", "translate(-10,0)rotate(-45)")
                .style("text-anchor", "end");

            // Add Y axis
            // get the lowest and highest values to set the y axis domain
            var max = Math.max(...data.map(e => e[keys[1]]));
            var min = Math.min(...data.map(e => e[keys[1]])) - 10;
            min = min >= 0 ? min : 0;

            const y = d3.scaleLinear().domain([min, max + 10]).range([height, 0]);
            svg.append("g").call(d3.axisLeft(y));

            // Bars
            var u = svg.selectAll("rect")
                .data(data);

            // update bars
            u
                .join(
                    enter => enter.append("rect"),
                    update => update,
                    exit => exit.remove()
                )
                .on("mouseover", (event) => {
                    if (event.srcElement) {
                        event.srcElement.style.opacity = 0.25;
                    }
                    if (tooltip) {
                        const text = event.srcElement && event.srcElement.__data__ ? event.srcElement.__data__[keys[1]] : '0'
                        tooltip.transition()
                            .duration(50)
                            .style("opacity", 1);

                        tooltip.html(text)
                            .style("left", (event.pageX + 10) + "px")
                            .style("top", (event.pageY - 15) + "px");
                    }
                })
                .on("mousemove", (event) => {
                    return tooltip.style("top", (event.pageY - 40) + "px").style("left", (event.pageX - 10) + "px");
                })
                .on("mouseout", (event) => {
                    if (event.srcElement) {
                        event.srcElement.style.opacity = 1.0;
                    }
                    tooltip.transition()
                        .duration(50)
                        .style("opacity", 0);
                })
                .transition()
                .duration(1000)
                .attr("x", (d) => x(new Date(d.timestamp * 1000)))
                .attr("y", (d) => y(d[keys[1]]))
                .attr("width", width/data.length)
                .attr("height", (d) => height - y(d[keys[1]]))
                .attr("fill", "#5f0f40");
            }
        )
    }

    useEffect(() => {
        update(uuid, graphType)
    }, [uuid, graphType])

    return <svg width={600} height={500} id="barchart" ref={ref} />;
}

export default BarPlot