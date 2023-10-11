import logging
import paho.mqtt.client as mqtt


class HeaterController:

    def __init__(self, on_value: int, off_value: int, protocol_number: int, protocol_length: int, delay: int, control_topic: str, mqtt_client: mqtt.Client):
        self.mqtt_client = mqtt_client
        self.control_topic = control_topic

        self.on_payload = {
            "value": on_value,
            "protocol": protocol_number,
            "length": protocol_length,
            "delay": delay
        }

        self.off_payload = {
            "value": off_value,
            "protocol": protocol_number,
            "length": protocol_length,
            "delay": delay
        }

    def set_state(self, state: bool):

        if state:
            payload = str(self.on_payload)
        else:
            payload = str(self.off_payload)

        # payload dictionary --> JSON --> MQTT --> OpenMQTTGateway --> ISM 433 MHz --> heater
        self.mqtt_client.publish(topic=self.control_topic, payload=payload)
        logging.debug(f"Published {payload} to {self.control_topic}")


class Heater:

    def __init__(self, name: str, heater_controller: HeaterController, default_power: int, config_topic: str, mqtt_client: mqtt.Client):
        self.name = name
        self.heater_controller = heater_controller
        self.config_topic = config_topic
        self.mqtt_client = mqtt_client

        self.pref_state = False  # Indicates whether you would like the fan to run. Whether it actually runs is not stored and depends on the power generation
        self.power = default_power  # How much power consumes - many devices have different power levels

        mqtt_client.message_callback_add(self.config_topic + "set/pref_state", self.pref_state_callback)
        mqtt_client.message_callback_add(self.config_topic + "set/power", self.power_callback)

    def pref_state_callback(self, mosq, obj, msg):  # noqa when I removed it I got an error, even though it is not used

        if msg.payload == b"on":
            self.pref_state = True
        else:
            self.pref_state = False
        logging.info(f"Preferred state of {self.name} changed to {self.pref_state}")

    def power_callback(self, mosq, obj, msg):  # noqa when I removed it I got an error, even though it is not used
        try:
            power = int(msg.payload)
            if power >= 0:
                self.power = power
                logging.info(f"Power of {self.name} changed to {self.power}")
            else:
                raise ValueError

        except ValueError:
            logging.warning(f"Error while parsing power value {msg.payload} for {self.name}")

    def set_state(self, state: bool):
        self.heater_controller.set_state(state)
        logging.info(f"Set state of {self.name} to {state}")
