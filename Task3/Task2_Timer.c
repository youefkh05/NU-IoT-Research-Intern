#include <gpiod.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <sys/time.h>

// BCM Pin Layout Definitions
#define CHIP_NAME "gpiochip0"
#define LED_PIN 17         // Hardware Out to LED
#define BUTTON_PIN 22      // Hardware In from Push-button

// Global hardware pointers visible to the background timer interrupt
struct gpiod_line *led_line = NULL;
struct gpiod_line *button_line = NULL;
volatile sig_atomic_t led_state = 0;

// 1. TIMER INTERRUPT HANDLER: Automatically wakes up every 200ms in the background
void timer_handler(int signum) {
    if (!button_line || !led_line) return;

    // Read the current physical button state (1 = Pressed, 0 = Released)
    int button_pressed = gpiod_line_get_value(button_line);

    if (button_pressed == 1) {
        // 🔹 Condition Met: Toggle the LED state back and forth
        led_state = !led_state;
        gpiod_line_set_value(led_line, led_state);
    } else {
        // 🔸 Condition Fails: Force the LED OFF immediately when released
        led_state = 0;
        gpiod_line_set_value(led_line, 0);
    }
}

int main(void) {
    struct gpiod_chip *chip;
    struct sigaction sa;
    struct itimerval timer;

    // 2. Open the main Raspberry Pi 4 controller chip
    chip = gpiod_chip_open_by_name(CHIP_NAME);
    if (!chip) {
        perror("Open chip failed");
        return 1;
    }

    // 3. Configure the Output LED Line
    led_line = gpiod_chip_get_line(chip, LED_PIN);
    if (!led_line || gpiod_line_request_output(led_line, "timer_led", 0) < 0) {
        perror("LED line configuration failed");
        gpiod_chip_close(chip);
        return 1;
    }

    // 4. Configure the Input Button Line (Sets it to listen for high signals)
    button_line = gpiod_chip_get_line(chip, BUTTON_PIN);
    if (!button_line || gpiod_line_request_input(button_line, "button_sensor") < 0) {
        perror("Button line configuration failed");
        gpiod_line_release(led_line);
        gpiod_chip_close(chip);
        return 1;
    }

    // 5. Register the Background Interrupt Signal Handler
    sa.sa_handler = &timer_handler;
    sa.sa_flags = SA_RESTART; 
    sigaction(SIGALRM, &sa, NULL);

    // 6. Set Blinking Speed (200,000 microseconds = 200ms for a faster blink)
    timer.it_interval.tv_sec = 0;
    timer.it_interval.tv_usec = 200000; // Continuous repeat interval
    timer.it_value.tv_sec = 0;
    timer.it_value.tv_usec = 200000;    // First initial delay time

    // 7. Arm the interval timer
    setitimer(ITIMER_REAL, &timer, NULL);

    printf("System active! Hold down the button to blink the LED.\n");
    printf("The main thread is 100%% free. Press Ctrl+C to exit...\n");

    // 8. The Main Loop is completely empty and non-blocking!
    while (1) {
        pause(); // Puts the main thread to sleep to use 0% CPU until a timer tick occurs
    }

    // Clean up hardware handles on exit
    gpiod_line_release(button_line);
    gpiod_line_release(led_line);
    gpiod_chip_close(chip);
    return 0;
}