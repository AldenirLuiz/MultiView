#!/usr/bin/env python3
"""Teste visual da tela de loading"""
from tkinter import Tk
from mainWindow import LoadingScreen
import time
import threading

# Criar janela principal
root = Tk()
root.title("Teste Loading Screen")
root.geometry("300x200")

# Criar loading
loading = LoadingScreen(root)

# Simular progresso em thread
def simular():
    for i in range(0, 101, 10):
        time.sleep(0.5)
        loading.update_progress(f"Conectando câmeras... {i}%", i)
    
    time.sleep(1)
    loading.close()
    root.quit()

thread = threading.Thread(target=simular, daemon=True)
thread.start()

root.mainloop()
print("Teste concluído!")
