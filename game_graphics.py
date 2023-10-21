import pyglet


class MyGUI:

    MOUSE_LEFT = pyglet.window.mouse.LEFT
    MOUSE_MIDDLE = pyglet.window.mouse.MIDDLE
    MOUSE_RIGHT = pyglet.window.mouse.RIGHT

    images = {}

    def __init__(self):
        self.window = None
        self.background = None
        self.sprites = []
        self.batch = pyglet.graphics.Batch()


    def load_images(self, path):

        pyglet.resource.path = [path]  
        MyGUI.images["0"] = pyglet.resource.image("box_empty.png")
        for i in range(1, 9):
            MyGUI.images[str(i)] = pyglet.resource.image(f"box_{i}.png")
        MyGUI.images["x"] = pyglet.resource.image("box_mine.png")
        MyGUI.images[" "] = pyglet.resource.image("box_back.png")
        MyGUI.images["f"] = pyglet.resource.image("box_flag.png")
 

    def create_window(self, width=800, height=600):
        self.window = pyglet.window.Window(width, height, resizable=False)
        
            
    def start(self):
        pyglet.app.run()


    def end(self):
        self.window.close()
        pyglet.app.exit()


    def draw_grid(self):
        self.batch.draw()
        self.sprites.clear()


    def clear_window(self):
        self.window.clear()
    

    def add_tile(self, key, x, y):
        image = MyGUI.images[str(key)]

        self.sprites.append(pyglet.sprite.Sprite(
            image,
            x,
            y,
            batch = self.batch
        ))

    
    def draw_text(self, text, x, y, text_color=(0, 0, 0, 255), text_font="arial", size=32):

        label = pyglet.text.Label(text,
            font_name=text_font,
            font_size=size,
            color=text_color,
            x=x, y=y,
            anchor_x="left", anchor_y="bottom"
        )
        
        label.draw()


    def set_mouse_handler(self, handler):
        if self.window:
            self.window.on_mouse_press = handler
        else:
            print("Could not set mouse handler because window is null")



    def set_draw_handler(self, handler):

        if self.window:
            self.window.on_draw = handler
        else:
            print("Could not set draw handler because window is null")
