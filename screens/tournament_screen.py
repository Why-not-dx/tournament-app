from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.list import OneLineListItem
import utils.my_tourneys as dab


class TournamentScreen(Screen):
    def __init__(self, **kwargs):
        super(TournamentScreen, self).__init__(**kwargs)
        self.curr_tournament = None
        self.data_tables = None
        #TODO add the functions to get rounds and feed the MDList
        #TODO add the function to get players from this tourney
        #TODO add the function and Button to add players to the tourney

    def on_pre_enter(self):
        super().on_pre_enter(self)
        # self.feed_list()
        self.curr_tournament = int(MDApp.get_running_app().tournament_id)
        t_name = dab.get_tourneys_list(t_id=self.curr_tournament)[0][3]
        self.ids.tournament_page_name.text = t_name
        print(self.curr_tournament, t_name)
        self.feed_rounds()

    def feed_rounds(self):
        print(self.curr_tournament, type(self.curr_tournament))
        rounds_list = dab.get_rounds(self.curr_tournament)
        rounds_list = [r[0] for r in rounds_list]
        self.feed_list(rounds_list)

    def feed_list(self, rounds):
        curr_screen = self.parent.get_screen('TournamentScreen')
        for r in rounds:
            curr_screen.ids.rounds_list.add_widget(
                OneLineListItem(text=f"Round :  {r}",
                                on_release=lambda x: self.change_screen()  #TODO create pop up with results of round
                                )
            )

    def change_screen(self, t_id: str):
        curr_screen = self.parent.get_screen('TournamentList')
        print(t_id)
        curr_screen.manager.current = "TournamentScreen"

    def players_list(self) -> list:
        players = dab.players_list(self.curr_tournament)
        players_list = []
        for p in players:
            players_list.append(dab.get_players_from_id((p,))[0])
        print(players_list)

        return players_list

    def open_players_table(self):
        """ open a MDDataTable with players informations"""
        curr_screen = self.parent.get_screen('TournamentScreen')

        self.box = MDBoxLayout(
            orientation="vertical",
            pos_hint={"center_x": .5, "bottom": .2},
            size_hint=(1, .9),
            md_bg_color=(1, 1, 1, .2)
        )
        self.data_tables = MDDataTable(
            use_pagination=True,
            column_data=[
                ("ID", dp(30)),("NAME", dp(30)),("SURNAME", dp(30))
            ],
            size_hint=(.9, .8),
            pos_hint={"center_x": .5, "center_y": .5}
        )
        self.butt = MDIconButton(
            icon="close-circle",
            md_bg_color=(122/255, 48/255, 108/255, 1),
            user_font_size=dp(25),
            on_release=lambda x: self.remove_players_table(),
            pos_hint={"right": .95}
        )
        self.box.add_widget(self.butt)
        self.box.add_widget(self.data_tables)

        curr_screen.add_widget(self.box)

    def remove_players_table(self):
        curr_screen = self.parent.get_screen('TournamentScreen')
        curr_screen.remove_widget(self.box)
