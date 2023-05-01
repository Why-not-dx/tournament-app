from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.pickers import MDDatePicker
import utils.my_tourneys as dab

class NewTourney(Screen):
    def __init__(self, **kwargs):
        super(NewTourney, self).__init__(**kwargs)
        self.dialog = None

    def on_pre_enter(self, *args):
        super().on_pre_enter(self, *args)
        self.clear_texts()

    def clear_texts(self):
        self.ids.search_tourney_date.text = ""
        self.ids.new_tourney_name.text = ""
        self.ids.new_tourney_format.text = ""

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

        self.dialog = None
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
            self.clear_texts()

