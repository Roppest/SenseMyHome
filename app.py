# TODO:
# Fix Thread killing bug
# Work on the UI (it's horrible)
# Add temperature sensor


# ------------------------------------------------------------------------------
# DESCRIPTION
# ------------------------------------------------------------------------------
# This python app conects with an arduino board and acts as an alarm system.
# The purpose of this app is merely educational and is a work in progess
#
# This app relies on the StandardFirmata Arduino Sketch running in parallel and
# an Arduino board connected via USB.
# Rodrigo Vazquez 2020
# ------------------------------------------------------------------------------

import pyfirmata
import time
import tkinter as tk
import logging
import threading
import json
import yagmail
from email.message import EmailMessage
from tkinter import *
from tkinter.ttk import *
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
import os
from PIL import ImageTk,Image

sender_email = os.getenv('EMAIL')
receiver_email = "rodvaudio@gmail.com"
smtp_server = "smtp.gmail.com"
alarm_active = False

def arduinoConnect(src='/dev/ttyACM0'):
    """
    Connects to Arduino Board in specified port.

    Parameters:
    src (string):

    Returns:
    pyfirmata.Arduino(): Board object.
    """
    try:
        board = pyfirmata.Arduino(src)
        it = pyfirmata.util.Iterator(board)
        it.start()
        #Image errors
        #sensor_state_icon = ImageTk.PhotoImage(Image.open('img/sensorOn.png'))
        #sensor_state_label = Label(image=sensor_state_icon)
        #sensor_state_label.pack()
        print('Connected to: ',board)
        board.analog[0].enable_reporting()
        board.analog[1].enable_reporting()


        time.sleep(0.100)
        return board

    except:
        print("ERROR: No device was found at ",src)
        print("Make sure the decive is connected or the right port is selected.")
        sensor_state_icon = ImageTk.PhotoImage(Image.open('img/sensorOff.png'))
        sensor_state_label = Label(image=sensor_state_icon)
        sensor_state_label.pack()
        input_txt = input("Reload? [Y/N]: ")
        if(input_txt.lower()[0] == 'y'):
            sensor_state_label.pack_forget()
            return arduinoConnect()
    else:
        exit()

def doorRead():
    """
    Reads door sensors from Arduino board connected to app.

    Returns:
    (String): Sensor analog read.
    """
    piezo = int(door_sensor.read()*1000)
    if piezo < 10:
        return 'Low'
    elif 10 < piezo and piezo < 20:
        return 'Medium'
    else:
        return 'High'

def deactivateAlarm():
    """
    Deactivates alarm mode. The app will stop constantly reading sensor data
    """
    alarm_state.config(text='Alarm: Off')
    alarm_button.config(image=alarm_icon_off,command=setAlarm,text='')
    alarm_active = False
    #reading_thread.join()

def setAlarm(doorThreshold=20):
    """
    Activates alarm mode. The app will constantly read the sensors state
    and will sound an alarm given parameters.

    Parameters:
    doorThreshold(int): Door alarm will set off if passed.
    """

    alarm_state.config(text='Alarm: On')
    alarm_button.config(image = alarm_icon_on,command=deactivateAlarm)
    alarm_active = True
    door_label.after(150,print(doorRead()))
    reading_thread.start()

def sendEmailAlert(sensor_message):
    """
    Sends a text over email with sensor details.

    Parameters:
    sensor_message(String): Sensor details.
    """
    port = 465  # For SSL
    password = os.getenv('PASSWORD')
    email = os.getenv('EMAIL')
    message = """\
    Subject: Home Alert Notification

    Your alert detected something: """ + sensor_message
    context = ssl.create_default_context()

    yag = yagmail.SMTP(email,password)
    yag.send(
        to=receiver_email,
        subject='Home Alert Notification',
        contents=message
    )

def liveRead():
    """
    Reads sensors in arduino indifinetly, must be used with a thread so it can be
    killed.

    Returns:
    report(Dictionary): Dictionary type object with all arduino readings.
    """
    while True:
        piezo = doorRead()
        magnet = windowTest()
        time_log = datetime.now()
        window_label.config(text=magnet)
        door_label.config( text= piezo)
        if piezo == 'High' or magnet == 'Open' and alarm_active == True:
            dict = {
                'Door': piezo,
                'Window': magnet,
                'Time': str(time_log)
            }
            print(dict)

            #try:
            #    sendEmailAlert(json.dumps(dict))
            #except:
            #    print('ERROR: Error ocurred while sending mail',sys.exc_info()[0])
            sendEmailAlert(json.dumps(dict))
            deactivateAlarm()

            return dict
        time.sleep(0.150)


def windowTest():
    """
    Reads door sensors from Arduino board connected to app.

    Returns:
    (String): Window state.
    """
    result = window_sensor.read()
    if result > 0.0 :
        return 'Closed'
    else:
        return 'Open'

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Sense My Home')
    canvas = tk.Canvas(root,height=250,width=450,bg='#85ff9e')#mint
    canvas.pack()
    frame = tk.Frame(root,bg = '#141414') #black
    frame.place(relwidth = 1, relheight= 0.90,relx = 0, rely=0.10)

    #--------------------Arduino----------------------
    board = arduinoConnect()
    door_sensor = board.get_pin('a:0:i')
    window_sensor = board.get_pin('a:1:i')
    print('door_sensor:', door_sensor)
    print('window_sensor',window_sensor)
    #-------------------------------------------------

    #This thread will run in the background.
    reading_thread = threading.Thread(target=liveRead)

    Label(root,text='Door: ',font =('Verdana', 13)).pack(side=TOP)
    door_label = Label(root, text = door_sensor.read()*1000,
        font =('Verdana', 13))
    door_label.pack(side=TOP)
    Label(root,text='Window: ',font =('Verdana', 13)).pack(side=TOP)
    window_label = Label(root, text = windowTest(),
        font =('Verdana', 13))
    window_label.pack(side=TOP)

    alarm_state = Label(root, text = 'Alarm: Off',
        font =('Verdana', 15))
    alarm_state.pack(side = TOP)
    alarm_photo_off = PhotoImage(file = r"img/alarmOff.png")
    alarm_photo_on = PhotoImage(file = r"img/alarmOn.png")
    alarm_icon_off = alarm_photo_off.subsample(3,3)
    alarm_icon_on = alarm_photo_on.subsample(3,3)
    alarm_button = Button(root,text = '',
        command=setAlarm,
        image = alarm_icon_off,
        compound=LEFT)
    alarm_button.pack(side=TOP)

    windowButton = tk.Button(root,text="Door", command=print(doorRead))
    windowButton.pack()
    doorButton = tk.Button(root,text="Window",command=print(windowTest))
    doorButton.pack()

    root.mainloop()
