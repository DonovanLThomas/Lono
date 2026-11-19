#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "esp_log.h"
#include "esp_err.h"
#include "esp_check.h"
#include "esp_memory_utils.h"
#include "lvgl.h"
#include "bsp/esp-bsp.h"
#include "bsp/display.h"
#include "lv_demos.h"



static void create_lono_ui(void){
    lv_obj_t *screen = lv_screen_active();
    lv_obj_t *title = lv_label_create(screen);
    lv_label_set_text(title, "Lono");
    lv_obj_align(title, LV_ALIGN_CENTER, 0, 0);

    lv_obj_t *button = lv_button_create(screen);
    lv_obj_set_size(button, 160, 50);
    lv_obj_align(button, LV_ALIGN_BOTTOM_MID, 0, -25);
    lv_obj_t *button_name = lv_label_create(button);
    lv_label_set_text(button_name, "Check Status");
    lv_obj_center(button_name);
}

void app_main(void)
{

    bsp_display_start();
    bsp_display_backlight_on();
    bsp_display_lock(0);
    create_lono_ui();
    bsp_display_unlock();
}
