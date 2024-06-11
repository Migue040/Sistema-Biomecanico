"""
Created by. Cesar Ponce, Tania Bernal, Miguel Vazquez, and Jareth Rivera
07 Sept 2024 

LCD for "Sistema de entrenamiento"
"""
# Definion of necessary libraries
from RPLCD import CharLCD
import time
import sys
import pandas as pd
import RPi.GPIO as GPIO
from gpiozero import Buzzer
lcd = CharLCD(numbering_mode=GPIO.BOARD,cols=20, rows=4, pin_rs=37, pin_e=35, pins_data=[40, 38, 36, 32, 33, 31, 29, 23]) # Library of LCD and definition of pins
buzzer = 7
GPIO.setup(buzzer,GPIO.OUT) # Buzzer setup
while True:
    flag_calib = 0 # Flag if the calibration is complete
    flag_mano_carrito = 0 # Flag if hand covers carrito
    end_flag = 0 # Flag that program has ended
    start_flag = 0 # Flag that program has started 
    start_ardu = 0 # Flag for arduino that program has started
    vel_carrito = "lento" # Initila speed of carrito
    file  = "/home/integrador/Documents/db.csv" # Path to database

    # Writes initial values to database
    df = 0
    df = pd.read_csv(file) 
    df._set_value(0, "value", flag_calib)
    df._set_value(1, "value", flag_mano_carrito)
    df._set_value(2, "value", start_flag)
    df._set_value(3, "value", end_flag)
    df._set_value(4, "value", puntaje)
    df._set_value(5, "value", vel_carrito)
    df.to_csv(file, index=False)

    # First message and pointer to where to start to write
    lcd.cursor_pos = (2,2)
    lcd.write_string(u'Inicializando...')

    time.sleep(5)

    lcd.clear() # Clears LCD content

    # Indefinite loop
    while True: 
        while flag_calib < 1: # Waits for calibrated flag
            lcd.cursor_pos = (2,4)
            lcd.write_string(u'Calibrando...')
            time.sleep(.5)
            df = pd.read_csv(file)
            if df["value"][0] == "1": # If criteria is met, set value locally
                flag_calib = 1
            df = 0

        lcd.clear()

        while flag_mano_carrito < 1: # Waits for user to cover the carrito
            lcd.cursor_pos = (0,2)
            lcd.write_string(u'BIENVENIDO')
            lcd.cursor_pos = (1,0)
            lcd.write_string(u'Coloca tu mano sobre')
            lcd.cursor_pos = (2,0)
            lcd.write_string(u'el carrito')
            lcd.cursor_pos = (3,0)
            lcd.write_string(u'para iniciar')
            time.sleep(.5)
            df = 0
            df = pd.read_csv(file)
            if df["value"][1] == "1": # If criteria is met, set value locally
                flag_mano_carrito = 1
            
        time.sleep(1)
        lcd.clear()

        # Program about to start
        lcd.cursor_pos = (1,2)
        lcd.write_string(u'3...')
        time.sleep(1)
        lcd.cursor_pos = (1,6)
        lcd.write_string(u'2...')
        time.sleep(1)
        lcd.cursor_pos = (1,10)
        lcd.write_string(u'1...')
        time.sleep(1)
        
        start_flag = 1 # Strt flag set to true
        df = 0
        df = pd.read_csv(file)
        df._set_value(2, "value", start_flag) # Send start flag to database
        df.to_csv(file, index=False) 
        GPIO.output(buzzer,GPIO.HIGH) # Buzzer is set to on
        lcd.clear()
        lcd.cursor_pos = (1,6)
        lcd.write_string(u'INICIO!')

        for i in range(30):
            lcd.clear()
            lcd.cursor_pos = (1,2)
            lcd.write_string(u'Tiempo restante:')
            lcd.cursor_pos = (2,8)
            segg = 30 - i
            seg = str(segg)
            lcd.write_string(seg + ' segundos') # Seconds left of the program
            time.sleep(1)
            GPIO.output(buzzer,GPIO.LOW) # Buzzer is set to off

        end_flag = 1
        df = pd.read_csv(file)
        df._set_value(3, "value", end_flag) # End of program is set to true
        df.to_csv(file, index=False)
        GPIO.output(buzzer,GPIO.HIGH) # Buzzer is set to on
        time.sleep(1)
        df = 0
        df = pd.read_csv(file)
        puntaje = df["value"][4]
        puntaje_py = int(float(puntaje)) # Writes score to LCD
        puntaje_LCD = str(puntaje)
        lcd.clear()

        # Chooses message depending of score
        if puntaje_py < 50:
            lcd.cursor_pos = (1,1)
            lcd.write_string(u'Sigue practicando')
            lcd.cursor_pos = (2,6)
            lcd.write_string(puntaje_LCD + '/100')
        else:
            lcd.cursor_pos = (1,1)
            lcd.write_string(u'Bien hecho!')
            lcd.cursor_pos = (2,6)
            lcd.write_string(puntaje_LCD + '/100')

        time.sleep(1)
        GPIO.output(buzzer,GPIO.LOW)
        time.sleep(15)
        lcd.clear()
        break # Starts program loop again