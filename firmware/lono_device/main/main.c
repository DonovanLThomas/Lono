#include "lvgl.h"
#include "bsp/esp-bsp.h"
#include "bsp/display.h"
#include "app_audio.h"
#include "esp_err.h"


static void status_button_event_cb(lv_event_t *event){
    lv_obj_t *status_label = lv_event_get_user_data(event);
    lv_label_set_text(status_label, "Button Pressed");
}


static void create_lono_ui(void){
    lv_obj_t *screen = lv_screen_active();
    lv_obj_t *title = lv_label_create(screen);
    lv_obj_t *status_label = lv_label_create(screen);
    lv_label_set_text(title, "Lono");
    lv_label_set_text(status_label, "Ready");
    lv_obj_align(status_label, LV_ALIGN_TOP_MID, 0, 0);
    lv_obj_align(title, LV_ALIGN_CENTER, 0, 30);

    lv_obj_t *button = lv_button_create(screen);
    lv_obj_set_size(button, 160, 50);
    lv_obj_align(button, LV_ALIGN_BOTTOM_MID, 0, -25);
    lv_obj_t *button_name = lv_label_create(button);
    lv_label_set_text(button_name, "Check Status");
    lv_obj_center(button_name);

    lv_obj_add_event_cb(
        button,
        status_button_event_cb,
        LV_EVENT_CLICKED,
        status_label
    );
}

void app_main(void)
{

    bsp_display_start();
    bsp_display_backlight_on();
    bsp_display_lock(0);
    create_lono_ui();
    bsp_display_unlock();
    ESP_ERROR_CHECK(app_audio_init());
    ESP_ERROR_CHECK(app_audio_play_test_tone());
}
