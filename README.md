# MultiView - Visualizador de Múltiplas Câmeras/Vídeos

## 🎯 Funcionalidades

- **Visualização de múltiplas câmeras simultaneamente** em grid automático
- **Suporte para:**
  - Câmeras IP (RTSP)
  - Arquivo de vídeo local (MP4, AVI, MKV, MOV)
  - Streams de URL
  - Webcam do sistema (índice 0)
- **Aceleração de hardware** (GPU/OpenCL opcional)
- **Tela de carregamento** com barra de progresso
- **Detecção automática** de tipo de fonte e timeout adaptativo

## 🚀 Como Usar

### Opção 1: Via Script (Recomendado)
```bash
run.bat
```

### Opção 2: Via Terminal
```bash
python mainWindow.py
```

## 📋 Interface

### Botões Principais

1. **Open URLs** - Conecta às câmeras/streams definidas no `urls.json`
2. **Select Videos** - Escolher arquivos de vídeo local
3. **Use Webcam** - Conectar à webcam do sistema (índice 0)
4. **Load URLs** - Carregar URLs de arquivo JSON
5. **Save to urls.json** - Salvar URLs padrão

### Indicadores

- **Conectado: X/Y** - Quantas câmeras conectaram (durante carregamento)
- **Pronto: X/Y** - Quantas câmeras têm frames sendo capturados
- **Filas: [...]** - Tamanho das filas de cada câmera (debug)

## ⚙️ Configuração

### Arquivo `urls.json`

Define as câmeras/streams padrão:

```json
[
  "rtsp://user:pass@192.168.0.2:554/cam/realmonitor?channel=1&subtype=1",
  "rtsp://user:pass@192.168.0.2:554/cam/realmonitor?channel=2&subtype=1",
  "/local/video.mp4",
  "0"
]
```

- Strings com `rtsp://` = câmera IP
- Caminho de arquivo = vídeo local
- Número inteiro = índice de câmera (0 = webcam)

## 🔧 Características Técnicas

### Threading Inteligente
- Cada câmera roda em thread separada
- Não bloqueia a UI durante conexão

### Retry Automático
- 3 tentativas por câmera
- Backoff exponencial (0.5s, 1s, 1.5s)
- Timeout adaptativo:
  - 30s para câmeras locais/arquivos
  - 120s para streams RTSP (OpenCV timeout + retry)

### Filas Otimizadas
- Buffer: 15 frames no driver OpenCV
- Aplicação: 8 frames por câmera
- Descarta frames antigos automaticamente
- Nunca bloqueia em espera

### Reprodução Fluida
- Frames não lêem em ordem fixa
- Sempre pega frame mais recente
- Reutiliza anterior se falhar
- FPS adaptativo (30 padrão)

## 📊 Saída de Debug

Quando conecta às câmeras, você verá:

```
============================================================
Inicializando 8 fonte(s) de vídeo
============================================================
  Fonte 1: rtsp://...channel=1...
  Fonte 2: rtsp://...channel=2...
  ...

Iniciando threads de leitura...
  [1/8] Thread criada para: rtsp://...channel=1...
  [2/8] Thread criada para: rtsp://...channel=2...
  ...

Aguardando conexão das fontes...
  ⓘ Detectado stream(s) RTSP - aguardando até 120 segundos
  Conectado: 1/8
  Conectado: 2/8
  ...
  [2s] Pronto: 0/8 | Filas: ['0', '0', ...]
  [4s] Pronto: 1/8 | Filas: ['0', '8', ...]
  ...
✓ Mínimo de fontes conectadas (4/8)
```

## 🛠️ Solução de Problemas

### "Nenhuma fonte respondeu"
- Câmeras estão offline
- IP incorreto ou fora da rede
- Credenciais (user/pass) erradas
- Firewall bloqueando conexão

**Solução:**
1. Verificar endereço IP: `ping 192.168.0.2`
2. Acessar câmera no navegador: `http://192.168.0.2`
3. Verificar credenciais
4. Use "Select Videos" para testar com arquivo local

### "Stream timeout triggered"
Esperado para RTSP - OpenCV aguarda até 30s por câmera
- 120s total com 3 tentativas + retry

### Baixo FPS / Travamentos
- Verificar conexão de rede
- Reduzir resolução das câmeras
- Aumentar buffer: modificar `DEFAULT_BUFFER_SIZE` em main.py

## 📝 Arquivo de Log

Os logs aparecem no terminal/console durante execução.

Para salvar logs em arquivo:
```bash
python mainWindow.py > log.txt 2>&1
```

## 🎨 Aceleração de Hardware

Marque "Use Hardware Acceleration (GPU/OpenCL)" para:
- Resize de imagens via GPU
- Processamento mais rápido

Funciona se seu sistema tem OpenCL disponível.

## ⌨️ Atalhos

- **Q** - Sair da reprodução (voltar à UI)
- **Ctrl+C** - Encerrar aplicação

## 📦 Dependências

- `opencv-python` (cv2)
- `tkinter` (incluso com Python)

Instalar:
```bash
pip install opencv-python
```

## 🔄 Versão & Histórico

**v1.0** - Inicial
- Threading paralelo para múltiplas câmeras
- Retry automático com backoff
- Tela de loading interativa
- Detecção automática de tipo de fonte
- Suporte a câmeras IP, vídeos e webcam

---

**Criado:** Junho 2026
**Autor:** MultiView Team
