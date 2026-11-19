idf_component_register(
    SRCS main.c app_audio.c
    INCLUDE_DIRS .
    REQUIRES esp32_s3_touch_lcd_1_83 lvgl__lvgl bsp_extra
)