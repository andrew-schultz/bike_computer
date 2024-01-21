
const StatContainer = ({name, unit, descriptionText, stat}) => {

    return (
        <div className="border-2 w-full content-center text-center p-3">
            <p className="text-1xl">{name}</p>
            <p className="text-8xl">{stat ? stat : '--'} <span className="text-sm font-bold">{unit}</span></p>
        </div>
    )
};

export default StatContainer;