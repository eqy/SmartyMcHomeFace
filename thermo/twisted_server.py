import quickstart
#-*- coding: utf-8 -*-
from twisted.web import server, resource
from twisted.internet import reactor
from twisted.web.static import File
import threading
import apiclient
import time
import temp
import cgi
import relay

CONST_REFRESH_INTERVAL = 1800.0

REQUEST_COUNT = 0
T_STATE_LOCK = threading.Lock()
T_VAL = -42.0
T_DATE = "OUTATIME"
T_TARGET = 0.0
T_GTARGET = 0.0
T_ON_TIME = 0.0
T_STATE = "OFF"

def heat_on():
    relay.heat.on()
    relay.fan.on()

def heat_off():
    relay.heat.off()
    relay.fan.off()

def get_gtarget():
    try:
        current_events = quickstart.getCurrentEvents()
        time.sleep(5.0)
    except Exception as e:
        print(e)
        print(type(e))
        pass
        return get_gtarget()
    gtarget = 0.0
    for event in current_events:
        try:
            cur_gtarget = float(event.split("temp=")[-1])
            if cur_gtarget > gtarget:
                gtarget = cur_gtarget
        except ValueError:
            print("Failed to parse event: " + event)
    return gtarget

def thermostat_task():
    while True:
        val = temp.read_temp()[1]
        gtarget = get_gtarget() 
        T_STATE_LOCK.acquire()
        global REQUEST_COUNT
        global T_ON_TIME
        print("visit count: {0:d}".format(REQUEST_COUNT))
        print("last on: {0:f}".format(T_ON_TIME))
        global T_VAL
        global T_DATE
        global T_STATE
        global T_GTARGET
        T_GTARGET = gtarget
        T_VAL = val
        T_DATE = time.strftime("%H:%M:%S %D", time.localtime())
        if T_STATE == "OFF" and (T_VAL < T_TARGET or T_VAL < T_GTARGET):
            heat_on()
            T_STATE = "ON"
            T_ON_TIME = time.time()
        elif T_STATE == "ON" and\
       (T_VAL <= T_TARGET + 1 or T_VAL < T_GTARGET + 1):
            #refresh to prevent heater from shutting down
            if T_ON_TIME < time.time() - CONST_REFRESH_INTERVAL:
                heat_off()
                time.sleep(0.05)
                heat_on()
                T_ON_TIME = time.time()
        else:
            heat_off()
            T_STATE = "OFF"
        T_STATE_LOCK.release() 
        time.sleep(1.0)

def gen_select_list(min_t, max_t):
    output = """<select name='temp'>"""
    for i in range(min_t, max_t):
        output += """<option value='{0:d}'>{0:d}</option>""".format(i)
    output += """</select>"""
    return output

def gen_page(temperature, temperature_target, gtemperature_target,\
    select, date, state, footnote=""):
    return """<!DOCTYPE html> 
    <html>
    <center>
    <h3>WELCOME TO SMARTY MCHOMEFACE SERVER</h3> <br>
    It is currently {0:.3f}&deg;F<br>
    Temp Set to {1:.3f}&deg;F<br>
    Gtemp Set to {2:.3f}&deg;F<br>
    T_STATE = {5:s}
    <form method='POST'>
    Set Temperature: {3:s} <br>
    <input type="submit" value="SET">
    </form>
    {4:s} <br>
    <img src='static/dat_boi.gif'>
    <br> 
    <small>{6:s}</small>
    </center>

    <audio src='static/dat_boi.mp3' autoplay>
    </audio>
    </html>
            """.format(temperature, temperature_target, gtemperature_target,\
    select, date, state, footnote)
   

class TInterface(resource.Resource):
    isLeaf = True
    
    def render_GET(self, request):
        t = temp.read_temp()[1] 
        global REQUEST_COUNT 
        T_STATE_LOCK.acquire()
        temperature = T_VAL
        temperature_target = T_TARGET
        gtemperature_target = T_GTARGET
        date = T_DATE
        REQUEST_COUNT += 1
        state = T_STATE
        T_STATE_LOCK.release()
        select = gen_select_list(50, 69)
        return gen_page(temperature, temperature_target, gtemperature_target,\
        select, date, state)

    def render_POST(self, request):
        temperature_target = float(cgi.escape(request.args['temp'][0]))
        t = temp.read_temp()[1] 
        global REQUEST_COUNT 
        global T_TARGET
        T_STATE_LOCK.acquire()
        temperature = T_VAL
        T_TARGET = temperature_target
        gtemperature_target = T_GTARGET
        date = T_DATE
        REQUEST_COUNT += 1
        state = T_STATE
        T_STATE_LOCK.release()
        select = gen_select_list(50, 69)
        return gen_page(temperature, temperature_target, gtemperature_target,\
        select, date, state,\
        "Temperature just set... updates may not happen immediately.")
   
       

root = resource.Resource()
root.putChild('', TInterface())
root.putChild('static', File('static'))

T_TASK = threading.Thread(target=thermostat_task)
T_TASK.daemon = True
T_TASK.start()

site = server.Site(root)
reactor.listenTCP(8080, site)

reactor.run()
