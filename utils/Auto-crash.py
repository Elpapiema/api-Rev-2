# lib/auto_crash.py
import threading
import os
import time

def crash_every(interval_hours=0.5):  # 0.5 horas = 30 minutos
    def trigger_crash():
        while True:
            print(f"[auto_crash] Esperando {interval_hours} horas antes de reiniciar...")
            time.sleep(interval_hours * 3600)
            print("[auto_crash] Reiniciando servidor...")
            os._exit(1)  # Fuerza un crash para que un sistema externo lo reinicie

    t = threading.Thread(target=trigger_crash, daemon=True)
    t.start()

def register(app):
    crash_every(0.5)
