import * as d3 from "d3";
import {useRef, useEffect} from "react";

export default function LinePlot({
    dataX=[],
    dataY=[],
    dataTime=[],
    headers=[],
    width = 640,
    height = 400,
    marginTop = 20,
    marginRight = 20,
    marginBottom = 30,
    marginLeft = 40
}) {
    const gx = useRef();
    const gy = useRef();
    // debugger
    // const data = dataX;
    const x = d3.scaleLinear([0, dataX.length - 1], [marginLeft, width - marginRight]);
    const y = d3.scaleLinear(d3.extent(dataX), [height - marginBottom, marginTop]);
    const line = d3.line((d, i) => x(i), y);

    useEffect(() => void d3.select(gx.current).call(d3.axisBottom(x)), [gx, x]);
    useEffect(() => void d3.select(gy.current).call(d3.axisLeft(y)), [gy, y]);
    return (
      <svg width={width} height={height}>
        <g ref={gx} transform={`translate(0,${height - marginBottom})`} />
        <g ref={gy} transform={`translate(${marginLeft},0)`} />
        <path fill="black" stroke="currentColor" strokeWidth="1.5" d={line(dataX)} />
        <g fill="white" stroke="currentColor" strokeWidth="1.5">
          {dataX.map((d, i) => (<circle key={i} cx={x(i)} cy={y(d)} r="2.5" />))}
        </g>
      </svg>
    );
}