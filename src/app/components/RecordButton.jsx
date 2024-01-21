
// interface RecordButtonProps {
//     handleRecordToggle(): void;
//     recordState: boolean;
// }

const RecordButton = ({handleRecordToggle, recordState}) => {

    return (
        <div className='border-2 w-full content-center text-center p-5 m-10 cursor-pointer font-bold w-1/6' onClick={(e) => handleRecordToggle()}>
            {recordState ? 'Stop' : 'Record'}
        </div>
    )
};

export default RecordButton;