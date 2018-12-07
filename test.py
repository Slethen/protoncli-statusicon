import wx
import commands
import requests
import json
import time
from threading import Thread
import sys

# define our basic information
TRAY_TOOLTIP = 'ProtonVPN-CLI Status'
TRAY_ICON_CONNECTED = 'connected.png'
TRAY_ICON_DISCONNECTED = 'disconnected.png'

# Initialise networkChanged
# Variable used to store connection state after each run of the status function.
# Only when variable changes will the UI update to prevent locking the UI.
global networkChanged
networkChanged = False

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
        self.set_icon(TRAY_ICON_CONNECTED)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

        # Start thread for connectionStatus
        self.thread = Thread(target=self.status)
        self.thread.daemon = True
        self.thread.start()

    # Get ProtonVPN connection status from API
    def status(self):
        global networkChanged
        retries = 1
        while True:
            print "Current Status", str(networkChanged) + " - No UI update"
            try:
                time.sleep(2)
                send_url = 'http://dl.slethen.io/api.php'
                r = requests.get(send_url)
                j = json.loads(r.text)

                if str(j) != networkChanged:
                    networkChanged = str(j)

                    if "True" in str(j):
                        print "ProtonVPN Connected - Update UI"
                        self.set_icon(TRAY_ICON_CONNECTED)

                    if "False" in str(j):
                        print "ProtonVPN Disconnected - Update UI"
                        self.set_icon(TRAY_ICON_DISCONNECTED)

            except Exception as e:
                wait = retries * 1;
                print 'Error! Waiting %s secs and re-trying...' % wait
                sys.stdout.flush()
                time.sleep(wait)
                retries += 1

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