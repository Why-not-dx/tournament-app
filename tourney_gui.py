# Link all the tournament functions into the GUI
from kivy.lang import Builder


from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.pickers import MDDatePicker


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



class TourneyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"

    def on_save(self, instance, value, date_range):
        """
        event called when the "ok" dialog boc button is clicked
        :type instance: <kivymd.uix.picker.MDDatePicker object>;
        :param value: selected date;
        :type value: <class 'datetime.date'>;
        :param date_range: list of 'datetime.date' objects in the selected range;
        :type date_range: <class 'list'>;
        """
        print(instance, value, date_range)


    def on_cancel(self, instance, value):
        """
        Events called when the "CANCEL" dialog box button is clicked.'
        """
        print("canceled")


    def show_date_picker(self):
        date_dialog = MDDatePicker(min_year=2022, max_year=2030)
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()


if __name__ == "__main__":
    TourneyApp().run()






