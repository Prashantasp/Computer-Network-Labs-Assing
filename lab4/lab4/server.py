import cv2
import socket
import struct
import math
import time

# ========== Settings ==========
DEST_IP   = "127.0.0.1"   # change to client IP if remote
DEST_PORT = 9999
VIDEO_SRC = "Dunes.mov"            # 0 = webcam, or "video.mp4"
PAYLOAD   = 1400          # bytes per UDP packet (safe size)
JPEG_QUALITY = 60         # 0-100
MAX_WIDTH = 640           # resize width to reduce bandwidth (set None to skip)
HEADER_STRUCT = "!IHH"    # frame_id (4 bytes), pkt_id (2 bytes), total_packets (2 bytes)
# ==============================

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest = (DEST_IP, DEST_PORT)

    cap = cv2.VideoCapture(VIDEO_SRC)
    if not cap.isOpened():
        print("Error: cannot open video source:", VIDEO_SRC)
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = 25.0
    frame_interval = 1.0 / fps

    frame_id = 0
    header_size = struct.calcsize(HEADER_STRUCT)
    chunk_size = PAYLOAD - header_size

    print("Server started, streaming to", dest)
    try:
        while True:
            start = time.time()
            ret, frame = cap.read()
            if not ret:
                print("Video ended or camera error.")
                break

            # Optional resize to cap width (keeps aspect ratio)
            if MAX_WIDTH:
                h, w = frame.shape[:2]
                if w > MAX_WIDTH:
                    scale = MAX_WIDTH / float(w)
                    frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

            # Encode as JPEG
            ok, encimg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
            if not ok:
                print("Warning: JPEG encoding failed for frame", frame_id)
                continue
            data = encimg.tobytes()

            # Split into chunks and send
            total_packets = math.ceil(len(data) / chunk_size)
            for pkt_id in range(total_packets):
                start_byte = pkt_id * chunk_size
                chunk = data[start_byte:start_byte + chunk_size]
                header = struct.pack(HEADER_STRUCT, frame_id, pkt_id, total_packets)
                sock.sendto(header + chunk, dest)

            # Debug print (one-line)
            print(f"Sent frame={frame_id} size={len(data)} bytes packets={total_packets}", end="\r")

            frame_id += 1

            # Maintain FPS
            elapsed = time.time() - start
            if elapsed < frame_interval:
                time.sleep(frame_interval - elapsed)

    except KeyboardInterrupt:
        print("\nServer interrupted by user.")
    finally:
        cap.release()
        sock.close()
        print("\nServer stopped.")

if __name__ == "__main__":
    main()
