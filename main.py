import datetime
import paho.mqtt.client as mqtt
import logging
import config
from heater import Heater, HeaterController

heater_list = []
last_update_time = datetime.datetime.now()


def main():

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler("fan_heater_photovoltaic_control.log")
        ]
    )

    my_config = config.config

    mqtt_client = init_mqtt(my_config["mqtt_credentials"])

    # select method that handles every update of the current available energy from SMLReader over MQTT (around one update per second)
    mqtt_client.message_callback_add(my_config["energy_overproduction_topic"], evaluate_heater_state)

    generate_heater_from_config(mqtt_client, my_config)

    mqtt_client.loop_forever()


def generate_heater_from_config(mqtt_client: mqtt.Client, my_config):
    for heater_config in my_config["heaters"]:
        my_ism_protocol = my_config["ism_protocol"]  # arduino RCSwitch: setProtocol, setPulseLength, send(unsigned long code, unsigned int length)

        heater_controller = HeaterController(
            on_value=heater_config["on_value"],
            off_value=heater_config["off_value"],
            protocol_number=my_ism_protocol["protocol_number"],
            protocol_length=my_ism_protocol["protocol_length"],
            delay=my_ism_protocol["delay"],
            control_topic=heater_config["control_topic"],
            mqtt_client=mqtt_client
        )

        heater = Heater(
            name=heater_config["name"],
            heater_controller=heater_controller,
            default_power=heater_config["default_power"],
            config_topic=heater_config["config_topic"],
            mqtt_client=mqtt_client
        )

        heater_list.append(heater)
        logging.info(f"Added heater {heater.name} to heater list")


def init_mqtt(mqtt_credentials) -> mqtt.Client:
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(username=mqtt_credentials["username"], password=mqtt_credentials["password"])
    mqtt_client.connect(host=mqtt_credentials["hostname"])
    mqtt_client.subscribe("#")  # This can be further restricted, but not deleted, because otherwise no more messages will be received. "#" is a MQTT wildcard.
    logging.info("Connected to MQTT broker")
    return mqtt_client


def evaluate_heater_state(mosq, obj, msg):  # noqa when I removed it I got an error, even though it is not used

    global last_update_time
    last_update_seconds_ago = (datetime.datetime.now() - last_update_time).total_seconds()

    if last_update_seconds_ago < config.config["update_cooldown_in_seconds"]:
        return
    else:
        last_update_time = datetime.datetime.now()

    try:
        overproduction = int(msg.payload)  # value received from SMLReader, energy from photovoltaic system that is currently not used
        overproduction = -overproduction  # In fact, SMLReader/obis gives us what we draw in electricity and not what we earn
    except ValueError:
        logging.warning("Error while parsing overproduction value")
        overproduction = 0

    heater_list.sort(key=lambda x: x.power, reverse=True)  # sort heater list by power, descending

    # greedy algorithm to maximize the heater power over all heaters but still stay below the overproduction
    sum_heater_power_required = 0
    for heater in heater_list:
        if heater.pref_state:  # only turn on heaters that should be running
            if sum_heater_power_required + heater.power <= overproduction:
                sum_heater_power_required += heater.power
                heater.set_state(True)
            else:
                heater.set_state(False)  # turn off every device on this ISM channel *on every iteration* to assert dominance
        else:                            # I really don't want my house to catch fire because a neighbor used my channel
            heater.set_state(False)


if __name__ == '__main__':
    main()
