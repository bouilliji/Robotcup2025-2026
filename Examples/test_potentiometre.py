from grove.adc import ADC
import time

adc = ADC()

try:
    while True:
        time.sleep(0.1)
        value = adc.read(0)  # le potentiometre sur A0
        print("Valeur potenciomettre", value)
except:
    print("fin du programme")
