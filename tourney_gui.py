# Link all the tournament functions into the GUI
from kivy.lang import Builder


from kivymd.app import MDApp
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

class ScreenManager(ScreenManager):
    ...

# runner =  Builder.load_file("tourney.kv")

class TourneyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"

        # return runner

if __name__ == "__main__":
    TourneyApp().run()






