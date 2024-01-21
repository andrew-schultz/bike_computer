const PubNub = require('pubnub');


const PubNubService = (messageHandler) => {
    const pubnub = new PubNub({
        publishKey: process.env.NEXT_PUBLIC_PUBNUB_PUB_KEY,
        subscribeKey: process.env.NEXT_PUBLIC_PUBNUB_SUB_KEY,
        userId: "12345abc",
    });
    
    const PUBNUB_DEFAULT_CHANNEL = process.env.NEXT_PUBLIC_PUBNUB_DEFAULT_CHANNEL
    
    // paste below "add listener" comment
    const listener = {
        status: (statusEvent) => {
            if (statusEvent.category === "PNConnectedCategory") {
                console.log("Connected");
            }
        },
        message: (messageEvent) => {
            // console.log('got a message', messageEvent)
            messageHandler(messageEvent);
            // showMessage(messageEvent.message.description);
        },
        presence: (presenceEvent) => {
            // handle presence
        }
    };
    pubnub.addListener(listener);
    
    // publish message
    const publishMessage = (message) => {
        pubnub.publish({
            channel: PUBNUB_DEFAULT_CHANNEL,
            message: message
        });
    }
    
    // subscribe to a channel
    pubnub.subscribe({
        channels: [PUBNUB_DEFAULT_CHANNEL],
    });
    
    const showMessage = (msg) => {
        console.log("message: " + msg);
    }

    return pubnub;
}


export default PubNubService