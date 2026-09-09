import pyray as rl

rl.set_trace_log_level(rl.TraceLogLevel.LOG_NONE)
rl.init_window(10, 10, "Pacman")

SCREEN_WIDTH = rl.get_monitor_width(rl.get_current_monitor())
SCREEN_HEIGHT = rl.get_monitor_height(rl.get_current_monitor())
rl.set_window_size(SCREEN_WIDTH, SCREEN_HEIGHT)
rl.toggle_fullscreen()
