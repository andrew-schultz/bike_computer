import { useEffect, useState } from 'react';

import GraphSelector from './GraphSelector.jsx';
import BarPlot from './BarPlot.jsx'; 
import LinePlot from './LinePlot.jsx';


const VisualizationMain = ({statUuid}) => {
    const [selectedGraph, setSelectedGraph] = useState('heart rate');
    const [currentData, setCurrentData] = useState();
    const [dataX, setDataX] = useState();
    const [dataY, setDataY] = useState();
    const [timeData, setTimeData] = useState();
    const [currentHeaders, setCurrentHeaders] = useState('');
    const [uuid, setUuid] = useState();

    const graphTypes = ['cadence', 'heart rate', 'speed', 'distance',];
    // const uuid = '8ab2e10a-39e4-402c-85ca-8394b781d65b';
    // const uuid = '47f87357-5134-4eea-8dbd-243e914a4026';

    const fileReader = new FileReader();

    useEffect(() => {
        setUuid(statUuid)
    }, [statUuid])

    const handleSetSelectedGraph = async (selected) => {
        console.log(selected);
        setSelectedGraph(selected);
        const [headers, data, timeArray, xArray, yArray] = await fetchCsv(uuid, selected.replace(' ', '_'));
        
        setCurrentHeaders(headers);
        setCurrentData(data);
        setTimeData(timeArray);
        setDataX(xArray);
        setDataY(yArray);
    };

    const processData = async (csv_array) => {
        // simple example of a row in the array
        // '"01/17/2024, 17:50:31",92'
        const processedArray = [];
        const timeArray = [];
        const xArray = [];
        const yArray = [];

        csv_array.forEach(row => {
            const rowArray = [];
            // toss the date
            // row = row.split(', ')[1];
            // debugger
            // split the parts
            if (row) {
                row = row.split(',');
                row.forEach(i => {
                    // // remove the trailing " from the time
                    // i = i.replace('"', '');
                    if (i) {
                        rowArray.push(i)
                    } else {
                        rowArray.push(0)
                    }
                })
                processedArray.push(rowArray);
                timeArray.push(rowArray[0]);
                xArray.push(rowArray[1]);
                yArray.push(rowArray[2]);
            }
        })

        return [processedArray, timeArray, xArray, yArray];
    }

    const fetchCsv = async (uuid, graph) => {
        const response = await fetch(`${uuid}_${graph}.csv`);
        const reader = response.body.getReader();
        const result = await reader.read();
        const decoder = new TextDecoder('utf-8');
        // csv is just a long string at this point
        const csv = await decoder.decode(result.value);

        // 'split' the array on '\r\n'
        const csv_array = csv.split('\r\n');

        // remove the first item in the array, should be the headers
        const headers = csv_array.shift();

        const [processedArray, timeArray, xArray, yArray] = await processData(csv_array);

        return [processedArray, timeArray, xArray, yArray];
    }
    
    return (
        <div className='visualizationMainDiv'>
            {uuid ?
            <div>
                <div className='flex items-center justify-center content-center'>
                    {/* {dataX ? 
                        <LinePlot
                            dataX={dataX}
                        ></LinePlot> : ''} */}
                    {uuid && selectedGraph ? 
                        <BarPlot
                            uuid={uuid}
                            graphType={selectedGraph.replace(' ', '_')}
                            dataX={dataX}
                        ></BarPlot> : ''}
                </div>
                <div className='flex items-center justify-center'>
                    <GraphSelector 
                        graphTypes={graphTypes}
                        selectedGraph={selectedGraph}
                        handleSetSelectedGraph={handleSetSelectedGraph}
                    ></GraphSelector>
                </div> 
            </div> : ''
            }
        </div>
    )
}

export default VisualizationMain