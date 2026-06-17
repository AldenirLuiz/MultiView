import cv2
import time
import os
import numpy as np
DEFAULT_BUFER_SIZE = 1

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



def main(video_sources, screen_width, use_gpu=False, columns=2, rows=2):
    # Open a VideoCapture for each source (file path or device index)
    caps = [cv2.VideoCapture(src) for src in video_sources]

    hardware_accel = _enable_hardware_acceleration(use_gpu)

    if use_gpu and not hardware_accel:
        print("Warning: hardware acceleration requested, but OpenCL is not available. Falling back to CPU.")

    if not any(cap.isOpened() for cap in caps):
        print("Error: None of the video sources could be opened.")
        for cap in caps:
            cap.release()
        return

    total_sources = len(video_sources)
    if total_sources > 0 and columns * rows < total_sources:
        columns = int(np.ceil(np.sqrt(total_sources)))
        rows = int(np.ceil(total_sources / columns))

    # Determine a reasonable FPS from the first opened capture
    fps = 30
    for cap in caps:
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_BUFFERSIZE, DEFAULT_BUFER_SIZE)
            framerate = cap.get(cv2.CAP_PROP_FPS)
            if framerate and framerate > 0:
                fps = framerate
            print(f"Using FPS: {fps} from source")
            break
    wait_time = 1.0 / fps if fps > 0 else 1.0 / 30

    while True:
        start = time.perf_counter()
        frames = []
        screen = (screen_width[0], screen_width[1])
        

        for cap, src in zip(caps, video_sources):
            if not cap.isOpened():
                frames.append(None)
                continue

            ret, frame = cap.read()
            if not ret or frame is None:
                # Fallback: if path exists and is an image, try imread once
                if os.path.isfile(src):
                    img = cv2.imread(src)
                    frame = img
                else:
                    frame = None
            frames.append(frame)

        # If all frames are None, stop
        if all(f is None for f in frames):
            print("Error: no frames available from any source. Exiting.")
            break

        total_tiles = columns * rows
        while len(frames) < total_tiles:
            frames.append(None)

        def to_tile(f):
            screen_width = screen[0] / columns
            screen_height = screen[1] / rows
            tile_width = int(screen_width)
            tile_height = int(screen_height)

            if f is None:
                tile = np.full((tile_height, tile_width, 3), 255, dtype=np.uint8)
                return cv2.UMat(tile) if hardware_accel else tile

            if hardware_accel:
                return cv2.resize(cv2.UMat(f), (tile_width, tile_height))

            return cv2.resize(f, (tile_width, tile_height))

        tiles = [to_tile(frames[i]) for i in range(total_tiles)]

        rows_tiles = []
        for row_idx in range(rows):
            start_idx = row_idx * columns
            end_idx = start_idx + columns
            row_tiles = tiles[start_idx:end_idx]
            rows_tiles.append(cv2.hconcat(row_tiles))

        combined = cv2.vconcat(rows_tiles)

        cv2.imshow('Video Stream', _as_mat(combined))

        # Maintain approximate framerate
        progress = (time.perf_counter() - start)
        sleep_time = max(0, wait_time - progress)
        time.sleep(sleep_time)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    for cap in caps:
        cap.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    pass