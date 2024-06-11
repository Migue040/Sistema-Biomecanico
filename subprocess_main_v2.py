"""
Created by. Cesar Ponce, Tania Bernal, Miguel Vazquez, and Jareth Rivera
07 Sept 2024 

Main program to run 2 scripts simultaneously
"""
# Definion of necessary libraries
import threading
import subprocess

def run_script(script_name):
    subprocess.run(["python3", script_name]) # Set initial label to write to terminal

if __name__ == "__main__":
    script1_thread = threading.Thread(target=run_script, args=("/home/integrador/Documents/vision_v3.py",)) # Path to give ot the terminal
    script2_thread = threading.Thread(target=run_script, args=("/home/integrador/Documents/LCD_v2.py",))

    script1_thread.start()
    script2_thread.start()

    script1_thread.join()
    script2_thread.join()

    print("Both scripts have finished executing.")