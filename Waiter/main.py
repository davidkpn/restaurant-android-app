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
import client as socket_client
import os
import sys

# my kivy version
kivy.require("1.11.1")

from kivy.core.window import Window

class ScrollableLabel(ScrollView):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))


    def add_text(self, text):
        self.text_label = Label(size_hint_y=None, height=40, markup=True)
        self.text_label.text = text
        self.text_label._label.refresh()
        self.text_label.height = self.text_label._label.texture.size[1]
        self.layout.clear_widgets()
        self.layout.add_widget(self.text_label)

class ScrollableLayout(ScrollView):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical')
        self.layout.size_hint_y = None
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)

    def add_item_to_scroll(self ,item):
        self.layout.add_widget(item)

    def delete_item(self, item):
        for row in self.layout.children:
            if row.children[4].text == item.children[4].text:
                self.layout.clear_widgets([row])
                for prod in waiter_app.invoice_page.inv_orders['products']:
                    if prod[0] == int(item.children[4].text):
                        waiter_app.invoice_page.inv_orders['products'].remove(prod)
                        waiter_app.invoice_page.total_order_price-=float(row.children[1].text)

class InvoicePage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.products = []
        self.categories = []
        self.invoice = None
        self.discount = 0
        self.inv_orders = {'products':[], 'ready':False}
        self.total_order_price = 0.0
        with self.canvas:
            Color(.3, .4, .4, .6)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda x,y:self.adjust_element_size(self.bg,self))

        self.orientation='horizontal'
        ##################*******************************
        # the left box contains current order, and the total invoice
        account_layout = BoxLayout(orientation='vertical')
        account_layout.size_hint_x = .4
        ##################################################
        # the top box contains total invoice
        self.order_box = BoxLayout(orientation='vertical', padding=10)

        self.account_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5, padding=5)
        self.account_title = TextInput()
        self.account_title.bind(text=self.title_changing)
        self.acc_dis_label = Label(text="discount:")
        self.account_discount = TextInput(text="0", size_hint_x=None, width=40)
        self.account_box.add_widget(self.account_title)
        self.account_box.add_widget(self.acc_dis_label)
        self.account_box.add_widget(self.account_discount)
        self.account_box.add_widget(Label(text="%", size_hint_x=None , width=30))
        self.order_box.add_widget(self.account_box)

        # Order Header
        self.order_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        self.order_header.add_widget(Label(text="ID"))
        self.order_header.add_widget(Label(text="Title"))
        self.order_header.add_widget(Label(text="Quantity"))
        self.order_header.add_widget(Label(text="Price"))
        self.order_header.add_widget(Label(text="Action"))
        self.order_header.bind(pos=self.update_order_header, size=self.update_order_header)
        with self.order_header.canvas:
            Color(.4, .7, .7, .6)
            self.order_header_bg = Rectangle(size=self.order_box.size, pos=self.order_box.pos)
        self.order_box.add_widget(self.order_header)

        # Order Items
        self.order_items = ScrollableLayout()

        self.order_box.add_widget(self.order_items)

        # Order actions
        self.order_buttons = BoxLayout(orientation="horizontal", padding=10, size_hint_y=None, height=50)
        btn_finish_order = Button(text="Finish order", size_hint_y=None, height=40)
        btn_finish_order.bind(on_press=self.finish_order)
        btn_cancel_order = Button(text="Cancel order", size_hint_y=None, height=40)
        btn_cancel_order.bind(on_press=self.cancel_order)
        self.order_buttons.add_widget(btn_finish_order)
        self.order_buttons.add_widget(btn_cancel_order)
        self.order_box.add_widget(self.order_buttons)

        account_layout.add_widget(self.order_box)

        ####################################################
        # the bottom box contains current order
        self.invoice_box = BoxLayout(orientation='vertical')
        ## the receipt
        receipt_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        receipt_layout.bind(minimum_height=receipt_layout.setter('height'))
        self.receipt = Label(size_hint_y=None, height=40, markup=True)

        receipt_layout.add_widget(self.receipt)
        receipt_scroll_view = ScrollView(size_hint=(1, None), size=(Window.size[0]*.4,Window.size[1]*.4))
        receipt_scroll_view.add_widget(receipt_layout)
        self.invoice_box.add_widget(receipt_scroll_view)
        ### invoice actions
        footer_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5, padding=5)

        footer_btn_delete = Button(text="delete account", size_hint_y=None, height=40)
        footer_btn_delete.bind(on_press=self.delete_account)
        footer_btn_pay = Button(text="PAY", size_hint_y=None, height=30)
        footer_btn_pay.bind(on_press=self.pay_account)
        footer_layout.add_widget(footer_btn_delete)
        footer_layout.add_widget(footer_btn_pay)


        self.invoice_box.add_widget(footer_layout)

        account_layout.add_widget(self.invoice_box)
        ##################*******************************
        self.add_widget(account_layout)
        ####################################################
        # Right box contains the products layout
        self.items_box = BoxLayout(orientation='vertical',padding=[20,10,0,5])# Padding of the text: [padding_left, padding_top, padding_right, padding_bottom].
        self.items_box.size_hint_x = .6

        self.items = StackLayout(orientation='lr-tb', spacing=5)
        # self.populate_item_selection('categories', None)
        self.items_box.add_widget(self.items)

        self.back_function = Button(text="back", size_hint_y=None, size_hint_x=None, height=40)
        self.back_function.bind(on_press=lambda x: self.populate_item_selection('categories',None))

        self.items_box.add_widget(self.back_function)
        self.add_widget(self.items_box)
        ####################################################


    def clear_fields(self):
        self.order_items.layout.clear_widgets()
        self.receipt.text=""
        self.inv_orders = {'products':[], 'ready':False}
        self.total_order_price=0.0
        for acc_btn in waiter_app.resturant_area_page.children[0].children:
            if acc_btn.invoice['ID'] == self.invoice['ID']:
                acc_btn.text = f"[color=452929][b]{self.invoice['title']}[/b][/color]"

        waiter_app.screen_manager.current = "Area"

    def pay_account(self, _):
        if len(self.invoice['orders'][-1]['products']) == 0:
            self.invoice['orders'].pop()
        for btn in waiter_app.resturant_area_page.children[0].children:
            if btn.invoice['ID'] == self.invoice['ID']:
                waiter_app.resturant_area_page.children[0].clear_widgets([btn])
                self.invoice['is_paid'] = 1
                update_invoice = {'method':'update_item', 'attributes':[self.invoice, 'invoices'], 'attribute_to_assign':'', 'class':None, 'type':''}
                Clock.schedule_once(lambda x:socket_client.send(update_invoice), .2)
        self.clear_fields()

    def delete_account(self, _):
        for btn in waiter_app.resturant_area_page.children[0].children:
            if btn.invoice['ID'] == self.invoice['ID']:
                waiter_app.resturant_area_page.children[0].clear_widgets([btn])
                delete_invoice = {'method':'delete_item', 'attributes':[self.invoice['ID'], 'invoices'], 'attribute_to_assign':'', 'class':None, 'type':''}
                Clock.schedule_once(lambda x:socket_client.send(delete_invoice), .2)
        self.clear_fields()

    def finish_order(self, _):
        self.invoice['total_price'] += self.total_order_price
        self.clear_fields()

        if len(self.invoice['orders'][-1]['products']) == 0:
            self.invoice['orders'].pop()
        #update
        update_invoice = {'method':'update_item', 'attributes':[self.invoice, 'invoices'], 'attribute_to_assign':'', 'class':None, 'type':''}
        Clock.schedule_once(lambda x:socket_client.send(update_invoice), .2)
        print("finish"*10)

    def cancel_order(self, _):
        self.clear_fields()
        self.invoice['orders'].pop()
        print(self.invoice['orders'])

    def title_changing(self, instance, value):
        if self.invoice is not None:
            self.invoice['title'] = value
            print(self.invoice)

    def set_invoice(self, invoice):
        self.invoice = invoice
        self.account_title.text = invoice['title']
        self.invoice['orders'].append(self.inv_orders)
        print(self.invoice['orders'])
        self.populate_receipt_text(self.invoice['orders'])

    def set_categories(self, categories):
        self.categories = categories
        self.populate_item_selection('categories', None)

    def set_products(self, products):
        self.products = products

    def add_text_receipt(self, text):
        if len(self.receipt.text)==0:
            total = f"""\n[b]discount: {self.account_discount.text}% \ntotal price: {self.invoice['total_price'] - self.invoice['total_price']*int(self.account_discount.text)/100}[/b]"""
            print(text)
            self.receipt.text += "[color=c8ccd1]" + text + "[/color]\n _" + total
        else:
            str = self.receipt.text.split('_')
            total = f"""_
            [b]discount: {self.account_discount.text}%
            total price: {self.invoice['total_price'] - self.invoice['total_price']*int(self.account_discount.text)}[/b]"""
            self.receipt.text =  str[0] + text + total

        self.receipt._label.refresh()
        self.receipt.height = self.receipt._label.texture.size[1]

    def populate_receipt_text(self, orders):

        str = ""
        for items in orders:
            for item in items['products']:
                print(item)
                prod = [prod for prod in self.products if prod['ID']==item[0]]
                if len(prod)>0:
                    print(prod)
                    prod=prod[0]
                    str += f"{prod['title']} X {item[1]}     {int(prod['price'])*item[1]}\n"
        self.add_text_receipt(str)

    def add_order_item(self, _item):
        for item in self.order_items.layout.children:
            if item.children[4].text == str(_item['ID']):
                item.children[2].text = str(int(item.children[2].text) + 1)
                item.children[1].text = str(float(item.children[1].text) + _item['price'])
                for prod in self.inv_orders['products']:
                    if prod[0] == _item['ID']:
                        prod[1] += 1
                # update database
                return

        item = BoxLayout(orientation='horizontal', size_hint=(1,None), height=30, spacing=5)
        item.add_widget(Label(text=str(_item['ID'])))
        item.add_widget(Label(text=_item['title']))
        item.add_widget(Label(text="1"))
        item.add_widget(Label(text=str(_item['price'])))
        btn_remove = Button(text="remove")
        btn_remove.bind(on_press=lambda x, item=item:self.order_items.delete_item(item))
        item.add_widget(btn_remove)
        self.order_items.add_item_to_scroll(item)
        self.inv_orders['products'].append([_item['ID'], 1])
        self.total_order_price += _item['price']
        #update Data base

    def update_order_header(self, instance, *_):
        self.order_header_bg.size=self.order_header.size
        self.order_header_bg.pos=self.order_header.pos

    def adjust_element_size(self, rect, element, *_):
        rect.size = element.size
        rect.pos = element.pos

    def populate_item_selection(self, type, id):
        self.items.clear_widgets()
        if type=='categories':
            for cat in self.categories:
                btn = Button(text=cat['title'], size_hint=(.3,.2))
                btn.background_normal = cat['picture_path']
                btn.bind(on_press=lambda x, id=cat['ID']:self.populate_item_selection('products', id))
                self.items.add_widget(btn)
        else:
            for prod in self.products:
                if prod['category_id']==id:
                    btn = Button(text=prod['title'], size_hint=(.3,.2))
                    btn.bind(on_press=lambda x, prod=prod:self.add_order_item(prod))
                    btn.background_normal = prod['picture_path']
                    self.items.add_widget(btn)

class DraggableButton(Button):
    def __init__(self, text, id, type,**kwargs):
        super().__init__(text=text, **kwargs)
        self.size_hint = (.2,.2)
        self.border: (2, 2, 2, 2)
        self.markup = True
        self.ID = id
        self.invoice = {"ID": None, "title": "" ,"orders": [], "total_price":0.0, "create_datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), "is_paid":0, "session_id":1}
        if type=="table":
            self.background_normal = './assets/table.png'
        else:
            self.background_normal = f'./assets/person{randint(1,4)}.png'
        self.font_size=20

    def set_invoice(self, invoice):
        self.invoice = invoice
        print(self.invoice)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            pass
        else:
            super(DraggableButton, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            self.pos = (self.pos[0]+touch.dx, self.pos[1]+touch.dy)
        else:
            return super(DraggableButton, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if abs(touch.x - touch.ox) < 1 and abs(touch.y - touch.oy) < 1:
                Clock.schedule_once(lambda x: waiter_app.resturant_area_page.show_invoices(self), .2)
        else:
            super(DraggableButton, self).on_touch_up(touch)


class ResturantAreaPage(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.empty_invoice = {"ID": None, "title": "" ,"orders": [], "total_price":0.0, "create_datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), "is_paid":0, "session_id":1}
        self.ID = 1

        self.orientation='lr-tb'

        self.btn_table = Button(text="add table",size_hint=(.1, .1))
        self.btn_table.bind(on_press=self.add_table)
        self.add_widget(self.btn_table)

        self.btn_client = Button(text="add client",size_hint=(.1, .1))
        self.btn_client.bind(on_press=self.add_client)
        self.add_widget(self.btn_client)

        self.flayout = FloatLayout(size=(Window.size[0],Window.size[1]*.9))

        self.add_widget(self.flayout)
        socket_client.start_listening(incoming_data, show_error)
        # method = function of the api
        # attributes = attributes for the api function
        # attribute_to_assign = the method / variable to manipulate in the main.py
        # class = which screen to reach
        # type = get or set, get=method, set=variable
        request_cat = {'method':'get_all_items', 'attributes':['categories'], 'attribute_to_assign':'set_categories', 'class':'InvoicePage', 'type':'get'}
        request_prod = {'method':'get_all_items', 'attributes':['products'], 'attribute_to_assign':'set_products', 'class':'InvoicePage', 'type':'get'}
        Clock.schedule_once(lambda x:socket_client.send(request_cat), .2)
        Clock.schedule_once(lambda x:socket_client.send(request_prod), .2)

    def add_table(self, _):
        self.empty_invoice['title'] = f"table {self.ID}"
        table = DraggableButton(text=f"[color=452929][b]{self.empty_invoice['title']}[/b][/color]", id=self.ID, type="table")
        table.bind(on_press=lambda x:self.show_invoices(table))
        self.flayout.add_widget(table)
        request_add_invoice = {'method':'add_item', 'attributes':[self.empty_invoice, 'invoices'], 'attribute_to_assign':self.ID, 'class':'DraggableButton', 'type':'set'}
        self.ID +=1
        Clock.schedule_once(lambda x:socket_client.send(request_add_invoice), .2)

    def add_client(self, _):
        self.empty_invoice['title'] = f"client {self.ID}"
        client = DraggableButton(text=f"[color=452929][b]{self.empty_invoice['title']}[/b][/color]", id=self.ID, type="client")

        client.bind(on_press=lambda x:self.show_invoices(client))
        self.flayout.add_widget(client)
        request_add_invoice = {'method':'add_item', 'attributes':[self.empty_invoice, 'invoices'], 'attribute_to_assign':self.ID, 'class':'DraggableButton', 'type':'set'}
        self.ID +=1
        Clock.schedule_once(lambda x:socket_client.send(request_add_invoice), .2)

    def show_invoices(self, account):
        waiter_app.screen_manager.current = "Invoice"
        waiter_app.invoice_page.set_invoice(account.invoice)

    def adjust_element_size(self, rect, element, *_):
        rect.size = element.size
        rect.pos = element.pos



class ConnectPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = 200
        self.spacing = 10
        self.cols = 2

        if os.path.isfile("prev_details.txt"):
            with open("prev_details.txt", "r") as f:
                data = f.read().split(",")
                prev_ip = data[0]
                prev_port = data[1]
                prev_username = data[2]
        else:
                prev_ip = ""
                prev_port = ""
                prev_username = ""

        self.add_widget(Label(text="IP:"))

        self.ip = TextInput(text=prev_ip,multiline=False)
        self.add_widget(self.ip)

        self.add_widget(Label(text="PORT:"))

        self.port = TextInput(text=prev_port,multiline=False)
        self.add_widget(self.port)

        self.add_widget(Label(text="USERNAME:"))

        self.username = TextInput(text=prev_username,multiline=False)
        self.add_widget(self.username)

        self.add_widget(Label())

        self.submit = Button(text="submit")
        self.submit.bind(on_press=self.connect_to_server)
        self.add_widget(self.submit)

    def connect_to_server(self, instance):
        port = self.port.text
        ip = self.ip.text
        username = self.username.text

        with open("prev_details.txt", "w") as f:
            f.write(f"{ip},{port},{username}")

        info = f"attemts to join{ip}:{port} as {username}"
        waiter_app.info_page.update_info(info)
        waiter_app.screen_manager.current = "Info"
        Clock.schedule_once(self.connect, 1)

    def connect(self, _):
        port = int(self.port.text)
        ip = self.ip.text
        username = self.username.text
        if not socket_client.connect(ip, port, username, show_error):
            return
        waiter_app.create_resturant_area_page()
        waiter_app.screen_manager.current = "Area"


class InfoPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.message = Label(halign="center", valign="middle", font_size=30)
        self.message.bind(width=self.update_text_width)
        self.add_widget(self.message)

    def update_info(self, message):
        self.message.text = message

    def update_text_width(self, *_):
        self.message.text_size = (self.message.width*.9, None)


class WaiterApp(App):
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

    def create_resturant_area_page(self):
        self.resturant_area_page = ResturantAreaPage()
        screen = Screen(name="Area")
        screen.add_widget(self.resturant_area_page)
        self.screen_manager.add_widget(screen)

        self.invoice_page = InvoicePage()
        screen = Screen(name="Invoice")
        screen.add_widget(self.invoice_page)
        self.screen_manager.add_widget(screen)


def show_error(message):
    print(message)
    waiter_app.info_page.update_info(message)
    waiter_app.screen_manager.current = "Info"
    Clock.schedule_once(sys.exit, 10)

def incoming_data(data):
    if data['class'] == 'ResturantAreaPage':
        screen_to_send = self
    elif data['class'] == 'InvoicePage':
        screen_to_send = waiter_app.invoice_page
    elif data['class'] == 'DraggableButton':
        for btn in waiter_app.resturant_area_page.children[0].children:
            if btn.ID == data['attribute_to_assign']:
                print(btn, data['data'])
                btn.invoice = data['data']
        return
    elif data['class'] is None:
        return
    if data['type']=='set':
        setattr(screen_to_send, data['attribute_to_assign'], data['data'] )
    else:
        getattr(screen_to_send, data['attribute_to_assign'])(*[data['data']])

if __name__ == "__main__":
    waiter_app = WaiterApp()
    waiter_app.run()
