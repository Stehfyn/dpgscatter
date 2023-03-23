import numpy as np
import dearpygui.dearpygui as dpg

file = ""
x_left, y_left, x_span, y_span = 0, 0, 0, 0

def __framebuffer_callback(sender, user_data):
    w, h = user_data.get_width(), user_data.get_height()
    image = np.frombuffer(user_data, dtype=np.float32, count=w*h*4)
    image = np.reshape(image, (h, w, 4)) # reshape to row major
    image = image[y_left:y_left + y_span, x_left: x_left + x_span, :] # crop
    image = image.flatten() # back to 1D
    image[:] *= 255 # pct to 8-bit range value
    path = "./bin/" + file
    dpg.save_image(path, x_span, y_span, image)

def __crop_region_and_save(filepath, start, end):
    start, end = __clip_region(start, end)
    global file, x_left, y_left, x_span, y_span
    file = filepath
    x_left, x_right, y_left, y_right = start[0], end[0], start[1], end[1]
    x_span, y_span = abs(x_right-x_left), abs(y_right-y_left)
    dpg.output_frame_buffer(callback=__framebuffer_callback)
    
def __clip_region(start, end):
    # discretize and clip
    clip_x = np.clip([round(start[0]), round(end[0])], a_min=0, a_max=dpg.get_viewport_client_width())
    clip_y = np.clip([round(start[1]), round(end[1])], a_min=0, a_max=dpg.get_viewport_client_height())

    start = (clip_x[0], clip_y[0])
    end = (clip_x[1], clip_y[1])

    if start[0] > end[0]:
        end[0] = start[0]
    
    if start[1] > end[1]:
        end[1] = start[1]
    
    return start, end

def save_item(sender, user_data, args):
    plot_tag, filepath = args[0], args[1]
    start_x, start_y = dpg.get_item_pos(plot_tag)
    end_x, end_y = dpg.get_item_rect_size(plot_tag)
    __crop_region_and_save(filepath, (start_x, start_y), (start_x + end_x, start_y + end_y))