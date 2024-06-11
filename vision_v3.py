"""
TO DO BEFORE START
Measure size of carrito
Ajust RGB ranges

Created by. Cesar Ponce, Tania Bernal, Miguel Vazquez, and Jareth Rivera
07 Sept 2024 

Vision System to analyze the movement of an object and its visibility within a system
"""
# Definion of necessary libraries
import cv2
import numpy as np
from time import sleep
import sys
from picamera2 import Picamera2
import serial
import pandas as pd

# Open communication with Arduino
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1) # Path to arduino can change if it's connected to another physical port
sleep(1)
ser.reset_input_buffer() # resets buffer connection

prim_calib = 0

# Open communication with camera module
# Additional initial configurations for camera
camera = Picamera2()
camera.preview_configuration.main.size = (900,700)
camera.preview_configuration.main.format = "RGB888"
camera.preview_configuration.align()
camera.configure("preview")
camera.start()

# Loop to run loop indefinetly 
while True:
    # Declaration and set initial values of variables
    color_pixels_sum = 0 
    visible_per = []
    cont= 0
    cont1 = 0
    cont2 = 0
    cont3 = 0
    sum_last3 = 0
    prom = []
    sum_last3_prom = 0
    score = 0
    file  = "/home/integrador/Documents/db.csv" # Path to database

    flag_calib = 0 # Flag if the calibration is complete
    flag_mano_carrito = 0 # Flag if hand covers carrito
    end_flag = 0 # Flag that program has ended
    start_flag = 0 # Flag that program has started 
    start_ardu = 0 # Flag for arduino that program has started
    prim_calib = 0 # First loop calibration

    # Function to calibrate system
    def calibrate(x_carrito,y_carrito,x_frame,y_frame,prim_calib):
        flag_carrito_x_posicion = 0
        flag_carrito_y_posicion = 0
        if prim_calib == 0: # Checks if it is the first calibration run
            diferencia_x = x_frame - x_carrito + 120
            diferencia_y = y_frame - y_carrito + 120 
            diferencia_y_mm = diferencia_y / 2.77 # Turns pixels to milimiters, changes depending of camera
            diferencia_x_mm = diferencia_x / 2.77
            diferencia_y_mm = int(diferencia_y_mm)*-5 # Adjustments to help motor receive stronger pulses
            diferencia_x_mm = int(diferencia_x_mm) *4
            diferencia_y_mm = str(diferencia_y_mm) # Integer converted to string 
            diferencia_x_mm = str(diferencia_x_mm)
            mensaje_dif = diferencia_x_mm + " " + diferencia_y_mm + "\n" # Joins message to send to arduino
            ser.write(mensaje_dif.encode("utf-8")) # Sends message to Arduino
            prim_calib = 1 # Set to true first loop is completed
            sleep(2)
        while True:
            if x_carrito not in range(x_frame - 50,x_frame + 50): # Checks if the carrito is within the X range
                flag_carrito_x_posicion = 0
            else:
                flag_carrito_x_posicion = 1
            if y_carrito not in range(y_frame - 50,y_frame + 50): # Checks if the carrito is within the Y range
                flag_carrito_y_posicion = 0
            else:
                flag_carrito_y_posicion = 1

            if flag_carrito_x_posicion == 1 & flag_carrito_y_posicion == 1: # If carrito in range, calibration is completed
                ser.write("calibrado\n".encode("utf-8"))
                return 1
            else: 
                diferencia_x = x_frame - x_carrito
                diferencia_y = y_frame - y_carrito 
                diferencia_y_mm = diferencia_y /2.77 # Turns pixels to milimiters, changes depending of camera
                diferencia_x_mm = diferencia_x /2.77
                diferencia_y_mm = int(diferencia_y_mm)*-5 # Adjustments to help motor receive stronger pulses
                diferencia_x_mm = int(diferencia_x_mm) *4
                diferencia_y_mm = str(diferencia_y_mm) # Integer converted to string 
                diferencia_x_mm = str(diferencia_x_mm)
                mensaje_dif = diferencia_x_mm + " " + diferencia_y_mm + "\n" # Joins message to send to arduino
                ser.write(mensaje_dif.encode("utf-8")) # Sends message to Arduino
                while True:
                    line = ser.readline().decode("utf-8") # Reads what Arduino sends
                    if ser.in_waiting <= 0:
                        line = ser.readline().decode("utf-8")
                        break
                    break
                sleep(2.5)
                return 0

    # Read until end of program is completed
    while True:
        im = camera.capture_array() # Image is captured
        
        dimensions = im.shape
        imaging_rgb = im
        cont1 = 0
        cont2 = 0
        sum_last3 = 0
        sum_last3_prom = 0
        
        # height, width, number of channels in image
        height = im.shape[0]
        width = im.shape[1]
        channels = im.shape[2]

        # Convert to RGB
        rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

        # Define range wanted color in RGB 
        # Red color detected
        lower_val = np.array([186,0,0]) 
        upper_val = np.array([255,100,130]) 

        # Threshold the RGB image - any red color will show up as white
        mask = cv2.inRange(rgb, lower_val, upper_val)
        #imS = cv2.resize(mask, (1000, 1000)) # Shows this mask
        #cv2.imshow('First mask',mask)

        # Sums amount of pixels detected
        try: 
            color_pixels = np.sum(mask)
            color_pixels_sum += color_pixels
            cont +=1
        except ValueError: # If error, do nothing
            pass

        # Center of working space
        # Define range wanted color in RGB   
        lower_val_frame = np.array([90,150,10]) 
        upper_val_frame = np.array([190,255,110]) # Green detected

        # Threshold the RGB image - any green color will show up as white
        mask2 = cv2.inRange(rgb, lower_val_frame, upper_val_frame)
        #im = cv2.resize(mask, (1000, 1000)) # Shows this mask
        #cv2.imshow('Second mask',mask2)

        # if there are any white pixels on mask, sum will be > 0
        if color_pixels > 0: 
            points = cv2.findNonZero(mask)
            avg = np.mean(points, axis=0)
            # calculate center of shape / well, kind of, just avergae of detected pixels 
            x = int(avg[0][0])
            y = int(avg[0][1])

            # Second mask
            points2 = cv2.findNonZero(mask2)
            avg2 = np.mean(points2, axis=0)

            # calculate center of shape / well, kind of, just avergae of detected pixels
            if avg2.ndim > 0:
                x2 = int(avg2[0][0])
                y2 = int(avg2[0][1])
            
            # Calls calibrate function if criteriaa are met
            if flag_calib == 0:
                flag_calib = calibrate(x,y,x2,y2,prim_calib)
                prim_calib = 1
                if flag_calib == 1:
                    df = pd.read_csv(file) # Reads Database
                    df._set_value(0, "value", flag_calib) # Sets value in data base
                    df.to_csv(file, index=False) # Saves new values
                    df = 0
                    sleep(3)

            # Percentage of visible carrito
            visible_per_cal = round(((color_pixels *100) / 1096955.35),2) # Size of carrito (pixels)
            visible_per.append(visible_per_cal)

            # Calculates average of visible pixels
            list_visible_per_last3 = visible_per[-12:]
            for value in list_visible_per_last3:
                sum_last3 += value 
                cont1 += 1
            prom.append(sum_last3 / cont1)

            list_prom_last3 = prom[-12:]
            for value in list_prom_last3:
                sum_last3_prom += value 
                cont2 += 1
            prom_last3 = sum_last3_prom/cont2

            df = 0
            df = pd.read_csv(file)
            if df["value"][2] == "1": # If criteria is met, set value locally
                start_flag = 1
            
            sleep(0.1)
                
            # Checks which conditions are true
            if flag_mano_carrito == 0 and flag_calib == 0: 
                pass
            elif flag_mano_carrito == 0 and flag_calib == 1:
                if 30 >= prom_last3 >= 0:
                    flag_mano_carrito = 1
                    df = pd.read_csv(file)
                    df._set_value(1, "value", flag_mano_carrito)
                    df.to_csv(file, index=False)
            elif flag_mano_carrito == 1 and flag_calib == 1 and start_flag == 1:
                if start_ardu == 0:
                    ser.write("start\n".encode("utf-8")) # Sends message to arduito that program is ready to start
                    start_ardu = 1
            
                score += visible_per_cal
                cont3 += 1 
                vel_carrito = "lento" # Initial speed
                
                # How much of the carrito is visible and sets new speed
                if prom_last3 <= 33:
                    vel_carrito = "rapido"
                elif 66 >= prom_last3 > 33:
                    vel_carrito = "medio"
                elif prom_last3 > 66:
                    vel_carrito = "lento"
                
                # Send to arduino new speed and saves it to db
                vel_carrito_ardu = vel_carrito + "\n"
                ser.write(vel_carrito_ardu.encode("utf-8"))
                df = 0
                df = pd.read_csv(file)
                df._set_value(5, "value", vel_carrito)
                df.to_csv(file, index=False)
    
            # Highlights values detected by the mask
            #cv2.circle(imaging_rgb, (x,y), radius=3, color=(0, 255, 0), thickness=3)
            #cv2.rectangle(imaging_rgb, (x2 + 50, y2 + 50), # Highlighting detected object with rectangle  "36" dimensions of car
            #           (x2 - 50, y2 - 50),   
            #           (0, 255, 0), 2)  
            #for i in range(len(points)):
            #    cv2.circle(imaging_rgb, (points[i][0][0],points[i][0][-1]), radius=1, color=(0, 255, 0), thickness=1)

            df = 0
            df = pd.read_csv(file)
            if df["value"][3] == "1": # If end flag is set, finishes program
                ser.write("fin\n".encode("utf-8"))
                puntaje = 100-(score / cont3)
                puntaje = int(round(puntaje))

                df = 0
                df = pd.read_csv(file)
                df._set_value(4, "value", puntaje)
                df.to_csv(file, index=False)
                
                sleep(17)
                break
            df = 0
        else:
            pass
        
        # Display image
        imS = cv2.resize(imaging_rgb, (1000, 1000)) # Resize image
        #cv2.imshow('Frame',imS) 
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    #find total size of carrito
    # average_pix_area = color_pixels_sum/cont
    # print(average_pix_area)
    ser.close()
    cv2.destroyAllWindows() # Closes all open windows