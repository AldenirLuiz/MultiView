#!/usr/bin/env python3
"""Script simples para testar camera e debug"""
import cv2
import time

print("Testando VideoCapture...")

# Tentar abrir camera padrão
cap = cv2.VideoCapture(0)
print(f"Camera 0 aberta: {cap.isOpened()}")

if cap.isOpened():
    print("Tentando ler primeiro frame...")
    ret, frame = cap.read()
    print(f"Leitura bem-sucedida: {ret}")
    if ret:
        print(f"Frame shape: {frame.shape}")
    cap.release()
else:
    print("Falha ao abrir camera 0")

# Tentar outras opções
for i in range(1, 4):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"\nCamera {i} disponível!")
        ret, frame = cap.read()
        if ret:
            print(f"  Frame shape: {frame.shape}")
        cap.release()
    else:
        print(f"Camera {i}: Não disponível")

print("\nTeste concluído!")
