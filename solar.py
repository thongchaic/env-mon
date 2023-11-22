import os 
import time 
import network
import random
from machine import Pin, SoftSPI, ADC, SoftI2C 
from sdcard import SDCard 
from dht import DHT22  
from bh1750 import BH1750
import webrepl
class EvnMon:
    def __init__(self):
        help('modules')
        
        #self.wifi_con("PNHome2","st11ae58*")
        #webrepl.start(password="good2cu")

        self.dht=None
        self.soil=None 
        self.lux=None 
        #22000  42000
        self.vmin=23000 #
        self.vmax=45000 #

        sd=self.init_sdcard()
        ss=self.init_sensors()
        
        self.init_failed =  sd and ss
        print(sd,ss,self.init_failed)
           
    def init_sdcard(self):
        # MISO    ->  13
        # MOSI    ->  12
        # SCK     ->  14
        # CS      ->  27
        # VCC     ->  5.2v 
        # GND     ->  GND
        try:
            spi = SoftSPI(-1,miso=Pin(13),mosi=Pin(12),sck=Pin(14))
            sd = SDCard(spi, Pin(27))
            vfs = os.VfsFat(sd)
            os.mount(vfs,'/sd')
            return True 
        except:
            return False 

    def init_sensors(self):
        
        try:
            #DTH22  ->  26 
            self.dht = DHT22(Pin(26))

            #Soil   ->  32 
            self.soil = ADC(Pin(32,Pin.IN))
            self.soil.atten(ADC.ATTN_11DB)
            #SoftI2C
            #SCL    ->  25 
            #SDA    ->  33 (DAT)
            #ADDR   ->  GND
            i2c = SoftI2C(scl=Pin(25), sda=Pin(33))
            self.lux = BH1750(i2c)

            return True
        except:
            return False 

    def init_warn(self):
        #Warn   ->  2

        err_led = Pin(2,Pin.OUT)
        while True:
            err_led.value( not err_led.value() )
            time.sleep(0.2)
    
    def read_dht(self):
        try:
            self.dht.measure()
            return self.dht.temperature(), self.dht.humidity()
        except:
           return None, None 

    def read_soil(self):
        try:
            uvolt=self.soil.read_u16()

            if uvolt > 45000:
                uvolt = uvolt+(uvolt%45000)
           
            self.vmax=uvolt if uvolt>self.vmax else self.vmax
            self.vmin=uvolt if uvolt<self.vmin else self.vmin
            normalized = (uvolt-self.vmin)/(self.vmax-self.vmin)
            percentage=100-(normalized*100)
            #print("=>",uvolt,self.vmin,self.vmax,normalized,percent)
            return uvolt, percentage #read a raw analog value (0-65535) / raw ADC value 12-bit resolution (0-4095)
            #return self.soil.read_uv() # micro volt 
        except:
            return None, None 
    
    def read_lux(self):
        try:
            return self.lux.luminance(BH1750.ONCE_HIRES_1)
        except:
            return None 

    def wifi_con(self,ssid,passwd):
        wlan=network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid,passwd)
        while not wlan.isconnected():
            print(".", end="")
            time.sleep(1)
        print("IP:",wlan.ifconfig())
    
    def log(self,temp,humid, uvolt, percentage, lux):
        try:
            line = str(temp)+","+str(humid)+","+str(uvolt)+","+str(percentage)+","+str(lux)
            #print(line)
            f=open('/sd/data.csv','a')
            f.write(line+"\n")
            f.close()
        except:
            print("write data failed...")
            time.sleep(1)

    def main(self):
        if not self.init_failed:
            self.init_warn()
            return 

        #n=10
        while True:
            temp, humid = self.read_dht()
            uvolt, percentage = self.read_soil()
            lux = self.read_lux()
            #print(temp, humid,uvolt, percentage, lux, self.vmin,self.vmax, sep="\t")
            self.log( temp, humid, uvolt, percentage, lux)
            #print(".",end="")
            time.sleep(1)
            #n=n-1 
        #print("..end..")

if __name__ == '__main__':
    env = EvnMon()
    env.main()
