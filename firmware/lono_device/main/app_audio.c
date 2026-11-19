#include "app_audio.h"
#include "bsp_board_extra.h"
#include <stdint.h>
#include <stddef.h>

#define TEST_SAMPLE_RATE       16000
#define TEST_FREQUENCY_HZ      1000
#define TEST_DURATION_MS       250
#define TEST_CHANNELS          2
#define TEST_AMPLITUDE         4000
#define TEST_CHUNK_FRAMES      256

esp_err_t app_audio_init(void){
    esp_err_t code = bsp_extra_codec_init();

    if (code != ESP_OK){
        return code;
    }

    esp_err_t volume = bsp_extra_codec_volume_set(40, NULL);

    if (volume != ESP_OK){
        return volume;
    }

    return ESP_OK;
}

esp_err_t app_audio_play_test_tone(void){
    static int16_t buffer[TEST_CHUNK_FRAMES * TEST_CHANNELS];

    const int total_frames = (TEST_SAMPLE_RATE * TEST_DURATION_MS) / 1000;
    const int half_wave = TEST_SAMPLE_RATE / (TEST_FREQUENCY_HZ * 2);
    int current_frame = 0;

    while(current_frame < total_frames){
        int remaining_frames = total_frames - current_frame;
        int frames_in_chunk;

        if (remaining_frames < TEST_CHUNK_FRAMES){
            frames_in_chunk = remaining_frames;
        }
        else{
            frames_in_chunk = TEST_CHUNK_FRAMES;
        }

        for (int index = 0; index < frames_in_chunk; index++) {
            int absolute_frame = current_frame + index;
            int16_t sample;

            if (((absolute_frame / half_wave) % 2) == 0) {
                sample = TEST_AMPLITUDE;
            } else {
                sample = -TEST_AMPLITUDE;
            }

            buffer[index * TEST_CHANNELS] = sample;
            buffer[index * TEST_CHANNELS + 1] = sample;
        }

        size_t byte_count =
            frames_in_chunk * TEST_CHANNELS * sizeof(int16_t);

        size_t bytes_written = 0;

        esp_err_t write_code = bsp_extra_i2s_write(
            buffer,
            byte_count,
            &bytes_written,
            1000
        );

        if (write_code != ESP_OK) {
            return write_code;
        }

        if (bytes_written != byte_count) {
            return ESP_FAIL;
        }

        current_frame += frames_in_chunk;
    }

    return ESP_OK;
}
