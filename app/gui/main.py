from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.pagelayout import PageLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
import os
kivy.require('1.0.7')


Builder.load_file("questions_generator.kv")


class LoadDialog(PageLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


# Declare both screens
class LoadQuestionsScreen(Screen):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        with open(os.path.join(path, filename[0])) as stream:
            self.text_input.text = stream.read()

        self.dismiss_popup()


class TicketsSettingsScreen(Screen):
    pass


class MainApp(App):
    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(LoadQuestionsScreen(name='load_questions_screen'))
        sm.add_widget(TicketsSettingsScreen(name='tickets_settings_screen'))

        return sm


if __name__ == '__main__':
    app = MainApp()
    app.run()
