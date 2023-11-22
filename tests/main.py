import webrepl
import os 
import time 
import network
import random
from machine import Pin, SoftSPI, ADC, SoftI2C 
from sdcard import SDCard 
from dht import DHT22  
from bh1750 import BH1750


webrepl.start(password="good2cu")


wlan=network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("PNHome2","st11ae58*")


while not wlan.isconnected():
    print(".",end="")
    time.sleep(1)

print("\n",wlan.ifconfig())

soil = ADC(Pin(32))
dht = DHT22(Pin(26))
i2c = SoftI2C(scl=Pin(25), sda=Pin(33))
lux = BH1750(i2c)
vmin = 22000
vmax = 38000

while True:
    dht.measure()
    uvolt=soil.read_u16()
    vmax=uvolt if uvolt>vmax else vmax
    vmin=uvolt if uvolt<vmin else vmin

    x = (uvolt-vmin)/(vmax-vmin)

    percent=100-(x*100)
    print(uvolt,vmin,vmax,x,percent," : ", dht.temperature(), dht.humidity(),lux.luminance(BH1750.ONCE_HIRES_1),sep="\t")#
    time.sleep(1)

