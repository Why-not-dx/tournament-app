import kivy
from kaki.app import App
from kivy.factory import Factory
from kivymd.app import MDApp
import os

class MainApp(App, MDApp):

    CLASSES = {
        "TourneyApp": "tourney_gui"
    }

    AUTORELOADER_PATHS = [
        (".", {"recursive": True})

    ]

    KV_FILES = {
        os.path.join(os.getcwd(), "tourney.kv")
    }

    def build_app(self):
        return Factory.TourneyApp()

MainApp().run()

# "MainPage": "tourney_gui",
# "PlayersList": "tourney_gui",
# "TourneyList": "tourney_gui",
# "NewTourney": "tourney_gui",
# "TournamentScreen": "tourney_gui",
# "RoundScreen": "tourney_gui",
# "StandingsScreen": "tourney_gui",