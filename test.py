import wx
import commands
import requests
import json
import time
from threading import Thread
import schedule

# define our basic information
TRAY_TOOLTIP = 'ProtonVPN-CLI Status'
TRAY_ICON_CONNECTED = 'connected.png'
TRAY_ICON_DISCONNECTED = 'disconnected.png'

if 'openvpn' in commands.getoutput('ps -A'):
    print 'Your process is running.'

# let's set up our window functions
def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item

class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON_DISCONNECTED)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

        # Start thread for status function
        self.thread = Thread(target=self.status)
        self.thread.daemon = True
        self.thread.start()

    # Get current status then set TRY_ICON
    def status(self):
        while True:
            try:
                time.sleep(2)
                send_url = 'http://dl.slethen.io/api.php'
                r = requests.get(send_url)
                j = json.loads(r.text)

                if "True" in str(j):
                    self.set_icon(TRAY_ICON_CONNECTED)

                if "False" in str(j):
                    self.set_icon(TRAY_ICON_DISCONNECTED)
            except Exception as e: print(e), "Error in status function"

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Say Hello', self.on_hello)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        print 'Tray icon was left-clicked.'
        while True:
            time.sleep(2)
            send_url = 'http://dl.slethen.io/api.php'
            r = requests.get(send_url)
            j = json.loads(r.text)

            if "True" in str(j):
                print 'True'
                self.set_icon(TRAY_ICON_CONNECTED)

            if "False" in str(j):
                print 'False'
                self.set_icon(TRAY_ICON_DISCONNECTED)

    def on_hello(self, event):
        print 'Hello, world!'

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self.frame.Close()

class App(wx.App):
    def OnInit(self):
        frame=wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        return True

def main():
    app = App(False)
    app.MainLoop()

if __name__ == '__main__':
    main()
