import threading
import time
from slcanv1 import SlcanV1
import time
slcan = SlcanV1()

# Assuming SlcanV1 and slcan are already imported/initialized in your environment
# from your_library import SlcanV1, slcan 

class CanWorker(threading.Thread):
    def __init__(self, channel_id, bitrate=500000):
        super().__init__()
        self.channel = channel_id
        self.bitrate = bitrate
        self.running = True
        self.daemon = True  # Ensures thread closes when main program exits

    def setup(self):
        """Initialize and start the specific channel."""
        print(f"[*] Initializing Channel: {self.channel}")
        slcan.open_port(self.channel)
        slcan.set_bitrate(self.bitrate, self.channel)
        slcan.start(self.channel)

    def run(self):
        """Main loop for the specific channel."""
        self.setup()
        
        counter = 0
        while self.running and counter < 10:
            # Attempt to read a frame (non-blocking or short timeout)
            frame = slcan.read_timeout(1, self.channel)
            f2 = SlcanV1.Frame()
            f2.id = 0xFF
            f2.ext = 1
            print("transmit = ", slcan.transmit_Frame(f2,self.channel))
            if frame:
                print(f"[CH {self.channel}] Received Frame ID: {hex(frame.id)}")
                
                # Create a response frame
                tx_frame = SlcanV1.Frame()
                tx_frame.id = 0x145 if self.channel == 0 else 0x14
                
                success = slcan.transmit_Frame(tx_frame, self.channel)
                print(f"[CH {self.channel}] Transmit Success: {success}")
            else:
                print(f"[CH {self.channel}] No frame received.")

            counter += 1
            time.sleep(0.1)
        
        self.cleanup()

    def cleanup(self):
        """Gracefully shut down the channel."""
        print(f"[*] Closing Channel: {self.channel}")
        slcan.stop(self.channel)
        slcan.close(self.channel)
        slcan.deinit(self.channel)

# --- Execution ---

# 1. Get available channels
channels = slcan.get_all_channels(3)

if len(channels) >= 2:
    # 2. Create threads for Channel 0 and Channel 1
    thread0 = CanWorker(channels[0])
    thread1 = CanWorker(channels[1])

    # 3. Start both threads
    thread0.start()
    thread1.start()

    # 4. Wait for both to complete
    thread0.join()
    thread1.join()

    print("Test Complete.")
else:
    print("Error: Not enough CAN channels found.")