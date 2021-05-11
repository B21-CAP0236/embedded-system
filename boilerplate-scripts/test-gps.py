# Amazing blogpost regarding the gps output documentation
# https://www.engineersgarage.com/microcontroller-projects/articles-raspberry-pi-neo-6m-gps-module-interfacing/

import sys
import serial
import webbrowser

ser = serial.Serial("/dev/ttyS0")
gpgga_info = "$GPGGA,"
GPGGA_buffer = 0
NMEA_buff = 0
GPGGA_data_available = ""

def convert_to_degrees(raw_value):
    decimal_value = raw_value/100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value))/0.6
    position = degrees + mm_mmmm
    position = "%.4f" %(position)
    return position

received_data = (str)(ser.read(200))
GPGGA_data_available = received_data.find(gpgga_info)

if (GPGGA_data_available>0):
    GPGGA_buffer = received_data.split(gpgga_info,1)[1]
    NMEA_buff = (GPGGA_buffer.split(','))
    nmea_time = []
    nmea_latitude = []
    nmea_longitude = []
    nmea_time = NMEA_buff[0]
    nmea_latitude = NMEA_buff[1]
    nmea_longitude = NMEA_buff[3]

    print("NMEA Time: ", nmea_time,'\n')

    lat = (float)(nmea_latitude)
    lat = convert_to_degrees(lat)
    longi = (float)(nmea_longitude)
    longi = convert_to_degrees(longi)

    print ("NMEA Latitude:", lat,"NMEA Longitude:", longi,'\n')

    map_link = 'http://maps.google.com/?q=' + lat + ',' + longi
    webbrowser.open(map_link)

sys.exit(0)
