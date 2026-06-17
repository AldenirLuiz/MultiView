#!/usr/bin/env python3
"""Teste de diagnóstico para cameras IP"""
import cv2
import time

print("\n" + "="*60)
print("TESTE DE CONEXÃO CÂMERAS IP")
print("="*60)

urls = [
    "rtsp://aldenir:lancer007@192.168.0.2:554/cam/realmonitor?channel=1&subtype=1",
]

for url in urls:
    print(f"\nTestando: {url}")
    print("  Aguardando conexão (até 10 segundos)...", flush=True)
    
    start = time.time()
    cap = cv2.VideoCapture(url)
    
    # Tentar ler com timeout (sem atribuir propriedades não existentes)
    ret = False
    frame = None
    timeout = 10  # segundos
    
    while time.time() - start < timeout:
        ret, frame = cap.read()
        if ret:
            break
        time.sleep(0.1)
    
    if ret and frame is not None:
        print(f"  ✓ Sucesso! Frame recebido. Shape: {frame.shape}")
    else:
        elapsed = time.time() - start
        print(f"  ✗ Falha após {elapsed:.1f}s (timeout ou câmera offline)")
    
    cap.release()
    time.sleep(1)

print("\n" + "="*60)
print("DIAGNÓSTICO:")
print("  Se a câmera não respondeu, ela está:")
print("    • Offline ou desligada")
print("    • Em outro endereço IP")
print("    • Com credenciais incorretas")
print("    • Fora da rede (firewall/roteador)")
print("\nSOLUÇÃO: Use 'Select Videos' para carregar arquivos locais")
print("="*60 + "\n")
