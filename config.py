config = {
    "update_cooldown_in_seconds": 20,  # To ignore high power consumption peaks on startup or small clouds
    "energy_overproduction_topic": "home/smartmeter/electricity/sensor/1/obis/1-0:16.7.0/255/value",  # the channel where we receive the currently available energy

    "mqtt_credentials": {
        "hostname": "My_MQTT_IP",
        "username": "My_MQTT_User_Name",
        "password": "My_MQTT_Password"
    },

    "ism_protocol": {  # Values for OpenMQTTGateway - I use the RCSwitch build and provide the values as JSON
        "protocol_number": 1,  # RCSwitch::setProtocol(int nProtocol)
        "protocol_length": 20,  # RCSwitch::send(unsigned long code, unsigned int length)  // code is provided as on_value in heaters
        "delay": 300  # RCSwitch::setPulseLength(int nPulseLength)
    },

    "heaters": [
        {
            "name": "Nathaniel",  # for you logs
            "default_power": 1975,  # power consumption of the heater in Watt
            "config_topic": "home/fanheater/livingroom/",  # channel to control this app over MQTT with your smart home system or something
            "control_topic": "home/openmqttgateway/commands/MQTTto433",  # channel to control the heater/433MHz power sockets over OpenMQTTGateway
            "on_value": 324352,  # value of the 433MHz power sockets used by RCSwitch - you have to somehow find out what your sockets respond to
            "off_value": 324367
        },
        {
            "name": "Bernd",
            "default_power": 1005,
            "config_topic": "home/fanheater/office/",
            "control_topic": "home/openmqttgateway/commands/MQTTto433",
            "on_value": 545675,
            "off_value": 545692
        }
    ]
}
