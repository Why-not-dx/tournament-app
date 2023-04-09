# Link all the tournament functions into the GUI
import sqlite3
import my_tourneys as dab
import pairing as pr
from sqlite3 import OperationalError
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.list import OneLineListItem
from kivymd.uix.pickers import MDDatePicker
from kivy.metrics import dp


class MainPage(Screen):
    ...


class PlayersList(Screen):
    def __init__(self, **kwargs):
        super(PlayersList, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        """when loading the page, adds on the list of all players in the app"""
        super().on_pre_enter(*args)
        self.feed_list()


    def feed_list(self, p_id=None, p_name=None, p_surname=None):
        """
        Checks nature of the call, if empty, returns all players in list
        If not empty, will either perform name search or tournament participation search
        Clears the list after every call
        """
        curr_screen = self.parent.get_screen('PlayersList')
        if not any((p_id, p_name, p_surname)):
            players_list = dab.read_players()
            for player in players_list:
                curr_screen.ids.players_list.add_widget(
                    OneLineListItem(
                        text=f"{player[0]} | {player[1]}  |  {player[2]}",
                        bg_color=(122/255, 48/255, 108/255, .1)
                    )
                )

        elif p_id:
            curr_screen.ids.players_list.clear_widgets()
            players_list = dab.get_players_from_id(p_id)

            for player in players_list:
                curr_screen.ids.players_list.add_widget(
                    OneLineListItem(
                        text=f"{player[0]} | {player[1]}  |  {player[2]}",
                        bg_color=(122/255, 48/255, 108/255, .1)
                    )
                )

        elif p_name or p_surname:
            curr_screen.ids.players_list.clear_widgets()
            players_list = dab.get_players_id(
                [p_name, p_surname]
            )
            for player in players_list:
                curr_screen.ids.players_list.add_widget(
                    OneLineListItem(
                        text=f"{player[0]} | {player[1]}  |  {player[2]}",
                        bg_color=(122/255, 48/255, 108/255, .1)
                    )
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

    def on_pre_enter(self, *args):
        super().on_pre_enter(self, *args)

        self.feed_list()

    def feed_list(self, t_id=None, t_date=None, t_name=None):
        """feed the list of tournaments in the scrollview / MDList of
        id = tourney_list
        if a search is returning nothing, the function breaks and returns the code
        False and will not affect the page + launch a pop up saying nothing was found
        """
        curr_screen = self.parent.get_screen('TourneyList')
        if not any((t_id, t_date, t_name)):
            curr_screen.ids.tourney_list.clear_widgets()
            tourney_list = dab.get_tourneys_list()
            for tour in tourney_list:
                curr_screen.ids.tourney_list.add_widget(
                    OneLineListItem(
                        text=f"{tour[0]} | {tour[2]}  |  {tour[3]}",
                        bg_color=(122 / 255, 48 / 255, 108 / 255, .1)
                    )
                )

        elif t_id:
            curr_screen.ids.tourney_list.clear_widgets()
            tourney_list = dab.get_tourneys_list(t_id)
            if not tourney_list:
                return print("False")

            for tour in tourney_list:
                curr_screen.ids.tourney_list.add_widget(
                    OneLineListItem(
                        text=f"{tour[0]} | {tour[2]}  |  {tour[3]}",
                        bg_color=(122 / 255, 48 / 255, 108 / 255, .1)
                    )
                )

        elif t_date:
            curr_screen.ids.tourney_list.clear_widgets()
            players_list = dab.get_tourneys_list((t_date,))
            for tour in players_list:
                curr_screen.ids.tourney_list.add_widget(
                    OneLineListItem(
                        text=f"{tour[0]} | {tour[2]}  |  {tour[2]}",
                        bg_color=(122 / 255, 48 / 255, 108 / 255, .1)
                    )
                )

    def on_cancel(self, instance, value):
        """
        Events called when the "CANCEL" dialog box button is clicked.'
        """
        print("canceled")

    def show_date_picker(self):
        date_dialog = MDDatePicker(min_year=2022, max_year=2030)
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()


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



class TournamentScreen(Screen):
    def __init__(self, **kwargs):
        super(TournamentScreen, self).__init__(**kwargs)

    def tourney_search(self):
        #TODO: make the function feed the players list without the error
        curr_screen = self.parent.get_screen('TournamentScreen')
        for x in range(10):
            curr_screen.ids.rounds_list.add_widget(
                OneLineListItem(text=f"Single-line item {x}")
            )

    def add_table(self):

        self.data_tables = MDDataTable(
            size_hint=(1, 1),
            pos_hint={"center_y": .5, "center_x": .5},
            use_pagination=True,
            check=True,
            # name column, width column, sorting function column(optional), custom tooltip
            column_data=[
                ("No.", dp(25), None, "Custom tooltip"),
                ("Status", dp(25)),
                ("Signal Name", dp(25)),
                ("Severity", dp(25)),
                ("Stage", dp(25)),
                ("Schedule", dp(25), lambda *args: print("Sorted using Schedule")),
                ("Team Lead", dp(25)),
            ],
        )
        self.popuptable = Popup(
            title="Standings - round X",
            content=self.data_tables,
            size_hint=(.8, .8)
        )
        self.popuptable.open()




class ScreenManager(ScreenManager):
    ...


class TourneyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "DeepPurple"
        self.theme_cls.accent_hue = "300"
        try:
            dab.db_create()
        except sqlite3.OperationalError:
            pass

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