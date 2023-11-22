import os
from machine import Pin, SoftSPI
from sdcard import SDCard 

# MISO    ->  13
# MOSI    ->  12
# SCK     ->  14
# CS      ->  27
spi = SoftSPI(-1,miso=Pin(13),mosi=Pin(12),sck=Pin(14))
sd = SDCard(spi, Pin(27))
vfs = os.VfsFat(sd)
os.mount(vfs,'/sd')
os.chdir('sd')
