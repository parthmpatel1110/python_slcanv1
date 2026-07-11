import ctypes
import os
import sys

def is_64bit_python():
    return sys.maxsize > 2**32

if is_64bit_python():
    _dll_path = os.path.join(os.path.dirname(__file__), "slcanv1_DLL_win_64bit.dll")
else:
    _dll_path = os.path.join(os.path.dirname(__file__), "slcanv1_DLL_win_32bit.dll")

_dll = ctypes.CDLL(_dll_path)

_dll2_path = os.path.join(os.path.dirname(__file__), "slcanv2.dll")
try:
    _dll2 = ctypes.CDLL(_dll2_path)
except Exception:
    _dll2 = None

slcanv1hnd = ctypes.c_void_p
PortNameType = ctypes.c_char * 40

class Frame(ctypes.Structure):
    __slots__ = []
    _fields_ = [
        ("channel", ctypes.c_uint8),
        ("id", ctypes.c_uint32),
        ("dlc", ctypes.c_uint8),
        ("data", ctypes.c_uint8 * 8),
        ("ext", ctypes.c_uint8),
        ("fd", ctypes.c_uint8),
        ("loopback", ctypes.c_uint8),
        ("rtr", ctypes.c_uint8),
        ("error", ctypes.c_uint8),
    ]



class PacketFD(ctypes.Structure):
    __slots__ = []
    _fields_ = [
        ("channel", ctypes.c_uint8),
        ("id", ctypes.c_uint32),
        ("dlc", ctypes.c_uint8),
        ("data", ctypes.c_uint8 * 64),
        ("ext", ctypes.c_uint8),
        ("fd", ctypes.c_uint8),
        ("brs", ctypes.c_uint8),
        ("esi", ctypes.c_uint8),
        ("rtr", ctypes.c_uint8),
        ("msg_type", ctypes.c_uint8),
        ("error", ctypes.c_uint8),
        ("bus_status", ctypes.c_uint8),
        ("error_level", ctypes.c_uint8),
        ("timestamp", ctypes.c_int64),
        ("timestamp_formated", ctypes.c_char * 32),
        ("error_msg", ctypes.c_char * 128),
    ]

class DeviceInfo(ctypes.Structure):
    _fields_ = [
        ("displayName", ctypes.c_char * 256),
        ("serialNo", ctypes.c_char * 256),
        ("devicePath", ctypes.c_char * 512),
        ("channel", ctypes.c_int32),
    ]

class DevCapability(ctypes.Structure):
    _fields_ = [
        ("vendor", ctypes.c_char * 128),
        ("product", ctypes.c_char * 128),
        ("serial", ctypes.c_char * 128),
        ("supportsFD", ctypes.c_uint8),
        ("fclk_can", ctypes.c_uint32),
    ]

# --- V2 Constants ---
SLCANV2_FLAG_NORMAL          = 0x00000000
SLCANV2_FLAG_LISTEN_ONLY     = 0x00000001
SLCANV2_FLAG_LOOPBACK        = 0x00000002
SLCANV2_FLAG_TRIPLE_SAMPLE   = 0x00000004
SLCANV2_FLAG_ONE_SHOT        = 0x00000008
SLCANV2_FLAG_TIMESTAMP       = 0x00000010
SLCANV2_FLAG_FD              = 0x00000100
SLCANV2_FLAG_DISABLE_TX_ECHO = 0x00008000

ERROR_INVALID_DEVICE    = 57010  
ERROR_INVALID_FIRMWARE  = 57011  
ERROR_CODE_IN_FEEDBACK  = 57012  
ERROR_RX_FIFO_OVERFLOW  = 57013
ERROR_CORRUPT_IN_DATA   = 57014
ERROR_UPDATE_FIRMWARE   = 57015
ERROR_TOO_MANY_ERRORS   = 57016


# --- Setup V1 Functions ---
_dll.slcanv1_init.restype = slcanv1hnd
_dll.slcanv1_deinit.restype = ctypes.c_int32
_dll.slcanv1_open.restype = ctypes.c_int32
_dll.slcanv1_close.restype = ctypes.c_int32
_dll.slcanv1_get_channel.restype = ctypes.c_int32
_dll.slcanv1_set_bitrate.restype = ctypes.c_int32
_dll.slcanv1_start.restype = ctypes.c_int32
_dll.slcanv1_stop.restype = ctypes.c_int32
_dll.slcanv1_transmit.restype = ctypes.c_int32
_dll.slcanv1_readMessage.restype = ctypes.c_int
_dll.slcanv1_readMessage_timeout.restype = ctypes.c_int
_dll.slcanv1_readMessage_WithMask.restype = ctypes.c_int

_dll.slcanv1_get_channel.argtypes = [slcanv1hnd, ctypes.c_char_p]
_dll.slcanv1_open.argtypes = [slcanv1hnd]
_dll.slcanv1_close.argtypes = [slcanv1hnd]
_dll.slcanv1_deinit.argtypes = [slcanv1hnd]
_dll.slcanv1_set_bitrate.argtypes = [slcanv1hnd, ctypes.c_uint8, ctypes.c_uint32]
_dll.slcanv1_start.argtypes = [slcanv1hnd]
_dll.slcanv1_stop.argtypes = [slcanv1hnd]
_dll.slcanv1_transmit.argtypes = [slcanv1hnd, Frame]
_dll.slcanv1_readMessage.argtypes = [slcanv1hnd, ctypes.POINTER(Frame)]
_dll.slcanv1_readMessage_timeout.argtypes = [slcanv1hnd, ctypes.POINTER(Frame),ctypes.c_uint32]
_dll.slcanv1_readMessage_WithMask.argtypes = [slcanv1hnd, ctypes.POINTER(Frame),ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32]

RX_CALLBACK_TYPE_V1 = ctypes.CFUNCTYPE(None, ctypes.POINTER(Frame))
_dll.slcanv1_set_rx_callback.restype = ctypes.c_int32
_dll.slcanv1_set_rx_callback.argtypes = [slcanv1hnd, RX_CALLBACK_TYPE_V1, ctypes.c_uint32, ctypes.c_uint32]

_dll.slcanv1_get_all_channels.argtypes = [ctypes.POINTER(PortNameType), ctypes.c_int]
_dll.slcanv1_open_port.argtypes = [slcanv1hnd, ctypes.c_char_p]

# --- Setup V2 Functions ---
def _get_func(dll, c_name, cpp_name=None):
    if dll is None: return None
    if hasattr(dll, c_name): return getattr(dll, c_name)
    if cpp_name and hasattr(dll, cpp_name): return getattr(dll, cpp_name)
    return None

slcanv2_open = _get_func(_dll2, 'slcanv2_open')
if slcanv2_open:
    slcanv2_open.argtypes = [ctypes.c_char_p]
    slcanv2_open.restype = slcanv1hnd

slcanv2_close = _get_func(_dll2, 'slcanv2_close')
if slcanv2_close:
    slcanv2_close.argtypes = [slcanv1hnd]
    slcanv2_close.restype = ctypes.c_int32

slcanv2_enum_devices = _get_func(_dll2, 'slcanv2_enum_devices')
if slcanv2_enum_devices:
    slcanv2_enum_devices.argtypes = [ctypes.POINTER(DeviceInfo), ctypes.c_int32]
    slcanv2_enum_devices.restype = ctypes.c_int32

slcanv2_set_bitrate_advanced = _get_func(_dll2, 'slcanv2_set_bitrate_advanced')
if slcanv2_set_bitrate_advanced:
    slcanv2_set_bitrate_advanced.argtypes = [slcanv1hnd, ctypes.c_uint8, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    slcanv2_set_bitrate_advanced.restype = ctypes.c_int32

slcanv2_add_mask_filter = _get_func(_dll2, 'slcanv2_add_mask_filter', '?slcanv2_add_mask_filter@@YAHPEAXEKK@Z')
if slcanv2_add_mask_filter:
    slcanv2_add_mask_filter.argtypes = [slcanv1hnd, ctypes.c_uint8, ctypes.c_uint32, ctypes.c_uint32]
    slcanv2_add_mask_filter.restype = ctypes.c_int32

slcanv2_start_with_flags = _get_func(_dll2, 'slcanv2_start_with_flags', '?slcanv2_start_with_flags@@YAHPEAXK@Z')
if slcanv2_start_with_flags:
    slcanv2_start_with_flags.argtypes = [slcanv1hnd, ctypes.c_uint32]
    slcanv2_start_with_flags.restype = ctypes.c_int32

slcanv2_send_packet = _get_func(_dll2, 'slcanv2_send_packet')
if slcanv2_send_packet:
    slcanv2_send_packet.argtypes = [slcanv1hnd, ctypes.POINTER(PacketFD), ctypes.c_uint64]
    slcanv2_send_packet.restype = ctypes.c_int32

slcanv2_send_packet_batch = _get_func(_dll2, 'slcanv2_send_packet_batch')
if slcanv2_send_packet_batch:
    slcanv2_send_packet_batch.argtypes = [slcanv1hnd, ctypes.POINTER(PacketFD), ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]
    slcanv2_send_packet_batch.restype = ctypes.c_int32

slcanv2_receive_packet = _get_func(_dll2, 'slcanv2_receive_packet', '?slcanv2_receive_packet@@YAHPEAXPEAUslcanv2PacketFD@@K@Z')
if slcanv2_receive_packet:
    slcanv2_receive_packet.argtypes = [slcanv1hnd, ctypes.POINTER(PacketFD), ctypes.c_uint32]
    slcanv2_receive_packet.restype = ctypes.c_int32

RX_CALLBACK_TYPE = ctypes.CFUNCTYPE(None, ctypes.POINTER(PacketFD))
slcanv2_set_rx_callback = _get_func(_dll2, 'slcanv2_set_rx_callback')
if slcanv2_set_rx_callback:
    slcanv2_set_rx_callback.argtypes = [slcanv1hnd, RX_CALLBACK_TYPE]
    slcanv2_set_rx_callback.restype = ctypes.c_int32

slcanv2_get_device_info = _get_func(_dll2, 'slcanv2_get_device_info')
if slcanv2_get_device_info:
    slcanv2_get_device_info.argtypes = [slcanv1hnd, ctypes.POINTER(DevCapability)]
    slcanv2_get_device_info.restype = ctypes.c_int32

slcanv2_get_details = _get_func(_dll2, 'slcanv2_get_details')
if slcanv2_get_details:
    slcanv2_get_details.argtypes = [slcanv1hnd, ctypes.c_char_p, ctypes.c_int32]
    slcanv2_get_details.restype = ctypes.c_int32

slcanv2_identify = _get_func(_dll2, 'slcanv2_identify')
if slcanv2_identify:
    slcanv2_identify.argtypes = [slcanv1hnd, ctypes.c_uint8]
    slcanv2_identify.restype = ctypes.c_int32

slcanv2_enable_busload_report = _get_func(_dll2, 'slcanv2_enable_busload_report')
if slcanv2_enable_busload_report:
    slcanv2_enable_busload_report.argtypes = [slcanv1hnd, ctypes.c_uint8]
    slcanv2_enable_busload_report.restype = ctypes.c_int32

slcanv2_enter_dfu_mode = _get_func(_dll2, 'slcanv2_enter_dfu_mode')
if slcanv2_enter_dfu_mode:
    slcanv2_enter_dfu_mode.argtypes = [slcanv1hnd]
    slcanv2_enter_dfu_mode.restype = ctypes.c_int32

slcanv2_disable_boot_pin = _get_func(_dll2, 'slcanv2_disable_boot_pin')
if slcanv2_disable_boot_pin:
    slcanv2_disable_boot_pin.argtypes = [slcanv1hnd]
    slcanv2_disable_boot_pin.restype = ctypes.c_int32

slcanv2_is_boot_pin_enabled = _get_func(_dll2, 'slcanv2_is_boot_pin_enabled')
if slcanv2_is_boot_pin_enabled:
    slcanv2_is_boot_pin_enabled.argtypes = [slcanv1hnd, ctypes.POINTER(ctypes.c_uint8)]
    slcanv2_is_boot_pin_enabled.restype = ctypes.c_int32

slcanv2_get_timestamp = _get_func(_dll2, 'slcanv2_get_timestamp')
if slcanv2_get_timestamp:
    slcanv2_get_timestamp.argtypes = [slcanv1hnd]
    slcanv2_get_timestamp.restype = ctypes.c_int64

slcanv2_set_timestamp_mode = _get_func(_dll2, 'slcanv2_set_timestamp_mode')
if slcanv2_set_timestamp_mode:
    slcanv2_set_timestamp_mode.argtypes = [slcanv1hnd, ctypes.c_int32]
    slcanv2_set_timestamp_mode.restype = ctypes.c_int32

slcanv2_format_error = _get_func(_dll2, 'slcanv2_format_error')
if slcanv2_format_error:
    slcanv2_format_error.argtypes = [slcanv1hnd, ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32]
    slcanv2_format_error.restype = ctypes.c_int32

class SlcanV1:
    Frame = Frame

    def __init__(self):
        self._hnd = _dll.slcanv1_init()
        self._hnd2 = {}
        if not self._hnd:
            raise RuntimeError("Failed to init slcanv1")

    def _get_hnd(self, port_name=None):
        if port_name is None:
            return self._hnd
        if isinstance(port_name, str):
            port_name = port_name.encode('utf-8')
        return self._hnd2.get(port_name, self._hnd)

    def get_channel(self):
        port_out = ctypes.create_string_buffer(256)
        ok = _dll.slcanv1_get_channel(self._hnd, port_out)
        if ok:
            return port_out.value.decode()
        else:
            return None
    
    def get_all_channels(self, max_ports=10):
        buffer = (PortNameType * max_ports)() 
        result = _dll.slcanv1_get_all_channels(buffer, max_ports)
        if result > 0:
            return [buffer[i].value.decode('utf-8') for i in range(result)]
        else:
            return None
    
    def open_port(self, port_name):
        if isinstance(port_name, str):
            port_name = port_name.encode('utf-8')
        if port_name not in self._hnd2:
            self._hnd2[port_name] = _dll.slcanv1_init()
        rc = _dll.slcanv1_open_port(self._hnd2[port_name], port_name)
        if rc != 0 :
            raise RuntimeError(f"failed to start poort: {port_name}")
        else:
            return 1

    def deinit(self, port_name = None):
        hnd = self._get_hnd(port_name)
        _dll.slcanv1_deinit(hnd)

    def set_bitrate(self, bitrate, port_name = None):
        hnd = self._get_hnd(port_name)
        rc = _dll.slcanv1_set_bitrate(hnd, 0, bitrate)
        if rc != 1:
            raise RuntimeError(f"Set bitrate failed: {rc}")

    def start(self, port_name = None):
        hnd = self._get_hnd(port_name)
        rc = _dll.slcanv1_start(hnd)
        if rc != 0:
            raise RuntimeError(f"Start failed: {rc}")

    def stop(self, port_name = None):
        hnd = self._get_hnd(port_name)
        _dll.slcanv1_stop(hnd)

    def transmit_Frame(self, f, port_name = None):
        hnd = self._get_hnd(port_name)
        rc = _dll.slcanv1_transmit(hnd, f)
        return rc

    def read(self, port_name = None):
        hnd = self._get_hnd(port_name)
        f = Frame()
        rc = _dll.slcanv1_readMessage(hnd, ctypes.byref(f))
        if rc == 0:
            return f
        else:
            return None
    
    def read_timeout(self,timeout, port_name = None):
        hnd = self._get_hnd(port_name)
        f = Frame()
        rc = _dll.slcanv1_readMessage_timeout(hnd, ctypes.byref(f),timeout)
        if rc == 0:
            return f
        else:
            return None
        
    def read_withMask(self,filter_id,mask_id,timeout, port_name = None):
        hnd = self._get_hnd(port_name)
        f = Frame()
        rc = _dll.slcanv1_readMessage_WithMask(hnd, ctypes.byref(f),filter_id,mask_id,timeout)
        if rc == 0:
            return f
        else:
            return None
        
    def open(self):
        rc = _dll.slcanv1_open(self._hnd)
        if rc != 0:
            raise RuntimeError(f"Open failed: {rc}")

    def set_rx_callback(self, callback, filter_id=0, mask=0, port_name=None):
        hnd = self._get_hnd(port_name)
        if callback is None:
            if hasattr(self, '_rx_cbs') and hnd in self._rx_cbs:
                del self._rx_cbs[hnd]
            return _dll.slcanv1_set_rx_callback(hnd, ctypes.cast(None, RX_CALLBACK_TYPE_V1), filter_id, mask)
        else:
            cb = RX_CALLBACK_TYPE_V1(callback)
            if not hasattr(self, '_rx_cbs'):
                self._rx_cbs = {}
            self._rx_cbs[hnd] = cb
            return _dll.slcanv1_set_rx_callback(hnd, cb, filter_id, mask)

    def close(self, port_name=None):
        hnd = self._get_hnd(port_name)
        _dll.slcanv1_close(hnd)

    def transmit(self, can_id, data: bytes, ext=False, port_name=None):
        hnd = self._get_hnd(port_name)
        f = Frame()
        f.channel = 0
        f.id = can_id
        f.dlc = len(data)
        f.ext = 1 if ext else 0
        for i in range(len(data)):
            f.data[i] = data[i]
        return _dll.slcanv1_transmit(hnd, f)

    def __del__(self):
        try:
            if hasattr(self, '_hnd') and self._hnd:
                self.stop()
                self.close()
                self.deinit()
        except:
            pass
        
        try:
            if hasattr(self, '_hnd2'):
                for port_name in list(self._hnd2.keys()):
                    self.stop(port_name)
                    self.close(port_name)
                    self.deinit(port_name)
        except:
            pass


class SlcanV2:
    PacketFD = PacketFD
    DeviceInfo = DeviceInfo
    DevCapability = DevCapability

    def __init__(self):
        self._hnd2 = {}
        self._rx_cbs = {}
        self.GPIO = 0x00

    def _get_hnd(self, port_name):
        if isinstance(port_name, str):
            port_name = port_name.encode('utf-8')
        if port_name not in self._hnd2:
            raise RuntimeError(f"Port not opened: {port_name}")
        return self._hnd2[port_name]

    def open_port(self, port_name):
        if not slcanv2_open: raise RuntimeError("V2 function not available")
        if isinstance(port_name, str):
            port_name = port_name.encode('utf-8')
        
        hnd = slcanv2_open(port_name)
        if not hnd:
            raise RuntimeError(f"Failed to open V2 port: {port_name.decode('utf-8')}")
        self._hnd2[port_name] = hnd
        return 1

    def close(self, port_name):
        if not slcanv2_close: raise RuntimeError("V2 function not available")
        if isinstance(port_name, str):
            port_name = port_name.encode('utf-8')
        if port_name in self._hnd2:
            hnd = self._hnd2[port_name]
            slcanv2_close(hnd)
            del self._hnd2[port_name]


    def enum_devices(self, max_devices=10):
        if not slcanv2_enum_devices: raise RuntimeError("V2 function not available")
        devices = (DeviceInfo * max_devices)()
        result = slcanv2_enum_devices(devices, max_devices)
        if result > 0:
            return [devices[i] for i in range(result)]
        return None

    def set_bitrate_advanced(self, is_fd, brp, seg1, seg2, port_name):
        if not slcanv2_set_bitrate_advanced: raise RuntimeError("V2 function not available")
        hnd = self._get_hnd(port_name)
        return slcanv2_set_bitrate_advanced(hnd, is_fd, brp, seg1, seg2)

    def add_mask_filter(self, is_29bit, filter_id, mask, port_name):
        if not slcanv2_add_mask_filter: raise RuntimeError("V2 function not available")
        hnd = self._get_hnd(port_name)
        return slcanv2_add_mask_filter(hnd, is_29bit, filter_id, mask)

    def start_with_flags(self, flags, port_name):
        if not slcanv2_start_with_flags: raise RuntimeError("V2 function not available")
        hnd = self._get_hnd(port_name)
        return slcanv2_start_with_flags(hnd, flags)

    def send_packet(self, packet, timeout_ms, port_name):
        if not slcanv2_send_packet: raise RuntimeError("V2 function not available")
        hnd = self._get_hnd(port_name)
        return slcanv2_send_packet(hnd, ctypes.byref(packet), timeout_ms)

    def send_packet_batch(self, packets_array, count, port_name):
        if not slcanv2_send_packet_batch: raise RuntimeError("V2 function not available")
        hnd = self._get_hnd(port_name)
        sent_count = ctypes.c_int32(0)
        rc = slcanv2_send_packet_batch(hnd, packets_array, count, ctypes.byref(sent_count))
        return rc, sent_count.value

    def receive_packet(self, timeout_ms, port_name):
        if not slcanv2_receive_packet: raise RuntimeError("V2 function not available")
        hnd = self._get_hnd(port_name)
        packet = PacketFD()
        rc = slcanv2_receive_packet(hnd, ctypes.byref(packet), timeout_ms)
        if rc == 1:
            return packet
        return None

    def set_rx_callback(self, callback, port_name=None):
        if not slcanv2_set_rx_callback: raise RuntimeError("V2 function not available")
        hnd = self._get_hnd(port_name)
        if callback is None:
            if hnd in self._rx_cbs:
                del self._rx_cbs[hnd]
            return slcanv2_set_rx_callback(hnd, ctypes.cast(None, RX_CALLBACK_TYPE))
        else:
            cb = RX_CALLBACK_TYPE(callback)
            self._rx_cbs[hnd] = cb
            return slcanv2_set_rx_callback(hnd, cb)

    def get_device_info(self, port_name):
        if not slcanv2_get_device_info: raise RuntimeError("V2 function not available")
        hnd = self._get_hnd(port_name)
        cap = DevCapability()
        rc = slcanv2_get_device_info(hnd, ctypes.byref(cap))
        if rc == 0:
            return cap
        return None

    def get_details(self, max_len=256, port_name=None):
        if not slcanv2_get_details: raise RuntimeError("V2 function not available")
        hnd = self._get_hnd(port_name)
        buf = ctypes.create_string_buffer(max_len)
        rc = slcanv2_get_details(hnd, buf, max_len)
        if rc == 0:
            return buf.value.decode('utf-8', errors='ignore')
        return None

    def identify(self, blink, port_name):
        if not slcanv2_identify: raise RuntimeError("V2 function not available")
        hnd = self._get_hnd(port_name)
        return slcanv2_identify(hnd, 1 if blink else 0)

    def enable_busload_report(self, interval, port_name):
        if not slcanv2_enable_busload_report: raise RuntimeError("V2 function not available")
        hnd = self._get_hnd(port_name)
        return slcanv2_enable_busload_report(hnd, interval)

    def enter_dfu_mode(self, port_name):
        if not slcanv2_enter_dfu_mode: raise RuntimeError("V2 function not available")
        hnd = self._get_hnd(port_name)
        return slcanv2_enter_dfu_mode(hnd)

    def disable_boot_pin(self, port_name):
        if not slcanv2_disable_boot_pin: raise RuntimeError("V2 function not available")
        hnd = self._get_hnd(port_name)
        return slcanv2_disable_boot_pin(hnd)

    def is_boot_pin_enabled(self, port_name):
        if not slcanv2_is_boot_pin_enabled: raise RuntimeError("V2 function not available")
        hnd = self._get_hnd(port_name)
        enabled = ctypes.c_uint8(0)
        rc = slcanv2_is_boot_pin_enabled(hnd, ctypes.byref(enabled))
        if rc == 0:
            return bool(enabled.value)
        return None

    def get_timestamp(self, port_name):
        if not slcanv2_get_timestamp: raise RuntimeError("V2 function not available")
        hnd = self._get_hnd(port_name)
        return slcanv2_get_timestamp(hnd)

    def set_timestamp_mode(self, mode, port_name=None):
        if not slcanv2_set_timestamp_mode: raise RuntimeError("V2 function not available")
        # In the C++ DLL mode is global, but the function takes an hnd
        if port_name:
            hnd = self._get_hnd(port_name)
        else:
            hnd = None
        return slcanv2_set_timestamp_mode(hnd, mode)

    def format_error(self, error_code, max_len=256, port_name=None):
        if not slcanv2_format_error: raise RuntimeError("V2 function not available")
        if port_name:
            hnd = self._get_hnd(port_name)
        else:
            hnd = None
        buf = ctypes.create_string_buffer(max_len)
        rc = slcanv2_format_error(hnd, error_code, buf, max_len)
        if rc == 0:
            return buf.value.decode('utf-8', errors='ignore')
        return None

    def GPIO_ON(self, pin, port_name):
        if not isinstance(pin, int):
            raise TypeError("pin must be an integer")
        
        pkt = self.PacketFD()
        pkt.id = 0x1FFFFF
        pkt.dlc = 2
        pkt.ext  = 1
        pkt.data[1] = 0xAA

        self.GPIO = self.GPIO | (1 << pin)
        pkt.data[0] = self.GPIO
        return self.send_packet(pkt, 1000, port_name)
        
    def GPIO_OFF(self, pin, port_name):
        if not isinstance(pin, int):
            raise TypeError("pin must be an integer")
        
        pkt = self.PacketFD()
        pkt.id = 0x1FFFFF
        pkt.dlc = 2
        pkt.ext  = 1
        pkt.data[1] = 0xAA
        self.GPIO =self.GPIO & ( ~ (1 << pin))
        pkt.data[0] = self.GPIO
        return self.send_packet(pkt, 1000, port_name)

    def __del__(self):
        try:
            if hasattr(self, '_hnd2'):
                for port_name in list(self._hnd2.keys()):
                    self.close(port_name)
        except:
            pass

        try:
            if(self.GPIO != 0x00):
                pkt = self.PacketFD()
                pkt.id = 0x1FFFFF
                pkt.dlc = 2
                pkt.ext  = 1
                pkt.data[1] = 0xAA
                pkt.data[0] = 0x00
                self.send_packet(pkt, 1000, port_name)
        except:
            pass
