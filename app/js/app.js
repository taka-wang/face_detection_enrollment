var 
    wsbroker = "127.0.0.1",
    wsport = 11883,
    client = new Paho.MQTT.Client(wsbroker, wsport, 'myclientid_' + parseInt(Math.random() * 100, 10)),
    options = {
        timeout: 3,
        onSuccess: function() {
            console.log('mqtt connected');
            // subscribe
            client.subscribe('myimage', { qos: 1 });
        },
        onFailure: function(message) {
            console.log('Connection failed: ' + message.errorMessage);
        }
    };

client.onConnectionLost = function (responseObject) {
    console.log("connection lost: " + responseObject.errorMessage);
};

client.onMessageArrived = function (message) {
    $("#camera").attr('src', 'data:image/jpg;base64,' + message.payloadString);
};

$(document).ready(function() {
    client.connect(options);
});