#PLEASE NOTE THE FOLLOWING
# ­> three hash symbols (###) indicates a description of the code's function
# while five hash symbols (#####) indicates areas where there is some ambiguity
# and/or future work is/may be needed.
# ­> new sections are devided by three long lines of has sybols followed by
# three rows of hash symbols followed by the section header.
####################
####################
####################
#SETUP SECTION
from threading import Lock
from threading import Thread
import time
import datetime
import json
import Queue
import adafruitbbio.GPIO as GPIO
import adafruitbbio.ADC as ADC
import MySQLdb

### ­­>SET DATA PARAMETERS
### (see data management section for more details)

data_logging_interval = 10 #how often a data point is logged(seconds)
data_storage_interval = 100 #how often data is stored(seconds)
data_upload_interval = 1000 #how often an attempt is made to upload data to the database(seconds)

### ­­>LOAD SETTINGS
### The config.json file contains all
### of the user generated
### settings for the program. It is
### created and stored on the web server
### using an html form based interface.
### the format of the config file is
### described in the documentation

##### the file is first updated by uploading
##### it from the database using the get_config module
##### this is so that changes can be
##### made intermittently to the configuration, however
##### a better mechanism for updating the json.config file is desired.

import get_config
with open('json.config') as json_data:
config = json.loads(json_data)

### ­­>SET UP SYSTEM PORTS
### set up ports for IO and ADC funtionality
### according to the config dictionary
### using adafruit GPIO and ADC libraries

for i in config['sensors']:
ADC.SETUP(i['pin'])

for i in config['rc_relays']:
GPIO.SETUP(i['pin'],'OUTPUT')

for i in config['dc_relays']:
GPIO.SETUP(i['pin'],'OUTPUT')

### ­­>INITIALIZE LOCK OBJECTS
### lock objects used to keep multiple threads from
### accessing the same variable simultaneously

sensor_lock = Lock()
rc_relay_lock = Lock()
dc_relay_lock = Lock()
meter_lock = Lock()
file_io_lock = Lock()

### ­­>SET UP CLASSES

### the sensor class

class sensor:
def __init__(self, id, name, type, pin):
##### the means of calculating or getting the sensor values is unclear
##### since the external hardware has not yet been designed.
##### the most likely scenarios are a value derived from the
##### adc reading on the corresponding pin or a value retreived
##### using serial communication with an external device

def self.get_reading(): ### get the raw ADC value from the sensor

def self.get_value(): ### convert the

# the relay class

class rc_relay:

def __init__(self, id, name, pin, min_on_time, min_off_time, max_off_time, sensor_max ,sensor_min):

self.name = name

self.id = id

self.type = type

self.pin = pin

self.min_on_time = min_on_time

self.min_off_time = min_off_time

self.last_on_time = time.time() ### the time the relay was last turned on

self.last_off_time = time.time() ### the time that the relay was last turned off

self.is_on = True

self.sensor = sensor ### this variable refers to an actual sensor object.

self.sensor_max = sensor_max

self.sensor_min = sensor_min

self.max_off_time = max_off_time

def can_turn_off(self): ### returns true if conditions are met for turning the relay off

with sensor_lock:

if time.time() ­ self.last_on_time() > self.min_off_time and sensor_value < self.sensor_max and

sensor_value = self.sensor.get_value()

sensor_value > self.sensor_min:

else:

return True

return False

def can_turn_on(self):

if time.time() ­ self.last_off_time > self.min_off_time:

else:

return True

return False

def turn_on(self): ### turn relay on if it can be turned on

self.on_time = time.time()

self.is_on = True

def turn_on_if_necessary(self): ### turn relay on if it has to be on else return false

with sensor_lock:

self.sensor_max or sensor_value < self.sensor_min:

sensor_value = self.sensor.value

if self.can_turn_on() and time.time­self.last_off_time > self.max_off_time or sensor_value >

GPIO.write(self.pin,GPIO.LOW)

self.on_time = time.time()

self.is_on = True

else:

return False

def turn_off(self): ### return true and turn relay off if it can be turned off else return false

if self.can_turn_off:

else:

GPIO.write(self.pin,GPIO.HIGH)

self.off_time = time.time()

self.is_on = False

return True

return False

class dc_relay:

def __init__(self, id, name, pin, time_spent_on, time_spent_off):

self.name = name

self.id = id

self.pin = pin

self.min_off_time = min_off_time

self.last_on_time = time.time()### the time the relay was last turned off

self.last_off_time = time.time() ### the time the relay was last turned on

self.is_on = True

self.time_spent_on = time_spent_on

self.time_spent_off = time_spent_off

### turn the relay off if it has exceeded its designated on time and visa versa

def cycle(self):

if self.is_on and time.time()­self.on_time > self.time_spent_on:

if not self.is_on and time.time() ­ self.off_time > self.time_spent_off:

GPIO.write(self.pin,GPIO.HIGH)

self.is_on = False

GPIO.write(self.pin,GPIO.LOW)

self.is_on = True

### energy meter class

##### as with the sensors, the methods, and parameters of the meter are largely undetermined

##### because the hardware is not yet decided upon.

##### the get_value method will return kw and kwh readings

class energy_meter:

def __init__(self):

def get_value(self):

### ­­>SET UP RELAY AND SENSOR OBJECTS

### sensor, rc relay and dc relay are created

### using the and stored in arrays.

sensors = []

for i in config['sensors']:

id = i

name = i['name']

the_type = i['type']

pin = i['pin']

sensors.append(sensor(id,name,type,pin))

sensor_length = len(sensors)

### for loop to create array of relay objects

rc_relays = []

for i in config['rc_relays']:

id = i

name = i['name']

pin = i['pin']

min_on_time = i['min_on_time']

min_off_time = i['min_off_time']

max_off_time = i['max_off_time']

sensor = i['sensor']

## the sensor variable references

## a sesor object that is correlated

## with the corresponding relay

sensor = sensors[int(i['sensor'])]

rc_relays.append(rc_relay(id,name,type,pin,min_off_time,min_on_time,max_off_time,sensor))

rc_relay_length = len(rc_relays)

dc_relays = []

if config['dc_relays']:

for i in config['dc_relays']:

id = i

name = i['name']

pin = i['pin']

on_time = i['min_on_time']

off_time = i['min_off_time']

dc_relays.append(dc_relay(id,name,type,pin,min_off_time,min_on_time,max_off_time,sensor))

dc_relay_length = len(dc_relays)

#SETUP SECTION

####################

####################

####################

#MAIN SECTION

peak_times = config['utility_profile']['peak_times']

peak_days = config['utility_profile']['peak_days']

holidays = config['utility_profile']['holidays']

set_points = config['set_points']

read_day = config['utility_profile']['read_day']

### is_on_peak():

### check the current time and date against the utility rate schedule

### and return true if it is an on peak time, and false otherwise

def is_on_peak(peak_days = peak_days, holidays = holidays,peak_times = peak_times):

if not peak_days[weekday]:

return False

for i in holidays:

the_date = time.strftime('%m/%d')

if i == the_date:

weekday = datetime.datetime.now().today().weekday()

return False

the_time = time.strftime('%H')

if the_time < peak_times[0] and the_time > peak_times[1]:

return True

return False

### get_set_point(): return the setpoint for the current month,

### as specified in the config dictionary. If the day of the month is

### on or before the utility read day, return the lesser of the two

### between this month's and the last months's set points

def get_set_point(set_points=set_points):

month = 3 #datetime.datetime.now().today().month

day = 1 #datetime.datetime.now().today().day

last_month = (month­1)%12

if day < read_day:

if set_points[1] < set_points[2]:

else:

else:

return set_points[month]

### cycle_loads(): iterate through all of the rc_relays starting with the

### current_cycle parameter. turn off the first relay that is on and can be

### turned off and return true, or return false if there are no such relays

def cycle_loads(current_cycle,rc_relay_length=rc_relay_length):

for i in range(rc_relay_length):

return set_points[month]

return set_points[last_month]

current = (count+current_cycle) % rc_relay_length

with rc_relay_lock:

this_relay = rc_relays[current]

if this_relay.is_on

return False

### turn_on_loads_if_necessary():

### iterate through all of the rc_relays and turn them on if they are required to be on

def turn_on_loads_if_necessary(rc_relay_length=rc_relay_length):

for i in range(rc_relay_length):

with rc_relay_lock:

rc_relays[i].turn_on_if_necessary()

def turn_on_all_loads(rc_relay_length=rc_relay_length):

for i in range(rc_relay_length):

with rc_relay_lock:

rc_relays[i].turn_on_if_necessary()

### duty_cycles(): execute the duty cycles

def duty_cycles(dc_relay_length=dc_relay_length):

for i in range(dc_relay_length):

with dc_relay_lock:

dc_relays[i].cycle()

### main_loop(): this is the core function in the program.

### during on peak hours, call turn_on_loads() and dtuty_cycles() continuously

### and turn off loads or call cycle loads()

### during off peak hours, turn everything on as soon as it can be safely turned on

### and call duty_cycles continuously

def main_loop(current_cycle=0, rc_relay_length=rc_relay_length):

while True:

while is_on_peak():

turn_on_loads_if_necessary()

duty_cyles()

set_point = get_set_point()

with meter_lock:

kw,kwh = get_kw()

if kwh > set_point and time.time()­last_turn_off > 30:

if cycle_loads(current_cycle)

current_cycle = (current_cycle + 1) % rc_relay_length

last_turn_off = time.time()

####################

####################

####################

#DATA RECORDING SECTION

### a queue object for safely passing data between threads

data_queue = Queue.Queue()

### get data:

### create a list (data_point) which containa all of the relevant data in order

### and put the data point into the data_queue object

def

put_data_point(sensor_length=sensor_length,rc_relay_length=rc_relay_length,dc_relay_length=dc_relay_length):

now = {}

data_point =[]

data_point.append(time.strftime('%m/%d/%y'))#current date

data_point.append(time.time())#current time

for i in range(sensor_length):

with sensor_lock:

data_point.append(sensors[i].get_value())

for i in range(rc_relays_length):

with rc_relay_lock:

data_point.append(rc_relays[i].is_on)

for i in range(dc_relays_length):

with dc_relay_lock:

data_point.append(dc_relays[i].is_on)

kw,kwh = get_kw()

data.append(kwh)

data.append(kw)

data_queue.put(data)

### record_data(): create a new data point every 'data_logging_interval'

def record_data(data_logging_interval = data_logging_interval):

while True:

time.sleep(data_logging_interval)

get_data()

def new_file(data):

with file_io_lock:

filename = 'upload/'+time.time() + '.json'

with open(filename, 'w+') as outfile:

json.dump(data,outfile)

### store_data(): pop all data points from data_queue object and store in

### a json file in the upload folder every 'data_sotrage_interval'

def store_data(data_storage_interval = config['data_storage_interval']):

while True:

time.sleep(data_storage_interval)

data={}

while not data_queue.empty:

new_file(data)

print time.strftime('%H:%M')

### ­­>START MYSQL QUERY

table = 'customer_data_1'

query_rows = "(date, time, "

data.update = data_queue.get()

for i in config['sensors']:

query_rows += i['name'] + ", "

for i in config['rc_relays']:

query_rows += i['name'] + ", "

if config['dc_relays']:

for i in config['dc_relays']:

query_rows += i['name'] + ", "

query_rows +="kwh, kw)"

query_start = "INSERT INTO " + table + " " + query_rows + " VALUES "

### upload_file(filename): load a json file (filename) into a python dictionary,

### turn it into a MySQL query, and attempt submit query to the database.

### return true if upload is successful, else return false

def upload_file(filename,query=query_start):

host = XXXX

user = XXXX

password = XXXX

database = XXXX

with open(filename) as json_data:

data = json.load(json_data)

for i in data:

query += "("

for j in i:

query += "***"

query = query.replace(',***','')

query += "), "

query += '***'

query = query.replace(', ***','')

try:

db = MySQLdb.connect(host,user,password,database)

cur = db.cursor()

cur.execute(query)

db.commit()

except:

return False

def archive_file(filename):

os.move(filename,'archive')

### upload_data(): every data_upload_interval, attempt to upload each file to the database.

### if file upload is successful, move file to archive folder.

def upload_data(data_upload_interval = data_upload_interval):

filenames = os.listdir('./upload')

for i in filenames:

if upload_file(i):

archive_file(i)

####################

####################

####################

#THREADING SECTION

##### the threads are currently set up as daemons with the main thread

##### terminating in an infinite loop. I did this for debugging purposes

##### so that I could terminate all of the threads with ctrl C. I am not sure that

##### there is a utility to this setup beyond this.

### ­­>CREATE THREAD OBJECTS

### for the energy management loop and the data record mechanism

main_loop = Thread(target = main_loop,args=())

main_cycle.daemon = True

data_logging = Thread(target = record_data,args=())

data_logging.daemon = True

data_storage = Thread(target = store_data,args=())

data_storage.daemon = True

data_upload = Thread(target = upload_data,args=())

simulate_sensors.daemon = True

### ­­>START ALL THREADS

main_loop.start()

data_logging.start()

data_storage.start()

data_upload.start()

While True:

time.sleep(1)
