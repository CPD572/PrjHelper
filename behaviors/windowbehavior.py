from kivy.core.window import Window

def adapt_window(new_size, left_top_cords=None):
    new_width, new_height = new_size
    old_width, old_height = Window.size
    if not left_top_cords:
        Window.left, Window.top = (Window.left-(new_width-old_width)/2,Window.top-(new_height-old_height)/2)
    else:
        Window.left, Window.top = left_top_cords
    Window.size = (new_width, new_height)
    
    
def isNewWindowBigger(new_size):
    return Window.size > new_size