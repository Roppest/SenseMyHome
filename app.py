# TODO: Find a way to stop the loop or allow the app to continue working under a while(True)
# Think og a way Arduino can send an urgent message to the App in Alert mode
# Create Alert mode

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
from tkinter import messagebox
import os

root = tk.Tk()
def doorTest():
    """
    Reads door sensors from Arduino board connected to app.

    Returns:
    (int): Sensor read.
    """
    door_sensor = board.get_pin('a:0:i')
    time.sleep(0.100)
    piezo = 0
    while(True):
        piezo = door_sensor.read()
        print('Door: ',int(piezo*1000))
        time.sleep(0.250)

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
        #board.analog[0].enable_reporting()
        print('Connected to: ',board)
        return board

    except:
        print("ERROR: No device was found at ",src)
        print("Make sure the decive is connected or the right port is selected.")
        input_txt = input("Reload? [Y/N]: ")
        if(input_txt.lower()[0] == 'y'):
            return arduinoConnect()
        else:
            exit()

canvas = tk.Canvas(root,height=500,width=450,bg='#85ff9e')
canvas.pack()

frame = tk.Frame(root,bg = '#141414')
frame.place(relwidth = 1, relheight= 0.85,relx = 0, rely=0.15)

startButton = tk.Button(root,text="Door", command=doorTest)
startButton.pack()
stopButton = tk.Button(root,text="Window")
stopButton.pack()
board = arduinoConnect()

root.mainloop()
