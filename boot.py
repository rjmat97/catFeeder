# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
print('boot.py loaded...')

import socket, network, esp, gc, time, ntptime
from machine import Pin, PWM


tst=0
with open('servoset.txt') as f: o,c,s=f.readline().split('_')
o,c,s = int(o), int(c), float(s) #open,sleep,close
led = Pin(4, Pin.OUT)
led.value(0)
servo = PWM(Pin(5), freq=40)


esp.osdebug(None)
gc.enable()

ssid  = 'wifi_ssid'
paswd = 'wifi_password'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, paswd)

while station.isconnected() == False: pass

print('connection succeeded')
print(station.ifconfig())
led.value(0)

servo.duty(c)
def serveFood(l,o=50,c=20,s=0.5):
    servo.duty(c)
    for i in range(l):
        print(i," ====>")
        servo.duty(o)
        time.sleep(s),
        servo.duty(50)
        servo.duty(c)
        servo.duty(50)
        servo.duty(c)
        time.sleep(s)
