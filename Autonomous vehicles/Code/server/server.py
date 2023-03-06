import sys, time, threading, logging

"""
This server runs on a computer and is able to coordinate a group of robots.
The backend does some pathfinding and interacts with the REST APIs of the robots to drive them.
The front end displays the state of the robots allows the user to communicate with them.
"""

# Web interface
from flask import Flask, Response, request
from flask import render_template, make_response, send_from_directory,send_file

import navigation
import cv2
import pathfinding
import requests

raspi_url = "192.168.137.62:5000"

current_pos = [0,0]

def startup():
    navigation.update_minimap(1,1)

class CustomFlaskApp(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
            with self.app_context():
                startup()
        super(CustomFlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


app = CustomFlaskApp(__name__)



@app.route("/static/<path:path>")
def fstatic(path):
    return send_from_directory('static', path)


@app.route("/minimap")
def make_minimap():
    raw_minimap = navigation.get_minimap()
    buffer = cv2.imencode(".png", raw_minimap)[1]
    response = make_response(buffer.tobytes())
    response.headers["Content-Type"] = "image/png"
    return response

@app.route("/initial_path")
def get_initial_path():
    global current_pos
    try:
        start = request.args.get('start', type=tuple)
        start = (int(start[0]),int(start[1]))
        destination = request.args.get('destination', type=tuple)
        destination = (int(destination[0]),int(destination[1]))
        path = pathfinding.initial_path(start,destination)
        path.pop(0)
        return str(path)
    except:
        return "[(0,0),(1,0),(2,0),(2,1),(2,2)]" # used for other modes

@app.route("/add_obstacle")
def add_obstacle():
    obstacle = request.args.get('obstacle', type=tuple)
    obstacle = (int(obstacle[0]),int(obstacle[1]))
    start = request.args.get('start', type=tuple)
    start = (int(start[0]),int(start[1]))
    destination = request.args.get('destination', type=tuple)
    destination = (int(destination[0]),int(destination[1]))
    path = pathfinding.add_obstacle(obstacle,start,destination)
    return str(path)


# Endpoints forwarded directly to raspi
"""
            data.speed_u = await (await fetch("/speed")).text();
            data.target_distance_u = await (await fetch("/target_distance")).text();
            data.steer_ratio_u = await (await fetch("/steer_ratio")).text();
            data.zone_top_u = await (await fetch("/zone_top")).text();
            data.zone_bottom_u = await (await fetch("/zone_bottom")).text();
            data.zone_width_u = await (await fetch("/zone_width")).text();
            data.manualp_u = await (await fetch("/manualp")).text();
            data.move_mode_u = await (await fetch("/move_mode")).text();
"""

@app.route("/auto")
def start_auto():
    start = request.args.get('start', type=tuple)
    destination = request.args.get('destination', type=tuple)
    direction = request.args.get('direction', type=str)

    sval = start[0] + start[1]
    dval = destination[0] + destination[1]

    r = requests.get("http://" + raspi_url + "/auto",params={"start":sval,"destination":dval,"direction":direction})
    return "Automatic mode started" if r.content == "ok" else "Automatic mode was already on !"    

@app.route("/abort")
def abort():
    r = requests.get("http://" + raspi_url + "/abort")
    return r.content

@app.route("/isauto")
def isauto():
    r = requests.get("http://" + raspi_url + "/isauto")
    return r.content

# Parameter control

@app.route("/speed")
def get_speed():
    r = requests.get("http://" + raspi_url + "/speed")
    return r.content
@app.route("/speed/<int:value>")
def set_speed(value):
    r = requests.get("http://" + raspi_url + "/speed/"+str(value))
    return r.content
# ---------
@app.route("/target_distance")
def get_target_distance():
    r = requests.get("http://" + raspi_url + "/target_distance")
    return r.content
@app.route("/target_distance/<int:value>")
def set_target_distance(value):
    r = requests.get("http://" + raspi_url + "/target_distance/"+str(value))
    return r.content
# ---------
@app.route("/steer_ratio")
def get_steer_ratio():
    r = requests.get("http://" + raspi_url + "/steer_ratio")
    return r.content
@app.route("/steer_ratio/<float:value>")
def set_steer_ratio(value):
    r = requests.get("http://" + raspi_url + "/steer_ratio/"+str(value))
    return r.content
# ---------
@app.route("/zone_top")
def get_zone_top():
    r = requests.get("http://" + raspi_url + "/zone_top")
    return r.content
@app.route("/zone_top/<int:value>")
def set_zone_top(value):
    r = requests.get("http://" + raspi_url + "/zone_top/"+str(value))
    return r.content
# ---------
@app.route("/zone_bottom")
def get_zone_bottom():
    r = requests.get("http://" + raspi_url + "/zone_bottom")
    return r.content
@app.route("/zone_bottom/<int:value>")
def set_zone_bottom(value):
    r = requests.get("http://" + raspi_url + "/zone_bottom/"+str(value))
    return r.content
# ---------
@app.route("/zone_width")
def get_zone_width():
    r = requests.get("http://" + raspi_url + "/zone_width")
    return r.content
@app.route("/zone_width/<int:value>")
def set_zone_width(value):
    r = requests.get("http://" + raspi_url + "/zone_width/"+str(value))
    return r.content
# ---------
@app.route("/manualp")
def get_manualp():
    r = requests.get("http://" + raspi_url + "/manualp")
    return r.content
@app.route("/manualp/<float:mode>")
def set_manualp(value):
    r = requests.get("http://" + raspi_url + "/manualp/"+str(value))
    return r.content
# -------

@app.route("/leave_circuit")
def get_leave_circuit():
    r = requests.get("http://" + raspi_url + "/leave_circuit")
    return r.content

@app.route("/leave_circuit/<int:value>")
def set_leave_circuit(value):
    r = requests.get("http://" + raspi_url + "/leave_circuit/"+str(value))
    return r.content


@app.route("/mode")
def get_mode():
    r = requests.get("http://" + raspi_url + "/mode")
    return r.content
@app.route("/mode/<int:value>")
def set_mode(value):
    r = requests.get("http://" + raspi_url + "/mode/"+str(value))
    return r.content


# Classic movement

@app.route("/left")
def go_left():
    r = requests.get("http://" + raspi_url + "/left")
    return r.content
@app.route("/right")
def go_right():
    r = requests.get("http://" + raspi_url + "/right")
    return r.content
@app.route("/forward")
def go_forward():
    r = requests.get("http://" + raspi_url + "/forward")
    return r.content
@app.route("/backward")
def go_backward():
    r = requests.get("http://" + raspi_url + "/backward")
    return r.content



# Control endpoints

@app.route("/ip/")
def get_ip(value):
    global raspi_url
    return raspi_url

@app.route("/set_ip/<value>")
def set_ip(value):
    global raspi_url
    # attempt to connect:
    raspi_url = value
    try:
        r = requests.get("http://" + raspi_url + "/",timeout=1)
        print(r)
        if r.status_code == 200:
            raspi_url = value
            return "ok"
    except Exception:
        pass

    return "not ok"

@app.route("/")
def index():
    return send_file('static/index.html')


if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",use_reloader=True)
