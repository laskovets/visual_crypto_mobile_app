from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.config import ConfigParser
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout as Layout
from tools import *


class image_storage:
    current_image = None

    def __init__(self, current_image=None):
        self.current_image = current_image


IS = image_storage()


current_image = None


Builder.load_string("""
<SelectShadow>:
    id: select_shadow
    #FileChooserIconView:
    FileChooserListView:
        id: filechooser
        rootpath: '/storage/emulated/0/'
        on_selection: select_shadow.selected(*args)
""")


class MenuScreen(Screen):

    def __init__(self, **kw):
        super(MenuScreen, self).__init__(**kw)
        box = BoxLayout(orientation='vertical')
        box.add_widget(Button(text='select shadow', on_press=lambda x:
                              set_screen('select_shadow')))
        box.add_widget(Button(text='use camera',
                              on_press=lambda x: set_screen('use_camera')))
        self.add_widget(box)


Builder.load_string('''
<KivyCamera>:
    orientation: 'horizontal'
    Camera:
        id: camera
        resolution: (640, 480)
        size: (64, 48)
        pos: (-1680, -1680)
        play: True
        # canvas.before:
        #     PushMatrix
        #     Rotate:
        #         angle: -90
        #         origin: self.center
        # canvas.after:
        #     PopMatrix
    Image:
        id: image
        # size_hint_x: 2.0
        pos: (0, 0)
        width: 240
        allow_stretch: True
        canvas.before:
            PushMatrix
            Rotate:
                angle: -90
                origin: self.center
        canvas.after:
            PopMatrix

''')


class KivyCamera(Layout):
    def __init__(self, fps, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        # self.camera = Camera(resolution=(640, 480), size=(64,48), play=True, id='camera')
        Clock.schedule_interval(self.update, 1.0 / 30)

    def update(self, dt):
        try:
            camera = self.ids['camera']
            self.snapshot = camera.texture
            if self.snapshot != None:

                image = self.ids['image']
                nparr = np.fromstring(camera.texture.pixels, dtype=np.uint8).copy()
                a = np.reshape(nparr, (480, 640, 4))
                texture = Texture.create(size=(a.shape[1], a.shape[0]), colorfmt='rgba')
                # TODO: PROCESS FRAME HERE
                image2 = cv2.imread(IS.current_image)
                image2 = cv2.flip(image2, 1)
                # image2 = cv2.imread('/home/alex/Загрузки/test.jpg')
                image2 = cv2.rotate(image2, cv2.ROTATE_90_COUNTERCLOCKWISE)
                b_c, g_c, r_c = cv2.split(image2)
                a_c = np.ones(b_c.shape, dtype=b_c.dtype) * 100
                image2 = cv2.merge((b_c, g_c, r_c, a_c))
                Logger.info('\n\n\n\n{}\n\n\n\n'.format(image2.shape))
                shadow = out_shadow(a, image2)
                Logger.info('\n\n\n\n{}\n\n\n\n'.format(IS.current_image))
                res = blend_transparent(a, shadow)
                b_c, g_c, r_c = cv2.split(res)
                a_c = np.ones(b_c.shape, dtype=b_c.dtype) * 100
                res = cv2.merge((b_c, g_c, r_c, a_c))
                ##########################
                texture.blit_buffer(res.tostring(), bufferfmt='ubyte', colorfmt="rgba")
                image.texture = texture

        except Exception as e:
            Logger.error('\n\n\n\n{}\n\n\n\n'.format(e))
            camera = self.ids['camera']
            nparr = np.fromstring(camera.texture.pixels, dtype=np.uint8).copy()
            a = np.reshape(nparr, (480, 640, 4))
            texture = Texture.create(size=(a.shape[1], a.shape[0]), colorfmt='rgba')
            texture.blit_buffer(a.tostring(), bufferfmt='ubyte', colorfmt="rgba")
            image.texture = texture


class SelectShadow(Screen):

    def selected(self, *args):
        # self.ids.image.source = filename[0]
        global IS
        sel = self.ids["filechooser"]
        IS.current_image = sel.selection[0]
        set_screen('menu')


class UseCamera(Screen):

    def __init__(self, **kwargs):
        super(UseCamera, self).__init__(**kwargs)
        self.add_widget(KivyCamera(fps=30))

    # def on_enter(self, *args):
    #     # self.camera_object.play = True
    #     camera = self.ids['camera']
    #     camera.play = True
    #
    # def on_leave(self, *args):
    #     camera = self.ids['camera']
    #     camera.play = False


def set_screen(name_screen):
    sm.current = name_screen


sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(SelectShadow(name='select_shadow'))
sm.add_widget(UseCamera(name='use_camera'))


class ShadowFinderApp(App):

    def __init__(self, **kvargs):
        super(ShadowFinderApp, self).__init__(**kvargs)
        self.config = ConfigParser()

    def get_application_config(self):
        return super(ShadowFinderApp, self).get_application_config(
            '{}/%(appname)s.ini'.format(self.directory))

    def build(self):
        return sm


if __name__ == '__main__':
    ShadowFinderApp().run()
