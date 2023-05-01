from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget
import utils.my_tourneys as dab
from main import RightCheckbox


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

    def show_alert_dialog_deletion(self):
        self.dialog = None
        if not self.players_check:
            self.dialog = MDDialog(
                text=f"No player selected",
                buttons=[
                    MDFlatButton(
                        text="Cancel",
                        md_bg_color=(122 / 255, 48 / 255, 108 / 255, .5),
                        on_release=lambda _: self.dialog.dismiss()
                    )
                ]
            )
        else:
            self.dialog = MDDialog(
                text=f"Delete selected players from data base ?",
                buttons=[
                    MDFlatButton(
                        text="ok",
                        md_bg_color=(122 / 255, 48 / 255, 108 / 255, .5),
                        on_release=lambda _: self.players_delete()
                    ),
                    MDFlatButton(
                        text="Cancel",
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
        dab.delete_players(p_ids)
        self.feed_list()
        self.dialog.dismiss()

    def show_add_players_dialog(self):
        """pop up asking for the tournament to feed
        show a MDList of the tourneys in the app"""

        curr_t = MDApp.get_running_app().tournament_id
        if not curr_t:
            self.dialog = MDDialog(
                text="Please choose a tournament in the tournament page"
            )
        else:
            self.dialog = MDDialog(
                text=f"Add those players to tournament {curr_t} ?",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        md_bg_color=(122 / 255, 48 / 255, 108 / 255, .5),
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="OK",
                        md_bg_color=(122 / 255, 48 / 255, 108 / 255, .5),
                        on_release=lambda x: print("Ok")
                    ),
                ],
            )
        self.dialog.open()

    def add_to_tourney(self, t_id: int):
        """takes a list of players and adds them to the tournament,
         the first round will immediatly be generated"""
        p_ids = [(x,) for x in self.players_check]
        print(p_ids)

    def checkbox_check(self, value, p_id):
        if value:
            self.players_check.append(p_id)
        else:
            self.players_check.remove(p_id)

        print("function in screen", self.players_check)

