import os
import sys
from typing import Optional, Dict, Any

import kivy
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import ObjectProperty as ObjectPropertyKivy
from kivy.resources import resource_add_path
from kivy.uix.pagelayout import PageLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen

from app.generator.quesions import generate_questions_factory
from app.logic.shuffle import tickets_generator
from app.parser.parsers import parse_factory, FormatEnum

kivy.require('1.0.7')

Config.set('graphics', 'resizable', False)

Builder.load_file("questions_generator.kv")

GlobalStore: Dict[str, Optional[Any]] = dict(
    path_to_folder=None,
    path_to_answers=None,

    questions_count=None,
    questions_answers_type=None,
    questions_to_answers=None,
)


class ErrorPopup(PageLayout):
    close_button_text = ObjectPropertyKivy(None)
    error_text = ObjectPropertyKivy(None)
    close = ObjectPropertyKivy(None)


class LoadDialog(PageLayout):
    load = ObjectPropertyKivy(None)
    cancel = ObjectPropertyKivy(None)


class SaveDialog(PageLayout):
    save = ObjectPropertyKivy(None)
    text_input = ObjectPropertyKivy(None)
    cancel = ObjectPropertyKivy(None)


class BaseScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

        self._popup: Optional[Popup] = None

    def _dismiss_popup(self) -> None:
        if self._popup is None:
            return
        self._popup.dismiss()
        self._popup = None

    def _show_error(self, error_text: str, button_text: str = 'OK'):
        content = ErrorPopup(
            close_button_text=button_text, error_text=error_text, close=self._dismiss_popup
        )
        if self._popup is not None:
            return

        self._popup = Popup(
            title="Ошибка",
            title_align="center",
            content=content,
            size_hint=(0.5, 0.5)
        )
        self._popup.open()


# Declare both screens
class LoadQuestionsScreen(BaseScreen):
    def __init__(self, **kw):
        super().__init__(**kw)

        self._path_to_folder: Optional[str] = GlobalStore['path_to_folder']
        self._path_to_answers: Optional[str] = GlobalStore['path_to_answers']

    def validate_and_goto_next_screen(self):
        if self._path_to_folder is None:
            self._dismiss_popup()
            self._show_error("Для начала выберете директорию где располагаются вопросы для билетов")
        else:
            try:
                questions_answers_type, questions_to_answers = parse_factory(self._path_to_folder, FormatEnum.dir)
            except RuntimeError as exc:
                self._dismiss_popup()
                self._show_error(''.join(exc.args))
                return

            GlobalStore['path_to_folder'] = self._path_to_folder
            GlobalStore['questions_answers_type'] = questions_answers_type
            GlobalStore['questions_to_answers'] = questions_to_answers

            self.manager.current = 'tickets_settings_screen'

    def show_load(self):

        content = LoadDialog(
            load=self.load_q_and_a, cancel=self._dismiss_popup
        )
        if self._popup is not None:
            return
        self._popup = Popup(
            title="Load file",
            content=content,
            size_hint=(0.9, 0.9)
        )
        self._popup.open()

    def load_q_and_a(self, path: str, filename: str):
        self._path_to_folder = path
        self._dismiss_popup()


class TicketsSettingsScreen(BaseScreen):
    def __init__(self, **kw):
        super().__init__(**kw)

        self._questions_count: Optional[int] = None
        self._path_to_folder: Optional[str] = GlobalStore['path_to_folder']

    def validate_goto_next_screen(self):
        try:
            self._questions_count = int(self._questions_count)
        except ValueError as exc:
            self._dismiss_popup()
            self._show_error("Для начала выберете количество вопросов числом")
            return

        try:
            tickets = tickets_generator(GlobalStore['questions_to_answers'], 5)
        except Exception as exc:
            self._dismiss_popup()
            self._show_error(''.join(exc.args))
            return

        GlobalStore['tickets'] = tickets
        GlobalStore['questions_count'] = self._questions_count

        self.manager.current = 'save_questions_to_screen'

    def on_text_handler(self):
        self._questions_count = self.ids['input_text'].text


class SaveQuestionsToScreen(BaseScreen):

    def __init__(self, **kw):
        super().__init__(**kw)

        self._questions_count: Optional[int] = None
        self._path_to_folder: Optional[str] = GlobalStore['path_to_folder']
        self._path_to_save: Optional[str] = None

    def show_save(self):
        content = SaveDialog(
            save=self.save, cancel=self._dismiss_popup
        )
        if self._popup is not None:
            return

        self._popup = Popup(
            title="Save file",
            content=content,
            size_hint=(0.9, 0.9)
        )
        self._popup.open()

    def save(self, path, filename):
        self._path_to_save = path
        try:
            generate_questions_factory(
                self._path_to_save, GlobalStore['questions_to_answers'], GlobalStore['questions_answers_type'], GlobalStore['tickets']
            )
        except Exception as exc:
            print(exc)
            self._dismiss_popup()
            self._show_error(''.join(exc.args))
            return

        self._dismiss_popup()

    def exit_app(self):
        exit(0)


class MainApp(App):
    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(LoadQuestionsScreen(name='load_questions_screen'))
        sm.add_widget(TicketsSettingsScreen(name='tickets_settings_screen'))
        sm.add_widget(SaveQuestionsToScreen(name='save_questions_to_screen'))

        return sm


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    app = MainApp()
    app.run()
