from flask import Flask, request
from flask import render_template

import os
import uuid
import pychromecast
import zeroconf
import json

zconf = zeroconf.Zeroconf()
listener = pychromecast.SimpleCastListener()
browser = pychromecast.CastBrowser(listener, zconf)
browser.start_discovery()

def load_config():
    with open('config.json', 'r') if os.path.exists('config.json') else open('config.example.json', 'r') as file:
        return json.load(file)

app = Flask(__name__)

@app.route("/")
def list_chromecasts():
    return render_template('index.html', devices=browser.devices.values())

chromecasts = dict()

@app.route("/devices/<device_uuid_string>", methods=['GET', 'POST'])
def device(device_uuid_string):
    device_uuid = uuid.UUID(device_uuid_string)
    cast_info = browser.devices.get(device_uuid)
    chromecast = chromecasts.get(device_uuid)

    if chromecast is None:
        chromecast = pychromecast.get_chromecast_from_cast_info(cast_info, zconf)
        chromecasts[device_uuid] = chromecast
    
    chromecast.wait()
    media = chromecast.media_controller
    media.update_status()

    config = load_config()    
    castable_media = config.get('castable_media', {})

    action = request.form.get('action', '')
    if action == "play":
        media.play()
    elif action == "pause":
        media.pause()
    elif action == "quit":
        chromecast.quit_app()
    elif action == "rewind30s":
        media.seek(media.status.current_time - 30)
    elif action == "cast":
        media.play_media(request.form['media'], 'video/mp4')

    return render_template('device.html', media_status=vars(media.status), device=cast_info, castable_media=castable_media)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)