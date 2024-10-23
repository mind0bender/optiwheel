import network
import socket
from time import sleep
from machine import reset, Pin

led = Pin("LED", Pin.OUT)

ssid = "mind0bender"
pswd = "IDKpassword"

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, pswd)
    while not wlan.isconnected():
        print("Waiting for connection...")
        sleep(1)
    
    ip = wlan.ifconfig()[0]
    print(f"Connected on {ip}")
    return ip

def open_socket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webpage():
    html = """	<!DOCTYPE html>
                <html>
                    <body>
                        Hi!
                        cool, huh?
                    </body>
                </html>"""
    return html

leftF = Pin(16, Pin.OUT)
leftB = Pin(17, Pin.OUT)
rightF = Pin(18, Pin.OUT)
rightB = Pin(19, Pin.OUT)

def forward():
    leftF.on()
    leftB.off()
    rightF.on()
    rightB.off()
    print("forward")

def left():
    leftF.off()
    leftB.on()
    rightF.on()
    rightB.off()
    print("left")

def right():
    leftF.on()
    leftB.off()
    rightF.off()
    rightB.on()
    print("right")

def neutral():
    leftF.on()
    leftB.on()
    rightF.on()
    rightB.on()
    print("neutral")

def serve(connection):
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        
        if request == "/neutral":
            neutral()
        elif request == "/forward":
            forward()
        elif request == "/left":
            left()
        elif request == "/right":
            right()
        else:
            print("Invalid directon!\nUnknown ACCIDENT")
            print(request)
            
        html = webpage()
        led.on()
        sleep(0.1)
        led.off()
        
        client.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        client.send(html)
        client.close()

neutral()
try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    pass
    # reset()
