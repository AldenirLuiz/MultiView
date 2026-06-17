import cv2
import time
import os
import numpy as np
import threading
from queue import Queue, Empty
from collections import deque

# Configuração otimizada para fluidez
DEFAULT_BUFFER_SIZE = 15  # Aumentado para melhor fluidez
FRAME_QUEUE_SIZE = 8     # Buffer de frames por fonte
TARGET_FPS = 15
FRAME_SKIP_THRESHOLD = 1.2  # Skip frame se atrasado


def _enable_hardware_acceleration(use_gpu):
    if not use_gpu:
        return False

    if hasattr(cv2, "ocl") and cv2.ocl.haveOpenCL():
        cv2.ocl.setUseOpenCL(True)
        return True

    return False


def _as_mat(frame):
    if hasattr(frame, "get"):
        return frame.get()
    return frame


class FrameReader(threading.Thread):
    """Thread para ler frames de uma fonte de vídeo continuamente"""
    def __init__(self, source, queue, is_running, on_connected=None):
        super().__init__(daemon=True)
        self.source = source
        self.queue = queue
        self.is_running = is_running
        self.cap = None
        self.last_frame = None
        self.is_connected = threading.Event()
        self.on_connected = on_connected
        self.connection_error = None
        
    def run(self):
        try:
            max_retries = 3
            retry_count = 0
            source_type = "câmera" if isinstance(self.source, int) else "arquivo/stream"
            
            while retry_count < max_retries and not self.cap:
                try:
                    print(f"  Tentativa {retry_count + 1}/{max_retries}: {self.source} ({source_type})")
                    self.cap = cv2.VideoCapture(self.source)
                    
                    # Verificar se abriu
                    if not self.cap.isOpened():
                        print(f"    → VideoCapture.isOpened() retornou False")
                        self.cap.release()
                        self.cap = None
                        retry_count += 1
                        time.sleep(0.5 * retry_count)
                        continue
                    
                    # Configurar propriedades ANTES de tentar ler
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, DEFAULT_BUFFER_SIZE)
                    self.cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)
                    
                    # Para streams RTSP, dar um tempo extra para inicializar
                    if "rtsp://" in str(self.source).lower():
                        time.sleep(1)
                    
                    # Tentar ler primeiro frame com timeout
                    frame_read_success = False
                    first_frame = None
                    
                    # Usar thread com timeout para a leitura
                    import threading as th_module
                    def read_frame():
                        nonlocal frame_read_success, first_frame
                        try:
                            ret, frame = self.cap.read()
                            if ret and frame is not None:
                                frame_read_success = True
                                first_frame = frame
                        except:
                            pass
                    
                    reader_thread = th_module.Thread(target=read_frame, daemon=True)
                    reader_thread.start()
                    reader_thread.join(timeout=5.0)  # Timeout de 5 segundos para leitura
                    
                    if not frame_read_success or first_frame is None:
                        print(f"    → Falha ao ler primeiro frame (timeout ou erro)")
                        self.cap.release()
                        self.cap = None
                        retry_count += 1
                        time.sleep(0.5 * retry_count)
                        continue
                    
                    # IMPORTANTE: Colocar frame na fila ANTES de marcar como conectado
                    frame_added = False
                    try:
                        self.queue.put(first_frame, block=True, timeout=1.0)
                        frame_added = True
                        print(f"    → Frame colocado na fila ✓")
                    except Exception as e:
                        print(f"    → ERRO ao adicionar frame à fila: {e}")
                        self.cap.release()
                        self.cap = None
                        retry_count += 1
                        continue
                    
                    if not frame_added:
                        continue
                    
                    # Sucesso - marcar como conectado DEPOIS que frame está na fila
                    self.is_connected.set()
                    self.last_frame = first_frame
                    self.connection_error = None
                    
                    if self.on_connected:
                        self.on_connected(self.source)
                    
                    print(f"  ✓ Conectado com sucesso: {self.source}")
                    break
                    
                except Exception as e:
                    self.connection_error = str(e)
                    print(f"    → Exceção: {type(e).__name__}: {e}")
                    retry_count += 1
                    if self.cap:
                        self.cap.release()
                        self.cap = None
                    time.sleep(0.5 * retry_count)
            
            if not self.cap or not self.is_connected.is_set():
                print(f"  ✗ NÃO foi possível conectar: {self.source}")
                if isinstance(self.source, int):
                    print(f"     → A câmera {self.source} não foi detectada ou não está acessível")
                else:
                    print(f"     → Arquivo/stream não encontrado ou inacessível: {self.source}")
                return
            
            # Loop principal de leitura
            print(f"  Iniciando loop de leitura para: {self.source}")
            loop_iterations = 0
            while self.is_running.is_set():
                try:
                    ret, frame = self.cap.read()
                    loop_iterations += 1
                    
                    if ret and frame is not None:
                        self.last_frame = frame
                        # Remover frames antigos da fila se estiver cheia
                        if self.queue.full():
                            try:
                                self.queue.get_nowait()
                            except Empty:
                                pass
                        try:
                            self.queue.put(frame, block=False)
                            if loop_iterations == 1:
                                print(f"    ✓ Loop de leitura ativo - frame adicionado")
                        except Exception as e:
                            print(f"    ⚠ Erro ao adicionar frame (fila cheia?): {e}")
                    elif self.last_frame is not None:
                        # Reutilizar último frame se não conseguir ler
                        try:
                            self.queue.put(self.last_frame, block=False)
                        except:
                            pass
                    
                    # Pequeno delay para não usar 100% CPU
                    time.sleep(0.001)
                except Exception as e:
                    print(f"Erro ao ler frame de {self.source}: {e}")
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"Erro fatal em FrameReader para {self.source}: {e}")
            self.connection_error = str(e)
        finally:
            if self.cap:
                self.cap.release()



def main(video_sources, screen_width, use_gpu=False, columns=2, rows=2, on_progress=None):
    """
    Reproduzir múltiplos vídeos em grid.
    on_progress: callback(message, percent) para atualizar UI durante carregamento
    """
    hardware_accel = _enable_hardware_acceleration(use_gpu)

    if use_gpu and not hardware_accel:
        print("Warning: hardware acceleration not available. Using CPU.")

    total_sources = len(video_sources)
    if total_sources == 0:
        print("Error: No video sources provided.")
        if on_progress:
            on_progress("Erro: Nenhuma fonte de vídeo fornecida", 0)
        return

    # Auto-ajustar layout
    if columns * rows < total_sources:
        columns = int(np.ceil(np.sqrt(total_sources)))
        rows = int(np.ceil(total_sources / columns))

    screen = (screen_width[0], screen_width[1])
    tile_width = int(screen[0] / columns)
    tile_height = int(screen[1] / rows)

    # Criar threads de leitura para cada fonte
    is_running = threading.Event()
    is_running.set()
    
    frame_queues = []
    reader_threads = []
    
    print(f"\n{'='*60}")
    print(f"Inicializando {total_sources} fonte(s) de vídeo")
    print(f"{'='*60}")
    for idx, src in enumerate(video_sources):
        print(f"  Fonte {idx+1}: {src}")
    print()
    
    if on_progress:
        on_progress(f"Conectando {total_sources} fonte(s) de vídeo...", 10)
    
    connected_sources = []
    def on_source_connected(source):
        connected_sources.append(source)
        percent = 10 + int((len(connected_sources) / total_sources) * 40)
        msg = f"Conectado: {len(connected_sources)}/{total_sources}"
        print(f"  {msg}")
        if on_progress:
            on_progress(msg, percent)
    
    print("\nIniciando threads de leitura...")
    for idx, src in enumerate(video_sources):
        queue = Queue(maxsize=FRAME_QUEUE_SIZE)
        frame_queues.append(queue)
        reader = FrameReader(src, queue, is_running, on_source_connected)
        reader.daemon = True
        reader.start()
        reader_threads.append(reader)
        print(f"  [{idx+1}/{total_sources}] Thread criada para: {src}")

    # Dar tempo às threads iniciarem suas tentativas de conexão
    print("\nThreads iniciadas. Aguardando primeiras respostas...")
    time.sleep(2)

    # Aguardar conexão com timeout aumentado e estratégia melhorada
    print("\nAguardando conexão das fontes...")
    
    # Detectar se há streams RTSP (que demoram mais para conectar)
    has_rtsp = any("rtsp://" in str(src).lower() for src in video_sources)
    if has_rtsp:
        max_wait = 120  # 2 minutos para streams RTSP (OpenCV timeout + retry)
        print("  ⓘ Detectado stream(s) RTSP - aguardando até 120 segundos (OpenCV timeout ~30s + retry)")
    else:
        max_wait = 30  # 30 segundos para câmeras locais/arquivos
    
    start_wait = time.time()
    check_interval = 0.3
    last_status_update = 0
    
    while time.time() - start_wait < max_wait:
        # Contar quantas fontes têm pelo menos um frame
        ready_sources = sum(1 for q in frame_queues if not q.empty())
        
        current_time = time.time() - start_wait
        
        # Atualizar status a cada 2 segundos
        if current_time - last_status_update > 2 or ready_sources > 0:
            elapsed = int(current_time)
            # Mostrar também tamanho das filas para debug
            queue_sizes = [f"{q.qsize()}" for q in frame_queues]
            print(f"  [{elapsed}s] Pronto: {ready_sources}/{total_sources} | Filas: {queue_sizes}")
            last_status_update = current_time
        
        # Critério de sucesso: pelo menos 1 fonte ou metade
        min_required = max(1, total_sources // 2)
        if ready_sources >= min_required:
            print(f"\n✓ Mínimo de fontes conectadas ({ready_sources}/{total_sources})")
            if on_progress:
                on_progress("Iniciando reprodução...", 60)
            break
        
        elapsed = time.time() - start_wait
        if on_progress and int(elapsed) % 3 == 0:  # Update UI a cada 3s
            percent = 10 + int((elapsed / max_wait) * 40)
            on_progress(f"Conectando... {ready_sources}/{total_sources}", percent)
        
        time.sleep(check_interval)
    
    # Verificar resultado final
    ready_sources = sum(1 for q in frame_queues if not q.empty())
    print(f"\nStatus final: {ready_sources}/{total_sources} fontes prontas")
    
    if ready_sources == 0:
        print("\n" + "="*60)
        print("✗ ERRO: Nenhuma fonte conseguiu conectar!")
        print("="*60)
        print("\nPossíveis causas:")
        print("  • Câmeras não conectadas ou desabilitadas no sistema")
        print("  • Arquivos de vídeo não encontrados ou com caminho incorreto")
        print("  • Streams de URL sem acesso à internet ou URL inválida")
        print("  • Permissões insuficientes para acessar os dispositivos")
        print("\nSugestões:")
        print("  1. Use 'Select Videos' para escolher arquivos locais")
        print("  2. Verifique a conexão de webcams e dispositivos de captura")
        print("  3. Teste URLs em um navegador antes de adicionar")
        print("  4. Verifique os logs acima para mais detalhes\n")
        
        if on_progress:
            on_progress("Erro: Nenhuma fonte respondeu", 100)
        is_running.clear()
        for reader in reader_threads:
            reader.join(timeout=1.0)
        return

    if on_progress:
        on_progress("Inicializando visualização...", 80)

    # Criar tile vazio (para slots sem vídeo)
    empty_tile = np.full((tile_height, tile_width, 3), 255, dtype=np.uint8)
    if hardware_accel:
        empty_tile = cv2.UMat(empty_tile)

    frame_cache = deque(maxlen=5)  # Cache de frames recentes
    frame_times = deque(maxlen=15)  # Para cálculo de FPS
    last_frame_time = time.perf_counter()
    target_wait = 100 #1000 // TARGET_FPS  # milliseconds (valores baixos faz a tela piscar se tiver atraso)
    first_frame_displayed = False

    try:
        while True:
            start_frame_time = time.perf_counter()
            frame_times.append(start_frame_time)

            # Obter últimos frames disponíveis (não bloquear)
            current_frames = []
            for i, queue in enumerate(frame_queues):
                frame = None
                try:
                    # Descartar frames antigos, pegar o mais recente
                    while not queue.empty():
                        frame = queue.get_nowait()
                    current_frames.append(frame)
                except Empty:
                    # Se fila vazia, usar frame anterior do cache se disponível
                    current_frames.append(None)  
                
            current_frames.append(frame)
            # Se todos os frames None, abortar
            """if all(f is None for f in current_frames):
                time.sleep(0.01)
                continue"""
            
            # Marcar que primeiro frame foi exibido com sucesso
            if not first_frame_displayed:
                if on_progress:
                    on_progress("Reprodução iniciada!", 100)
                first_frame_displayed = True

            # Construir grid de tiles (com resize otimizado)
            tiles = []
            total_tiles = columns * rows
            
            for i in range(total_tiles):
                if i < len(current_frames) and current_frames[i] is not None:
                    f = current_frames[i]
                    # Resize otimizado
                    if hardware_accel:
                        try:
                            tile = cv2.resize(cv2.UMat(f), (tile_width, tile_height), interpolation=cv2.INTER_LINEAR)
                        except:
                            tile = cv2.resize(f, (tile_width, tile_height), interpolation=cv2.INTER_LINEAR)
                    else:
                        tile = cv2.resize(f, (tile_width, tile_height), interpolation=cv2.INTER_LINEAR)
                else:
                    tile = empty_tile

                tiles.append(tile)

            # Concatenar tiles em paralelo (manualmente para melhor control)
            rows_tiles = []
            for row_idx in range(rows):
                start_idx = row_idx * columns
                end_idx = start_idx + columns
                row_tiles = tiles[start_idx:end_idx]
                rows_tiles.append(cv2.hconcat(row_tiles))

            combined = cv2.vconcat(rows_tiles)
            cv2.imshow('Video Stream', _as_mat(combined))

            # Controle adaptativo de FPS
            elapsed = (time.perf_counter() - start_frame_time) * 1000  # em ms
            wait_key = max(1, int(target_wait - elapsed))
            
            # Calcular FPS real
            if len(frame_times) > 1:
                fps_calc = len(frame_times) / (frame_times[-1] - frame_times[0] + 0.0001)
            else:
                fps_calc = TARGET_FPS

            # Interromper se pressionar 'q'
            if cv2.waitKey(wait_key) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário")
    except Exception as e:
        print(f"\nErro durante reprodução: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nEncerrando reprodução...")
        # Encerrar threads
        is_running.clear()
        for i, reader in enumerate(reader_threads):
            reader.join(timeout=1.0)
            if reader.is_alive():
                print(f"  Aviso: Thread {i} não respondeu ao término")
        
        cv2.destroyAllWindows()
        print("✓ Reprodução encerrada")

    return 0


if __name__ == "__main__":
    pass