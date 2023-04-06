# Link all the tournament functions into the GUI
from kivy.lang import Builder
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import OneLineListItem
from kivymd.uix.pickers import MDDatePicker





class MainPage(Screen):
    ...


class PlayersList(Screen):
    def __init__(self, **kwargs):
        super(PlayersList, self).__init__(**kwargs)


    def feed_list(self):
        # ToDO: replace code with sql query of all players
        curr_screen = self.parent.get_screen('PlayersList')
        for x in range(10):
            curr_screen.ids.players_list.add_widget(
                OneLineListItem(text=f"Single-line item {x}")
            )



class TourneyList(Screen):
    def __init__(self, **kwargs):
        super(TourneyList, self).__init__(**kwargs)


    def on_save(self, instance, value, date_range):
        """
        event called when the "ok" dialog boc button is clicked
        :type instance: <kivymd.uix.picker.MDDatePicker object>;
        :param value: selected date;
        :type value: <class 'datetime.date'>;
        :param date_range: list of 'datetime.date' objects in the selected range;
        :type date_range: <class 'list'>;
        """

        curr_screen = self.parent.get_screen('TourneyList')
        curr_screen.ids.search_tourney_date.text = str(value)

    def on_cancel(self, instance, value):
        """
        Events called when the "CANCEL" dialog box button is clicked.'
        """
        print("canceled")

    def show_date_picker(self):
        date_dialog = MDDatePicker(min_year=2022, max_year=2030)
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()


    def tourney_search(self):
        #TODO: make the function feed the players list without the error
        curr_screen = self.parent.get_screen('TourneyList')
        for x in range(10):
            curr_screen.ids.players_list.add_widget(
                OneLineListItem(text=f"Single-line item {x}")
            )

class NewTourney(Screen):
    def __init__(self, **kwargs):
        super(NewTourney, self).__init__(**kwargs)

    def on_save(self, instance, value, date_range):
        """
        event called when the "ok" dialog boc button is clicked
        :type instance: <kivymd.uix.picker.MDDatePicker object>;
        :param value: selected date;
        :type value: <class 'datetime.date'>;
        :param date_range: list of 'datetime.date' objects in the selected range;
        :type date_range: <class 'list'>;
        """

        curr_screen = self.parent.get_screen('NewTourney')
        curr_screen.ids.test.text = str(value)

    def on_cancel(self, instance, value):
        """
        Events called when the "CANCEL" dialog box button is clicked.'
        """
        print("canceled")

    def show_date_picker(self):
        date_dialog = MDDatePicker(min_year=2022, max_year=2030)
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()



class TournamentScreen(Screen):
    ...


class RoundScreen(Screen):
    ...


class StandingsScreen(Screen):
    ...

class ScreenManager(ScreenManager):
    ...


class TourneyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "DeepPurple"
        self.theme_cls.accent_hue = "300"

        Builder.load_file("new_tourney.kv")
        Builder.load_file("search_tourney.kv")
        Builder.load_file("players.kv")
        Builder.load_file("tourney.kv")

    def player_search(self):
        #Because of the screen system, calling function returns an empty list
        #you need to use the root.get_screen('name of screen') to access it like you would access root.
        curr_screen = self.root.get_screen('PlayersList')
        #ToDO: replace code with sql query of all players
        for x in range(10):
            curr_screen.ids.players_list.add_widget(
                OneLineListItem(text=f"Single-line item {x}")
            )


    def light_dark_change(self):
        """change the light or dark mode"""
        self.theme_cls.theme_style = "Light" if self.theme_cls.theme_style == "Dark" else "Dark"


if __name__ == "__main__":
    TourneyApp().run()






