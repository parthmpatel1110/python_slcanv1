#ifndef slcanv1_H_
#define slcanv1_H_

#include <stdint.h>

//#ifdef SLCANV1_EXPORTS
#define SLCANV1_API __declspec(dllexport)
//#else
//#define SLCANV1_API __declspec(dllimport)
//#endif

typedef void* slcanv1hnd;

typedef struct slcanv1Frame {
    uint8_t channel;
    uint32_t id;
    uint8_t dlc;
    uint8_t data[8];
    uint8_t ext;
    uint8_t fd;
    uint8_t loopback;
    uint8_t rtr;
    uint8_t error;
} slcanv1Frame;
//
extern SLCANV1_API slcanv1hnd slcanv1_init();
extern SLCANV1_API int32_t slcanv1_deinit(slcanv1hnd hnd);
extern SLCANV1_API int32_t slcanv1_open(slcanv1hnd hnd);
extern SLCANV1_API int32_t slcanv1_close(slcanv1hnd hnd);
extern SLCANV1_API int32_t slcanv1_set_rx_callback(
    slcanv1hnd hnd,
    void(__cdecl* callback)(slcanv1Frame* f),
    uint32_t filter_id,
    uint32_t mask);
extern SLCANV1_API int32_t slcanv1_start(slcanv1hnd hnd);
extern SLCANV1_API int32_t slcanv1_stop(slcanv1hnd hnd);
extern SLCANV1_API int32_t slcanv1_transmit(slcanv1hnd hnd, const slcanv1Frame f);
extern SLCANV1_API int32_t slcanv1_set_bitrate(slcanv1hnd hnd, uint8_t channel, uint32_t bitrate);
extern SLCANV1_API int32_t slcanv1_get_channel(slcanv1hnd hnd, char* serialPortOut);
extern SLCANV1_API int slcanv1_readMessage(slcanv1hnd hnd, slcanv1Frame* f);
extern SLCANV1_API int slcanv1_readMessage_WithMask(
    slcanv1hnd hnd,
    slcanv1Frame* f,
    uint32_t filter_id,
    uint32_t mask,
    uint32_t timeout_ms);
extern SLCANV1_API int slcanv1_readMessage_timeout(slcanv1hnd hnd, slcanv1Frame* f, uint32_t timeout_ms);
extern SLCANV1_API int32_t slcanv1_get_all_channels(char serialPortsOut[][40], int maxPorts);
extern SLCANV1_API int32_t slcanv1_open_port(slcanv1hnd hnd, char* fullPort);
    

#endif
