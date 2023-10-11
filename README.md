## Consume your own electricity instead of feeding it in with losses

### Overview
This project is designed to operate on a server and listen for MQTT messages, commanding heating devices. Its primary function is to assess the surplus energy available and efficiently direct it towards heating purposes. This is achieved by managing the operation of available heating devices in such a way that a maximum amount of surplus energy is used for heating.

#### Features
- Monitors MQTT messages for heater control instructions.
- Utilizes [SMLReader](https://github.com/mruettgers/SMLReader) to receive real-time surplus energy information via MQTT.
- Employs [OpenMQTTGateway](https://github.com/1technophile/OpenMQTTGateway) to communicate with radio-controlled outlets that power the fan heaters. These outlets operate within the ISM band.

#### License
This project is licensed under MIT - you can find the details in the LICENSE file.

#### Acknowledgments
Special thanks to the authors and contributors of SMLReader and OpenMQTTGateway for their valuable tools and libraries.
