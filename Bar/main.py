import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.image import Image
from kivy.lang import Builder
from random import randint
import time
import server as socket_server
import os
from API import Api
# my kivy version
kivy.require("1.11.1")

from kivy.core.window import Window


class Bone(BoxLayout):
    def __init__(self, text, invoice, order, **kwargs):
        super().__init__(**kwargs)
        self.size_hint=(.333, None)
        self.height=250
        self.invoice = invoice
        self.order = order
        self.orientation = 'vertical'

        self.layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        a = Label(text=text, size_hint=(1, None))
        a._label.refresh()
        a.size = a._label.texture.size
        self.layout.add_widget(a)

        self.scrollview = ScrollView(size_hint=(1, None), size=(self.width, self.height-50))
        self.scrollview.add_widget(self.layout)

        btn_ready = Button(text="ready", size_hint_y=None, height=40)
        btn_ready.bind(on_press=self.order_ready)

        self.add_widget(btn_ready)
        self.add_widget(self.scrollview)

    def order_ready(self, _):
        for ord in self.invoice['orders']:
            if ord == self.order:
                ord['ready'] = True
                #api update invoice
                api.update_item(self.invoice, 'invoices')
                #delete the bone from the parent layout
                bar_app.bar_bones.layout.clear_widgets([self])
        pass


class BarBones(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.products = api.get_all_items('products')
        self.size_hint=(1, None)
        self.size=(Window.width, Window.height)
        self.layout = StackLayout(orientation='lr-tb', spacing=10, size_hint_y=None, padding=10)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)
        Clock.schedule_interval(self.update_bones, 5)



    def update_bones(self, _):
        invoices = api.get_all_items('invoices')
        self.layout.clear_widgets()
        for inv in invoices:
            for order in inv['orders']:
                if not order['ready']:
                    # create a bone layout
                    str = inv['title'] + " - \n\n\n"
                    # add scroll view and accept button
                    for product in order['products']:
                        prod = [prod for prod in self.products if prod['ID'] == product[0]]
                        if len(prod)>0:
                            prod = prod[0]
                            str += f"\n{prod['title']} X {product[1]}"
                    bone = Bone(str, inv, order)
                    self.layout.add_widget(bone)




class ConnectPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = 200
        self.spacing = 10
        self.cols = 3

        self.add_widget(Label(text="USERNAME:", size_hint_y=None, height=40))

        self.username = TextInput(text="",multiline=False, size_hint_y=None, height=40)
        self.add_widget(self.username)

        self.submit = Button(text="start session", size_hint_y=None, height=40)
        self.submit.bind(on_press=self.start_server)
        self.add_widget(self.submit)

    def start_server(self, instance):
        socket_server.start_server(connected, None)
        info = f"waitng for {self.username.text} to connect: {socket_server.IP}"
        bar_app.info_page.update_info(info)
        bar_app.screen_manager.current = "Info"


class InfoPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.message = Label(halign="center", valign="middle", font_size=30)
        self.message.bind(width=self.update_text_width)
        self.add_widget(self.message)
        Clock.schedule_interval(connected, 1)


    def update_info(self, message):
        self.message.text = message

    def update_text_width(self, *_):
        self.message.text_size = (self.message.width*.9, None)

def connected(time):
    print(socket_server.CONNECTED)
    if socket_server.CONNECTED:
        Clock.unschedule(connected)
        Clock.schedule_once(bar_app.create_bar_bones_page,1)

class BarApp(App):
    # the initialize method
    def build(self):
        self.screen_manager = ScreenManager()

        self.connect_page = ConnectPage()
        screen = Screen(name="Connect")
        screen.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen)

        self.info_page = InfoPage()
        screen = Screen(name="Info")
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

    def create_bar_bones_page(self, time):
        self.bar_bones = BarBones()
        screen = Screen(name="Bar")
        screen.add_widget(self.bar_bones)
        self.screen_manager.add_widget(screen)
        bar_app.screen_manager.current = "Bar"


if __name__ == "__main__":
    api = Api()
    bar_app = BarApp()
    bar_app.run()
