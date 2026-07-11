// =============================================================================
//  slcanv2.h  –  CAN DLL API (Candlelight / USB / WinUSB)
// =============================================================================
#ifndef SLCANV2_H_
#define SLCANV2_H_

#include <stdint.h>

// ---------------------------------------------------------------------------
//  DLL Export / Import
// ---------------------------------------------------------------------------
#ifdef SLCANV2_EXPORTS
    #define SLCANV2_API __declspec(dllexport)
#else
    #define SLCANV2_API __declspec(dllimport)
#endif

#ifdef __cplusplus
extern "C" {
#endif

// ---------------------------------------------------------------------------
//  Opaque Handle
// ---------------------------------------------------------------------------
typedef void* slcanv2hnd;

// ===========================================================================
//  Data Structures
// ===========================================================================

// --- Extended CAN FD frame (64-byte data) ---
typedef struct slcanv2PacketFD {
    uint8_t  channel;
    uint32_t id;
    uint8_t  dlc;
    uint8_t  data[64];
    uint8_t  ext;           // 1 = 29-bit extended CAN ID
    uint8_t  fd;            // 1 = CAN FD frame
    uint8_t  brs;           // 1 = Bit Rate Switching
    uint8_t  esi;           // 1 = Error State Indicator
    uint8_t  rtr;           // 1 = Remote Transmission Request
    uint8_t  msg_type;
    uint8_t  error;
    uint8_t  bus_status;
    uint8_t  error_level;
    int64_t  timestamp;     
    char     timestamp_formated[32];
    char     error_msg[128];
} slcanv2PacketFD;

// --- Device enumeration info ---
typedef struct slcanv2DeviceInfo {
    char    displayName[256];
    char    serialNo[256];
    char    devicePath[512];
    int32_t channel;        // One-based channel number
} slcanv2DeviceInfo;

// --- Device capability info ---
typedef struct slcanv2DevCapability {
    char     vendor[128];
    char     product[128];
    char     serial[128];
    uint8_t  supportsFD;    // 1 = CAN FD supported
    uint32_t fclk_can;      // CAN clock frequency (Hz)
} slcanv2DevCapability;

// ===========================================================================
//  Constants
// ===========================================================================

// --- Device start flags (combinable, for slcanv2_start_with_flags) ---
#define SLCANV2_FLAG_NORMAL          0x00000000
#define SLCANV2_FLAG_LISTEN_ONLY     0x00000001
#define SLCANV2_FLAG_LOOPBACK        0x00000002
#define SLCANV2_FLAG_TRIPLE_SAMPLE   0x00000004
#define SLCANV2_FLAG_ONE_SHOT        0x00000008
#define SLCANV2_FLAG_TIMESTAMP       0x00000010  // Enable MCU timestamps
#define SLCANV2_FLAG_FD              0x00000100  // CAN FD mode
#define SLCANV2_FLAG_DISABLE_TX_ECHO 0x00008000  // Disable Tx echo

#define ERROR_INVALID_DEVICE    57010  
#define ERROR_INVALID_FIRMWARE  57011  
#define ERROR_CODE_IN_FEEDBACK  57012  
#define ERROR_RX_FIFO_OVERFLOW  57013  // The application is polling ReceiveData() slower than USB IN packets arrive. In the demo app the reason may be the slow Windows console.
#define ERROR_CORRUPT_IN_DATA   57014  // Corrupt USB IN packet received from the firmware
#define ERROR_UPDATE_FIRMWARE   57015  // The user must update the firmware
#define ERROR_TOO_MANY_ERRORS   57016  // too many errors during WritePipe / ReadPipe

// ===========================================================================
//  Device Enumeration
// ===========================================================================

SLCANV2_API int32_t slcanv2_enum_devices(slcanv2DeviceInfo* devicesOut, int32_t maxDevices);

// ===========================================================================
//  Open / Close
// ===========================================================================

// Open a Candlelight USB device by its devicePath (obtained from slcanv2_enum_devices)
// Returns a valid handle on success, or NULL on failure.
SLCANV2_API slcanv2hnd slcanv2_open(const char* devicePath);

// Close the device and free the handle.
SLCANV2_API int32_t slcanv2_close(slcanv2hnd hnd);

// ===========================================================================
//  Bitrate Configuration
// ===========================================================================

// --- Device enumeration ---
SLCANV2_API int32_t slcanv2_enum_devices(slcanv2DeviceInfo* devicesOut, int32_t maxDevices);

// --- Bitrate (advanced, CAN FD) ---
SLCANV2_API int32_t slcanv2_set_bitrate_advanced(
    slcanv2hnd hnd, uint8_t isFD, int32_t brp, int32_t seg1, int32_t seg2);

// ===========================================================================
//  CAN ID Filtering
// ===========================================================================

// Add a CAN ID acceptance mask filter (up to 8 filters).
// is29bit: 0 = 11-bit, 1 = 29-bit
SLCANV2_API int32_t slcanv2_add_mask_filter(
    slcanv2hnd hnd, uint8_t is29bit, uint32_t filter_id, uint32_t mask);

// ===========================================================================
//  Start / Stop
// ===========================================================================

// Start the CAN interface with device flags (SLCANV2_FLAG_* constants).
SLCANV2_API int32_t slcanv2_start_with_flags(slcanv2hnd hnd, uint32_t flags);

// ===========================================================================
//  Send / Receive
// ===========================================================================

// --- Send (CAN FD) ---
SLCANV2_API int32_t slcanv2_send_packet(slcanv2hnd hnd, const slcanv2PacketFD* packet,uint64_t timeout_ms);

// --- Send Batch (CAN FD) ---
SLCANV2_API int32_t slcanv2_send_packet_batch(slcanv2hnd hnd, const slcanv2PacketFD* packets, int32_t count, int32_t* sentCountOut);

// --- Receive (polling, CAN FD) ---
// Returns: 1 = packet received, 0 = timeout, negative = error
SLCANV2_API int32_t slcanv2_receive_packet(
    slcanv2hnd hnd, slcanv2PacketFD* packet, uint32_t timeout_ms);

// --- Receive (callback, background thread) ---
// Pass callback = NULL to stop the receive thread.
// Returns: 0 = started, 1 = already running (filter updated), -1 = error

SLCANV2_API
int32_t slcanv2_set_rx_callback(
    slcanv2hnd hnd,
    void (__cdecl* callback)(slcanv2PacketFD* f));


// ===========================================================================
//  Device Info
// ===========================================================================

SLCANV2_API int32_t slcanv2_get_device_info(slcanv2hnd hnd, slcanv2DevCapability* capOut);
SLCANV2_API int32_t slcanv2_get_details(slcanv2hnd hnd, char* detailsOut, int32_t maxLen);

// ===========================================================================
//  LED / Identification
// ===========================================================================

// blink: 1 = start blinking, 0 = stop
SLCANV2_API int32_t slcanv2_identify(slcanv2hnd hnd, uint8_t blink);

// ===========================================================================
//  Bus Load Reporting
// ===========================================================================

// interval: 0 = disable, 1-255 = interval in 100 ms units
SLCANV2_API int32_t slcanv2_enable_busload_report(slcanv2hnd hnd, uint8_t interval);

// ===========================================================================
//  DFU / Boot Pin
// ===========================================================================

SLCANV2_API int32_t slcanv2_enter_dfu_mode(slcanv2hnd hnd);
SLCANV2_API int32_t slcanv2_disable_boot_pin(slcanv2hnd hnd);
SLCANV2_API int32_t slcanv2_is_boot_pin_enabled(slcanv2hnd hnd, uint8_t* enabledOut);

// ===========================================================================
//  Timestamps
// ===========================================================================

// Get a high-precision Windows timestamp (microseconds, monotonic).
SLCANV2_API int64_t slcanv2_get_timestamp(slcanv2hnd hnd);

// Select timestamp source for received packets.
// mode: SLCANV2_TIMESTAMP_NONE / _MCU / _WINDOWS
SLCANV2_API int32_t slcanv2_set_timestamp_mode(slcanv2hnd hnd, int32_t mode);

// ===========================================================================
//  Error Formatting
// ===========================================================================

SLCANV2_API int32_t slcanv2_format_error(
    slcanv2hnd hnd, int32_t errorCode, char* msgOut, int32_t maxLen);

#ifdef __cplusplus
}
#endif

#endif // SLCANV2_H_
