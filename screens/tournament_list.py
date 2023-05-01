from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.pickers import MDDatePicker

import utils.my_tourneys as dab
from main import RightCheckboxTourney


class TourneyList(Screen):
    def __init__(self, **kwargs):
        super(TourneyList, self).__init__(**kwargs)
        self.tourneys_check = []
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
        self.ids.search_tourney_date.text = ""

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
                this_line = OneLineAvatarIconListItem(
                    IconLeftWidget(icon="account"),
                    RightCheckboxTourney(),
                    text=f"{t_id} | {t_date}  |  {t_name}",
                    bg_color=(122 / 255, 48 / 255, 108 / 255, .1),
                    on_release=lambda x: self.change_screen(x.text),
                    )
                curr_screen.ids.tourney_list.add_widget(this_line)

        elif t_id:
            curr_screen.ids.tourney_list.clear_widgets()
            tourney_list = dab.get_tourneys_list(t_id)
            if not tourney_list:
                return False

            for tour in tourney_list:
                t_id = tour[0]
                t_date = tour[2]
                t_name = tour[3]
                this_line = OneLineAvatarIconListItem(
                    IconLeftWidget(icon="account"),
                    RightCheckboxTourney(),
                    text=f"{t_id} | {t_date}  |  {t_name}",
                    bg_color=(122 / 255, 48 / 255, 108 / 255, .1),
                    on_release=lambda x: self.change_screen(x.text)
                )
                curr_screen.ids.tourney_list.add_widget(this_line)

        else:
            curr_screen.ids.tourney_list.clear_widgets()
            tourney_list = dab.get_tourneys_list(t_name=t_name, t_date=t_date)
            if not tourney_list:
                return False

            for tour in tourney_list:
                t_id = tour[0]
                t_date = tour[2]
                t_name = tour[3]
                this_line = OneLineAvatarIconListItem(
                    IconLeftWidget(icon="account"),
                    RightCheckboxTourney(),
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
        MDApp.get_running_app().tournament_id = t_id
        curr_screen = self.parent.get_screen('TourneyList')
        curr_screen.manager.current = "TournamentScreen"

    def tourney_delete(self):
        """keeps updates the list of players selected to perform an action"""
        t_ids = [(x,) for x in self.tourneys_check]
        dab.delete_tourney(t_ids)
        self.feed_list()
        self.dialog.dismiss()

    def checkbox_check(self, value, t_id):
        if value:
            self.tourneys_check.append(t_id)
        else:
            self.tourneys_check.remove(t_id)

    def show_alert_dialog_deletion(self):
        self.dialog = None
        if not self.tourneys_check:
            self.dialog = MDDialog(
                text=f"No tournament selected",
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
                text=f"Delete selected tournaments from data base ?",
                buttons=[
                    MDFlatButton(
                        text="ok",
                        md_bg_color=(122 / 255, 48 / 255, 108 / 255, .5),
                        on_release=lambda _: self.tourney_delete()
                    ),
                    MDFlatButton(
                        text="Cancel",
                        md_bg_color=(122 / 255, 48 / 255, 108 / 255, .5),
                        on_release=lambda _: self.dialog.dismiss()
                    )
                ]
            )
        self.dialog.open()

