#!/usr/bin/env python3
"""Teste direto do main() para debug"""
import sys
from main import main

print("\n" + "="*60)
print("TESTE DIRETO - Chamando main()")
print("="*60 + "\n")

# Usar as URLs do urls.json
urls = [
    "rtsp://aldenir:lancer007@192.168.0.2:554/cam/realmonitor?channel=1&subtype=1",
    "rtsp://aldenir:lancer007@192.168.0.2:554/cam/realmonitor?channel=2&subtype=1",
]

screen_width = (1920, 1080)

def on_progress(msg, percent):
    print(f"[Progress] {percent}% - {msg}")

try:
    main(urls, screen_width, use_gpu=False, columns=2, rows=1, on_progress=on_progress)
except KeyboardInterrupt:
    print("\n\nInterrompido pelo usuário")
except Exception as e:
    print(f"\nErro: {e}")
    import traceback
    traceback.print_exc()

print("\nTeste concluído")
