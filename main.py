# Link all the tournament functions into the GUI
import sqlite3

from kivy.lang import Builder
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.list import IRightBodyTouch

from utils import my_tourneys as dab

#commit before file organisation change : b4f34206d904d81f4b20490272ed8a3662de33c7


#TODO : link MDLists to tournament data then allow to create match up by selecting players from a pop up ?

class RightCheckbox(IRightBodyTouch, MDCheckbox):
    """Custom right container."""
    selection_items = []

    def on_active(self, rcb, value):
        """go up 2 levels to get the line and retrieve the ID from it with split"""
        p_id = self.parent.parent.text.split(" |")[0]
        screen_control = MDApp.get_running_app().root.get_screen("PlayersList")

        if value:
            print(p_id)
            screen_control.checkbox_check(value, p_id)
        else:
            print("false")
            screen_control.checkbox_check(value, p_id)


class RightCheckboxTourney(IRightBodyTouch, MDCheckbox):
    """Custom right container."""
    selection_items = []

    def on_active(self, rcb, value):
        """go up 2 levels to get the line and retrieve the ID from it with split"""
        t_id = self.parent.parent.text.split(" |")[0]
        screen_control = MDApp.get_running_app().root.get_screen("TourneyList")

        if value:
            print(t_id)
            screen_control.checkbox_check(value, t_id)
        else:
            print("false")
            screen_control.checkbox_check(value, t_id)


class ScreenManager(ScreenManager):
    ...


class TourneyApp(MDApp):
    tournament_id = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "DeepPurple"
        self.theme_cls.accent_hue = "300"

        try:
            dab.db_create()
        except sqlite3.OperationalError:
            pass

        sm = Builder.load_file("screens/tourney.kv")
        return sm

    def light_dark_change(self):
        """change the light or dark mode"""
        self.theme_cls.theme_style = "Light" if self.theme_cls.theme_style == "Dark" else "Dark"




if __name__ == "__main__":
    TourneyApp().run()