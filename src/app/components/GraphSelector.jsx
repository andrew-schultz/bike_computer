
const GraphSelector = ({
    graphTypes,
    selectedGraph,
    handleSetSelectedGraph,
}) => {

    const GraphTypeButtons = (graphTypes) => (
        <>
          {graphTypes.map(graphType => (
            <div 
                key={`${graphType}_graph_button`}
                className={`border-2 w-full content-center text-center m-2 p-2 cursor-pointer ${selectedGraph == graphType ? 'bg-slate-400' : 'bg-slate-100'}`}
                onClick={(e) => handleSetSelectedGraph(graphType)}
                
            >{graphType}</div>
          ))}
        </>
    ); 

    return (
        <div className='flex items-center justify-center'>
            {GraphTypeButtons(graphTypes)}
        </div>
    )
}

export default GraphSelector