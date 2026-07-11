
import time
import subprocess
import sys
import ctypes
import os
import sys
# subprocess.check_call([sys.executable, "-m", "pip", "install", " python_slcanV1.zip"])

from slcanv1 import SlcanV1, SlcanV2
def test_single_channel():
    print("--- Running Single Channel Test ---")
    slcan = SlcanV1()
    
    channels = slcan.get_all_channels(3)
    if not channels:
        print("No channels found.")
        return

    port = channels[0]
    print(f"Opening port: {port}")
    
    # Initialize port
    slcan.open_port(port)
    slcan.set_bitrate(500000, port)
    slcan.start(port)

    # Transmit a frame
    f_tx = SlcanV1.Frame()
    f_tx.id = 0x01
    f_tx.ext = 1
    f_tx.dlc = 8
    print(f"Transmitting from {port} (status: {slcan.transmit_Frame(f_tx, port)})")

    # Read a frame
    print("Reading frame (timeout 1s)...")
    while(1):
        frame = slcan.read_timeout(10, port)
        if frame:
            print(f"Received frame ID: {hex(frame.id)}")
        else:
            pass
            # print("No frame received.") 

    # Cleanup
    slcan.stop(port)
    slcan.close(port)
    slcan.deinit(port)
    print("Single channel test completed.\n")


def test_multi_channel():
    print("--- Running Multi Channel Test ---")
    slcan = SlcanV1()
    
    channels = slcan.get_all_channels(3)
    if not channels or len(channels) < 2:
        print("Need at least 2 channels for multi-channel test.")
        return

    port1, port2 = channels[0], channels[1]
    print(f"Opening port 1: {port1}")
    print(f"Opening port 2: {port2}")

    # Initialize ports
    slcan.open_port(port1)
    slcan.open_port(port2)
    slcan.set_bitrate(500000, port1)
    slcan.set_bitrate(500000, port2)
    slcan.start(port1)
    slcan.start(port2)

    # Transmit using multiple channels
    f_tx = SlcanV1.Frame()
    f_tx.id = 0x145
    f_tx.dlc = 8
    
    print(f"Transmitting from {port1} (status: {slcan.transmit_Frame(f_tx, port1)})")
    print(f"Transmitting from {port2} (status: {slcan.transmit_Frame(f_tx, port2)})")

    # Read from multiple channels
    print(f"Reading from {port1}...")
    frame1 = slcan.read_timeout(1, port1)
    if frame1: print(f"Received on {port1}: {hex(frame1.id)}")

    print(f"Reading from {port2}...")
    frame2 = slcan.read_timeout(1, port2)
    if frame2: print(f"Received on {port2}: {hex(frame2.id)}")

    # Cleanup
    slcan.stop(port1)
    slcan.close(port1)
    slcan.deinit(port1)

    slcan.stop(port2)
    slcan.close(port2)
    slcan.deinit(port2)
    print("Multi channel test completed.\n")


def rx_callback(frame_ptr):
    if frame_ptr:
        f = frame_ptr.contents
        print(f.timestamp)
        print(f"    -> [Callback] Received Frame! ID: {hex(f.id)} DLC: {f.dlc}")


def test_v2_functions():
    print("--- Running V2 Functions Test ---")
    slcan = SlcanV2()
    
    # 1. Enumerate Devices using V2 function
    try:
        devices = slcan.enum_devices(10)
        if devices:
            print(f"Found {len(devices)} devices via V2 enum:")
            for d in devices:
                print(f"  Name: {d.displayName.decode('utf-8', errors='ignore')} | Path: {d.devicePath.decode('utf-8', errors='ignore')}")
        else:
            print("No devices found via V2 enum.")
            return
    except RuntimeError as e:
        print(f"V2 Enum failed (maybe slcanv2.dll not loaded): {e}")
        return

    # Use first found channel for further V2 tests
    port = devices[0].devicePath.decode('utf-8', errors='ignore')
    print(f"\nOpening port (V2 style path): {port}")
    
    # Initialization uses V1 functions for handle management
    slcan.open_port(port)
    
    # Get Device Info (V2 Function)
    info = slcan.get_device_info(port)
    if info:
        print(f"Device Info: Vendor={info.vendor.decode('utf-8', errors='ignore')}, Supports FD={info.supportsFD}")


    # Identify / blink LED (V2 Function)
    print("Blinking LED (Identify)...")
    slcan.identify(True, port)
    time.sleep(0.5)
    slcan.identify(False, port)

    slcan.set_bitrate_advanced(0, 2, 119, 40, port)
    # slcan.add_mask_filter(0, 0x781, 0x7ff, port)
    # time.sleep(0.5)
    # Start with Flags (V2 Function)
    try:
        from slcanv1._slcanv1 import SLCANV2_FLAG_NORMAL, SLCANV2_FLAG_TIMESTAMP,SLCANV2_FLAG_DISABLE_TX_ECHO,SLCANV2_FLAG_ONE_SHOT
        flags = SLCANV2_FLAG_NORMAL  
        slcan.start_with_flags(flags, port)
        print("Started interface with V2 flags.")
    except Exception as e:
        print(f"Failed to start with flags: {e}")

    # Set Rx Callback (V2 Function)
    print("Setting RX Callback to listen for incoming messages in background...")
    # slcan.set_rx_callback(rx_callback, port_name=port)
    
    # Transmit a V2 PacketFD (V2 Function)
    pkt = SlcanV2.PacketFD()
    pkt.id = 0x781
    pkt.dlc = 8

    # Wait to see if callback triggers for loopback or incoming
    print("Waiting 1s for callback messages...")
    time.sleep(1.0)
    i = 0

    while( i < 1000):

        # print("Transmitting V2 PacketFD...")
        slcan.send_packet(pkt, 1000, port)
        time.sleep(0.00020)
        i = i+ 1
    i = 0
    while(1):     
        
        f =slcan.receive_packet(1,port)
        if(f != None):
            print(f"Received Frame! ID: {hex(f.id)} DLC: {f.dlc}, ",i)
            i = i + 1
        pass
    # Stop and clear callback
    print("Cleaning up...")
    slcan.set_rx_callback(None, port_name=port)
    slcan.close(port)

    
    print("V2 test completed.\n")


def test_v2_batch_send():
    print("--- Running V2 Batch Send Test ---")
    slcan = SlcanV2()
    
    # 1. Enumerate Devices using V2 function
    try:
        devices = slcan.enum_devices(10)
        if not devices:
            print("No devices found via V2 enum.")
            return
    except RuntimeError as e:
        print(f"V2 Enum failed: {e}")
        return

    # Use first found channel
    port = devices[0].devicePath.decode('utf-8', errors='ignore')
    print(f"\nOpening port: {port}")
    
    slcan.open_port(port)
    slcan.set_bitrate_advanced(0, 2, 119, 40, port)
    
    try:
        from slcanv1._slcanv1 import SLCANV2_FLAG_NORMAL, SLCANV2_FLAG_DISABLE_TX_ECHO
        flags = SLCANV2_FLAG_NORMAL | SLCANV2_FLAG_DISABLE_TX_ECHO 
        slcan.start_with_flags(flags, port)
        print("Started interface with V2 flags.")
    except Exception as e:
        print(f"Failed to start with flags: {e}")

    # Prepare a Python list of messages
    print("Preparing batch of 10 messages...")
    messages = []
    for i in range(291):
        pkt = SlcanV2.PacketFD()
        pkt.id = 0x100 + i
        pkt.dlc = 8
        # Fill some data
        for j in range(8):
            pkt.data[j] = (j + i) % 256
        messages.append(pkt)

    # Convert the Python list to a ctypes array
    count = len(messages)
    PacketArrayType = SlcanV2.PacketFD * count
    packets_array = PacketArrayType(*messages)

    # Send the batch
    print(f"Sending {count} packets in batch...")
    rc, sent_count = slcan.send_packet_batch(packets_array, count, port)
    
    print(f"Batch send result: rc={rc}, sent_count={sent_count}")

    print("Cleaning up...")
    slcan.close(port)
    print("V2 batch test completed.\n")


def test_v2_functions_GPIO():
    print("--- Running V2 Functions Test ---")
    slcan = SlcanV2()
    
    # 1. Enumerate Devices using V2 function
    try:
        devices = slcan.enum_devices(10)
        if devices:
            print(f"Found {len(devices)} devices via V2 enum:")
            for d in devices:
                print(f"  Name: {d.displayName.decode('utf-8', errors='ignore')} | Path: {d.devicePath.decode('utf-8', errors='ignore')}")
        else:
            print("No devices found via V2 enum.")
            return
    except RuntimeError as e:
        print(f"V2 Enum failed (maybe slcanv2.dll not loaded): {e}")
        return

    # Use first found channel for further V2 tests
    port = devices[0].devicePath.decode('utf-8', errors='ignore')
    print(f"\nOpening port (V2 style path): {port}")
    
    # Initialization uses V1 functions for handle management
    slcan.open_port(port)
    
    # Get Device Info (V2 Function)
    info = slcan.get_device_info(port)
    if info:
        print(f"Device Info: Vendor={info.vendor.decode('utf-8', errors='ignore')}, Supports FD={info.supportsFD}")


    # Identify / blink LED (V2 Function)
    print("Blinking LED (Identify)...")
    slcan.identify(True, port)
    time.sleep(0.5)
    slcan.identify(False, port)

    slcan.set_bitrate_advanced(0, 2, 119, 40, port)
    # slcan.add_mask_filter(0, 0x781, 0x7ff, port)
    # time.sleep(0.5)
    # Start with Flags (V2 Function)
    try:
        from slcanv1._slcanv1 import SLCANV2_FLAG_NORMAL, SLCANV2_FLAG_TIMESTAMP,SLCANV2_FLAG_DISABLE_TX_ECHO,SLCANV2_FLAG_ONE_SHOT
        flags = SLCANV2_FLAG_NORMAL | SLCANV2_FLAG_DISABLE_TX_ECHO 
        slcan.start_with_flags(flags, port)
        print("Started interface with V2 flags.")
    except Exception as e:
        print(f"Failed to start with flags: {e}")

    # Set Rx Callback (V2 Function)
    print("Setting RX Callback to listen for incoming messages in background...")
    # slcan.set_rx_callback(rx_callback, port_name=port)
    
    # Transmit a V2 PacketFD (V2 Function)
    # pkt = SlcanV2.PacketFD()
    # pkt.id = 0x1FFFFF
    # pkt.dlc = 2
    # pkt.ext  = 1
    # pkt.data[0] = 0x0F
    # pkt.data[1] = 0xAA

    # # Wait to see if callback triggers for loopback or incoming
    # print("Waiting 1s for callback messages...")
    # time.sleep(1.0)
    i = 0

    while( i < 10):

        # print("Transmitting V2 PacketFD...")
        slcan.GPIO_ON(6,port)
        time.sleep(5)
        slcan.GPIO_ON(7,port)
        time.sleep(5)
        slcan.GPIO_OFF(6,port)
        time.sleep(5)
        slcan.GPIO_OFF(7,port)
        time.sleep(5)
        i = i+ 1
    # while(1):     
    #     f =slcan.receive_packet(1,port)
        # if(f != None):
            # print(f"Received Frame! ID: {hex(f.id)} DLC: {f.dlc}")
        # pass
    # Stop and clear callback
    print("Cleaning up...")
    slcan.set_rx_callback(None, port_name=port)
    slcan.close(port)

    
    print("V2 test completed.\n")


if __name__ == "__main__":
    # test_single_channel()
    # test_multi_channel()
    test_v2_functions()
    # test_v2_functions_GPIO()
    # test_v2_batch_send()