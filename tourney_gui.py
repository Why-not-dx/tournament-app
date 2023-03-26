# Link all the tournament functions into the GUI

import my_tourneys as mt
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivy.uix.screenmanager import ScreenManager, Screen



class MainPage(Screen):
    ...


class PlayersList(Screen):
    ...


class TourneyList(Screen):
    ...


class NewTourney(Screen):
    ...


class TournamentScreen(Screen):
    ...


class RoundScreen(Screen):
    ...


class StandingsScreen(Screen):
    ...

class TourneyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "DeepPurple"
        my_screens = (MainPage, PlayersList, TourneyList, NewTourney, TournamentScreen, RoundScreen, StandingsScreen)
        self.sm = ScreenManager()

        for i in my_screens:
            self.sm.add_widget(i(name=i.__name__))

        return self.sm


if __name__ == "__main__":
    TourneyApp().run()




