# Link all the tournament functions into the GUI
import sqlite3

from kivy.properties import ObjectProperty
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox
import my_tourneys as dab
import pairing as pr
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.list import OneLineListItem, OneLineAvatarIconListItem, IconLeftWidget, IRightBodyTouch
from kivymd.uix.pickers import MDDatePicker
from kivy.metrics import dp


#TODO : link MDLists to tournament data then allow to create match up by selecting players from a pop up ?

class RightCheckbox(IRightBodyTouch, MDCheckbox):
    """Custom right container."""

    selection_items = []

    def on_active(self, rcb, value):
        """go up 2 levels to get the line and retrieve the ID from it with split"""
        p_id = self.parent.parent.text.split(" |")[0]
        myapp = MDApp.get_running_app().root.get_screen("PlayersList")

        if value:
            print(p_id)
            myapp.checkbox_check(value, p_id)
        else:
            print("false")
            myapp.checkbox_check(value, p_id)



class MainPage(Screen):
    ...


class PlayersList(Screen):
    def __init__(self, **kwargs):
        super(PlayersList, self).__init__(**kwargs)
        self.dialog = None
        self.players_check = []

    def on_pre_enter(self, *args):
        """when loading the page, adds on the list of all players in the app"""
        super().on_pre_enter(*args)
        self.feed_list()
        self.clear_texts()

    def clear_texts(self):
        """emptying boxes of the page"""
        self.ids.search_id.text = ""
        self.ids.search_name.text = ""
        self.ids.search_surname.text = ""

    def feed_list(self, p_id=None, p_name=None, p_surname=None):
        """
        Checks nature of the call, if empty, returns all players in list
        If not empty, will either perform name search or tournament participation search
        Clears the list after every call
        """
        curr_screen = self.parent.get_screen('PlayersList')
        if not any((p_id, p_name, p_surname)):
            curr_screen.ids.players_list.clear_widgets()
            players_list = dab.read_players()
            for player in players_list:
                curr_screen.ids.players_list.add_widget(
                    OneLineAvatarIconListItem(
                        IconLeftWidget(icon="account"),
                        RightCheckbox(),
                        text=f"{player[0]} | {player[1]}  |  {player[2]}",
                        bg_color=(122 / 255, 48 / 255, 108 / 255, .1)
                    )
                )

        elif p_id:
            curr_screen.ids.players_list.clear_widgets()
            players_list = dab.get_players_from_id(p_id)

            for player in players_list:
                curr_screen.ids.players_list.add_widget(
                    OneLineAvatarIconListItem(
                        IconLeftWidget(icon="account"),
                        text=f"{player[0]} | {player[1]}  |  {player[2]}",
                        bg_color=(122 / 255, 48 / 255, 108 / 255, .1)
                    )
                )

        elif p_name or p_surname:
            curr_screen.ids.players_list.clear_widgets()
            players_list = dab.get_players_id(
                [p_name, p_surname]
            )
            for player in players_list:
                curr_screen.ids.players_list.add_widget(
                    OneLineAvatarIconListItem(
                        IconLeftWidget(icon="account"),
                        text=f"{player[0]} | {player[1]}  |  {player[2]}",
                        bg_color=(122 / 255, 48 / 255, 108 / 255, .1)
                    )
                )
        self.clear_texts()

    def show_alert_dialog_creation(self, p_id=None):
        self.dialog = None
        if not p_id:
            self.dialog = MDDialog(
                text="This player couldn't be created \nPlease try again",
            )
        elif p_id:
            self.dialog = MDDialog(
                text=f"Your player was added with the id number :\n {p_id}",
                buttons=[
                    MDFlatButton(
                        text="ok",
                        md_bg_color=(122 / 255, 48 / 255, 108 / 255, .5),
                        on_release=lambda _: self.dialog.dismiss()
                    )
                ]
            )
        self.dialog.open()

    def add_player(self, p_name, p_surname):
        """add player in the players_list form to you data base"""
        try:
            enrolling = dab.enroll_players((p_name, p_surname))
            self.feed_list() #resets the players shown to show new players
            self.clear_texts()
        except:
            print("Failed")
            return
        return self.show_alert_dialog_creation(enrolling)

    def players_delete(self):
        """keeps updates the list of players selected to perform an action"""
        p_ids = [(x,) for x in self.players_check]
        print("pre_test", p_ids)
        call = dab.delete_players(p_ids)
        self.feed_list()

        print("called", call)

    def checkbox_check(self, value, p_id):
        if value:
            self.players_check.append(p_id)
        else:
            self.players_check.remove(p_id)

        print("function in screen", self.players_check)




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
        self.clear_texts()

    def clear_texts(self):
        """ to clear everty input on load of the page"""
        self.ids.search_id_tourney.text = ""
        self.ids.search_name_tourney.text = ""
        self.ids.search_tourney_date .text= ""

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
                t_id = tour[0]
                t_date = tour[2]
                t_name = tour[3]
                this_line = OneLineListItem(
                        text=f"{t_id} | {t_date}  |  {t_name}",
                        bg_color=(122 / 255, 48 / 255, 108 / 255, .1),
                        on_release=lambda x: self.change_screen(x.text)
                    )
                curr_screen.ids.tourney_list.add_widget(this_line)

        elif t_id:
            curr_screen.ids.tourney_list.clear_widgets()
            tourney_list = dab.get_tourneys_list(t_id)
            if not tourney_list:
                return print("False")

            for tour in tourney_list:
                t_id = tour[0]
                t_date = tour[2]
                t_name = tour[3]
                this_line = OneLineListItem(
                    text=f"{t_id} | {t_date}  |  {t_name}",
                    bg_color=(122 / 255, 48 / 255, 108 / 255, .1),
                    on_release=lambda x: self.change_screen(x.text)
                )
                curr_screen.ids.tourney_list.add_widget(this_line)

        else:
            curr_screen.ids.tourney_list.clear_widgets()
            tourney_list = dab.get_tourneys_list(t_name=t_name, t_date=t_date)
            if not tourney_list:
                return print("False")

            for tour in tourney_list:
                t_id = tour[0]
                t_date = tour[2]
                t_name = tour[3]
                this_line = OneLineListItem(
                    text=f"{t_id} | {t_date}  |  {t_name}",
                    bg_color=(122 / 255, 48 / 255, 108 / 255, .1),
                    on_release=lambda x: self.change_screen(x.text)
                )
                curr_screen.ids.tourney_list.add_widget(this_line)
        self.clear_texts()

    def on_cancel(self, instance, value):
        """
        Events called when the "CANCEL" dialog box button is clicked.'
        """
        print("canceled")

    def show_date_picker(self):
        date_dialog = MDDatePicker(min_year=2022, max_year=2030)
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    def change_screen(self, t_id: str):
        t_id = t_id.split("|")[0]
        tournament_infos = 0
        #TODO add function to get tournament rounds and infos and pass them as a data file into the next page
        curr_screen = self.parent.get_screen('TourneyList')
        curr_screen.manager.current = "TournamentScreen"


class NewTourney(Screen):
    def __init__(self, **kwargs):
        super(NewTourney, self).__init__(**kwargs)
        self.dialog = None

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

    def show_alert_dialog_creation(self, t_id=None):
        if not self.dialog:
            if not t_id:
                self.dialog = MDDialog(
                    text="This tournament cannot be created \nMissing informations",
                )
            elif t_id:
                self.dialog = MDDialog(
                    text=f"Your tournament was created with id number {t_id}"
                )
        self.dialog.open()

    def create_tournament(self, t_name, t_format, t_date):
        """
        Takes all information and add tournament to the data base then
        launch a pop up to confirm it's done and returns to main page
        """
        print(t_name, t_format, t_date)
        if t_name == "" or t_format == "" or t_date == "":
            self.show_alert_dialog_creation()

        else:
            new_tourney = dab.create_tourney(t_format, t_name, t_date)
            self.show_alert_dialog_creation(new_tourney)


class TournamentScreen(Screen):
    def __init__(self, **kwargs):
        super(TournamentScreen, self).__init__(**kwargs)

    # def on_pre_enter(self):
    #     super().on_pre_enter(self)
    #     # TODO: make the function feed the players list without the error
    #     self.feed_list()

    def feed_list(self):
        curr_screen = self.parent.get_screen('TournamentScreen')
        for x in range(10):
            curr_screen.ids.rounds_list.add_widget(
                OneLineListItem(text=f"Single-line item {x}",
                                on_release=lambda x: self.change_screen()
                                )
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

    def change_screen(self, t_id: str):
        curr_screen = self.parent.get_screen('TournamentList')
        print(t_id)
        curr_screen.manager.current = "TournamentScreen"


class ScreenManager(ScreenManager):
    ...


class TourneyApp(MDApp):
    curr_tournament = None
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
        # Because of the screen system, calling function returns an empty list
        # you need to use the root.get_screen('name of screen') to access it like you would access root.
        curr_screen = self.root.get_screen('PlayersList')
        # ToDO: replace code with sql query of all players
        for x in range(10):
            curr_screen.ids.players_list.add_widget(
                OneLineListItem(text=f"Single-line item {x}")
            )

    def light_dark_change(self):
        """change the light or dark mode"""
        self.theme_cls.theme_style = "Light" if self.theme_cls.theme_style == "Dark" else "Dark"


if __name__ == "__main__":
    TourneyApp().run()
