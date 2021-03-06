#!/usr/bin/env python3

import os
import socketio

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

from random import randint
from gevent import pywsgi
from flask import Flask, send_from_directory

# ==========
# APP
# ==========
debug = False # Get From Environment

# Configure Socket / App
sio = socketio.Server(logger=debug, async_mode='gevent')
app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = debug
app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)
thread = None

# Test "Device" State (On/Off)
test_device_on = False

# Socket Config
mqtt_namespace = '/mqtt'

# MQTT Config
# Use "iot.eclipse.org" for a public broker host
mqtt_broker_host = "localhost" # Get From Environment
mqtt_topics = [ ["pure/#", 0], ["test/#", 0] ]

def log(*msgs):
    if debug:
        print("<><> ", *msgs)

# ==========
# MQTT
# ==========

# MQTT Handlers
def on_message(mosq, obj, msg):
    log("incoming mqtt: {} {} {}".format(msg.topic, msg.qos, msg.payload))
    emit_message = 'test message' if msg.topic.startswith('test') else 'new message'
    sio.emit('new message', {'data': str(msg.payload.decode())}, namespace=mqtt_namespace)
    mosq.publish('pong', 'ack', 0)

def on_publish(mosq, obj, mid):
    pass

# MQTT Client
def create_mqtt_client():
    # Create Mqtt client and connect
    mqtt_client = mqtt.Client()
    mqtt_client.on_message = on_message
    mqtt_client.on_publish = on_publish

    # mqtt_client.tls_set('root.ca', certfile='c1.crt', keyfile='c1.key')
    mqtt_client.connect(mqtt_broker_host, 1883, 60)

    # Subscribe to our topics
    for topic in mqtt_topics:
        mqtt_client.subscribe(*topic)

    return mqtt_client

# ==========
# Socket IO
# ==========

# Socket Helpers
def emit_test_device_state():
    global test_device_on
    sio.emit('test device status', { 'test_device_on': test_device_on }, namespace=mqtt_namespace)

def start_background_tasks():
    global thread
    log(thread)
    if thread is None:
        thread = sio.start_background_task(background_test_thread)

# Socket IO Handlers
@sio.on('client connected', namespace=mqtt_namespace)
def connect(sid):
    emit_test_device_state()
    log('client connected...', sid)


@sio.on('client disconnected', namespace=mqtt_namespace)
def disconnect(sid):
    log('client disconnected...', sid)


@sio.on('test state change', namespace=mqtt_namespace)
def update_test_state(sid, data):
    global test_device_on
    test_device_on = data.get('test_device_on', False)
    emit_test_device_state()
    log('test data turned {}...'.format('on' if test_device_on else 'off'))


# Test thread
def background_test_thread():
    """Periodically publish random 'device' data"""
    global test_device_on
    msgs = [{'topic': "test/led", 'payload': "hello"},
            {'topic': "test/led", 'payload': "goodbye"},
            {'topic': "test/status", 'payload': "test active"}]
    while True:
        sio.sleep(1)
        if test_device_on:
            msg = randint(0, len(msgs) - 1)
            publish.single(hostname=mqtt_broker_host, **msgs[msg])

# ==========
# Flask
# ==========

# Flask Route Handlers
@app.route('/')
def index():
    start_background_tasks()
    return app.send_static_file('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.after_request
def add_header(r):
    """
    Do not cache - need index to make sure background task is started
    """
    r.headers["Cache-Control"] = "no-cache, no-store"
    return r

if __name__ == '__main__':

    # Create MQTT Client and start listening
    mqtt_client = create_mqtt_client()
    mqtt_client.loop_start()

    # Deploy with gevent - gevent allows for cross context emit events
    try:
        from geventwebsocket.handler import WebSocketHandler
        websocket = True
    except ImportError:
        websocket = False
    if websocket:
        pywsgi.WSGIServer(('', 8080), app, handler_class=WebSocketHandler).serve_forever()
    else:
        pywsgi.WSGIServer(('', 8080), app).serve_forever()
