import cv2
import socket
import struct
import numpy as np
import time

print("DEBUG: client.py started")

# ========== Settings ==========
LISTEN_IP   = "0.0.0.0"
LISTEN_PORT = 9999
BUFFER_SIZE  = 65535
HEADER_STRUCT = "!IHH"   # same as server
FRAME_TIMEOUT = 5.0      # seconds, drop partial frames older than this
# ==============================

def main():
    print("DEBUG: entered main()")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_IP, LISTEN_PORT))
    # optional timeout so we can periodically prune old frames and check for 'q'
    sock.settimeout(0.5)

    header_size = struct.calcsize(HEADER_STRUCT)
    frames = {}         # frame_id -> list of packet payloads (size = total_packets)
    meta = {}           # frame_id -> (total_packets, first_recv_time)

    print("Client listening on port", LISTEN_PORT)
    print("Press 'q' in the video window to exit.")

    try:
        while True:
            try:
                packet, addr = sock.recvfrom(BUFFER_SIZE)
            except socket.timeout:
                # Prune old partial frames
                now = time.time()
                for fid, (total, ts) in list(meta.items()):
                    if now - ts > FRAME_TIMEOUT:
                        print(f"\nDropping incomplete frame {fid} (timeout).")
                        del meta[fid]
                        del frames[fid]
                # allow cv2 window events even if no new frame
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                continue

            # parse header & payload
            header = packet[:header_size]
            payload = packet[header_size:]
            frame_id, pkt_id, total = struct.unpack(HEADER_STRUCT, header)

            # initialize structure if needed
            if frame_id not in frames:
                frames[frame_id] = [None] * total
                meta[frame_id] = (total, time.time())

            # safety: if total changed mid-stream, re-init (rare)
            if len(frames[frame_id]) != total:
                frames[frame_id] = [None] * total
                meta[frame_id] = (total, time.time())

            # store payload
            frames[frame_id][pkt_id] = payload

            # check completion
            if all(p is not None for p in frames[frame_id]):
                data = b"".join(frames[frame_id])
                nparr = np.frombuffer(data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if frame is not None:
                    cv2.imshow("UDP Stream", frame)
                else:
                    print(f"\nWarning: failed to decode frame {frame_id}")

                # cleanup
                del frames[frame_id]
                del meta[frame_id]

                # exit on 'q'
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    except KeyboardInterrupt:
        print("\nClient interrupted by user.")
    finally:
        sock.close()
        cv2.destroyAllWindows()
        print("Client stopped.")

if __name__ == "__main__":
    main()
