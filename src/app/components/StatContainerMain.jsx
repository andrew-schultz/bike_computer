import { useEffect, useState } from 'react';

import StatContainer from "./StatContainer";
import RecordButton from "./RecordButton";
import VisualizationMain from './VisualizationMain';

import PubNubService from "../services/pubnub";


const PUBNUB_DEFAULT_CHANNEL = process.env.NEXT_PUBLIC_PUBNUB_DEFAULT_CHANNEL

const StatContainerMain = ({}) => {
    const defaultStats = {
        'cadence': '--',
        'speed': '--',
        'distance': '--',
        'heart_rate': '--',
    }

    // const [stats, setStats] = useState(defaultStats);
    const [speed, setSpeed] = useState('--');
    const [distance, setDistance] = useState('--');
    const [cadence, setCadence] = useState('--');
    const [heartRate, setHeartRate] = useState('--');
    const [recordState, setRecordState] = useState(false);
    const [pubnub, setPubnub] = useState();
    const [uuid, setUuid] = useState();

    useEffect(() => {
        const pubnub = PubNubService(handleMessage)
        setPubnub(pubnub)
    }, [])

    // stuff here about updating the values passed in to each StatContainer component?
    const handleMessage = (messageEvent) => {    
        if (messageEvent.message.device_type == 'cadence') {
            setCadence(messageEvent.message.cadence)
        }
        else if (messageEvent.message.device_type == 'speed') {
            setSpeed(messageEvent.message.speed)
            setDistance(messageEvent.message.distance)
        }
        else if (messageEvent.message.device_type == 'heart_rate') {
            setHeartRate(messageEvent.message.heart_rate)
        }
        else if (messageEvent.message.action == 'statsReady') {
            setUuid(messageEvent.message.uuid)
        }
    }

    const handleRecordToggle = () => {
        const newRecordState = !recordState;

        const messageBody = {
            'action': 'record',
            'record': newRecordState,
        }

        pubnub.publish({
            channel: PUBNUB_DEFAULT_CHANNEL,
            message: messageBody
        })

        setRecordState(newRecordState);
    }

    return (
        <div className="min-h-screen p-24">
            <div className="flex columns-2 items-center justify-between">
                <div className="flex flex-col items-center justify-between w-1/2">
                    <StatContainer name={'Speed'} unit={'km/hr'} stat={speed}></StatContainer>
                    <StatContainer name={'Distance'} unit={'km'} stat={distance}></StatContainer>
                </div>
                <div className="flex flex-col items-center justify-between w-1/2">
                    <StatContainer name={'Cadence'} unit={'RPM'} stat={cadence}></StatContainer>
                    <StatContainer name={'Heart Rate'} unit={'BPM'} stat={heartRate}></StatContainer>
                </div>
            </div>

            <div className="flex items-center justify-center">
                <RecordButton handleRecordToggle={handleRecordToggle} recordState={recordState}></RecordButton>
            </div>

            <VisualizationMain
                statUuid={uuid}
            ></VisualizationMain>
        </div>
        
    )
};

export default StatContainerMain;