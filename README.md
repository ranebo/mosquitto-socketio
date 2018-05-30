
Playing around with [MQTT](http://en.wikipedia.org/wiki/Mqtt) and [WebSockets](https://en.wikipedia.org/wiki/WebSocket) 

## Requirements
Requires [Mosquitto](http://mosquitto.org/) to be installed on your machine.

On Linux with the **apt-get** package manager:

    sudo apt-get install mosquitto
    sudo apt-get install mosquitto-clients

On Mac with the **homebrew** package manager (mosquitto will also get mosquitto-clients):

    brew install mosquitto

Also install [virtualenv](https://pypi.python.org/pypi/virtualenv) if you want to use it:

    sudo apt-get install python-virtualenv

or with pip:

    pip install virtualenv 


## Setup
The use of virtualenv is optional but recommended.

Clone this repo, setup virtualenv, and use pip to install requirements.

    git clone https://github.com/ranebo/mosquitto-socketio.git
    cd mosquitto-socketio
    virtualenv .
    source bin/activate
    pip install -r requirements.txt

If you do not have your own MQTT Broker setup you can use a public one. For example set the following in server.py:

    mqtt_broker_host = "iot.eclipse.org"


## Run
First start the server which will initialize the mqtt client:

    python server.py

Then open your browser and start the 'test' device to see data flow:

    localhost:8080

You can also send a custom message with the mosquitto-client cli tool.

    mosquitto_pub -d -h [broker host] -q 0 -t [topic] -m 'Success!'

The rest is up to you. Get connected!


## References

 * https://github.com/roppert/mosquitto-python-example
 * http://blog.yatis.io/install-secure-robust-mosquitto-mqtt-broker-aws-ubuntu/
 * https://github.com/miguelgrinberg/python-socketio
 * http://mosquitto.org/documentation/python/
 * https://pypi.python.org/pypi/paho-mqtt
