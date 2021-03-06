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
from app.logic.shuffle import tickets_generator, shuffle_if_needed
from app.parser.parsers import parse_factory, FormatEnum

kivy.require('1.0.7')

Config.set('graphics', 'resizable', False)

# Builder.load_file("questions_generator.kv")
Builder.load_string("""
#:kivy 1.1.0


<LoadQuestionsScreen>:
    AnchorLayout:
        padding: [50, 50, 50, 50]
        anchor_x: 'center'
        anchor_y: 'center'
        AnchorLayout:
            anchor_x: 'center'
            anchor_y: 'center'
            Button:
                size_hint: (.3, .1)
                text: 'Загрузить вопросы и ответы'
                on_release: root.show_load()
        AnchorLayout:
            anchor_x: 'center'
            anchor_y: 'bottom'
            Button:
                size_hint: (.3, .1)
                text: 'Далее'
                on_press: root.validate_and_goto_next_screen()


<ErrorPopup>:
    AnchorLayout:
        padding: [5, 5, 5, 5]
        anchor_x: 'center'
        anchor_y: 'center'
        AnchorLayout:
            anchor_x: 'right'
            anchor_y: 'top'
            Label:
                text_size: self.width, None
                text: root.error_text
        AnchorLayout:
            anchor_x: 'center'
            anchor_y: 'bottom'
            Button:
                size_hint: (.3, .1)
                text: root.close_button_text
                on_release: root.close()


<LoadDialog>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        FileChooserListView:
            id: filechooser

        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: "Cancel"
                on_release: root.cancel()

            Button:
                text: "Load"
                on_release: root.load(filechooser.path, filechooser.selection)


<TicketsSettingsScreen>:
    AnchorLayout:
        padding: [50, 50, 50, 50]
        anchor_x: 'center'
        anchor_y: 'center'
        AnchorLayout:
            anchor_x: 'center'
            anchor_y: 'center'
            AnchorLayout:
                anchor_x: 'left'
                anchor_y: 'center'
                Label:
                    text: 'Введите количество вопросов в билете  '
            AnchorLayout:
                anchor_x: 'right'
                anchor_y: 'center'
                TextInput:
                    id: input_text
                    size_hint: (.1, .1)
                    on_text: root.on_text_handler()

        AnchorLayout:
            anchor_x: 'center'
            anchor_y: 'top'
            AnchorLayout:
                anchor_x: 'right'
                anchor_y: 'top'
                Label:
                    size_hint: (.6, .1)
                    text: "Случайно перемешать ответы и вопросы"
            AnchorLayout:
                anchor_x: 'right'
                anchor_y: 'top'
                CheckBox:
                    size_hint: (.1, .1)
                    on_release: root.checkbox_click_shuffle()

        AnchorLayout:
            anchor_x: 'left'
            anchor_y: 'bottom'
            Button:
                size_hint: (.3, .1)
                text: 'Назад'
                on_release: root.manager.current = 'load_questions_screen'
        AnchorLayout:
            anchor_x: 'right'
            anchor_y: 'bottom'
            Button:
                size_hint: (.3, .1)
                text: 'Далее'
                on_press: root.validate_goto_next_screen()


<SaveQuestionsToScreen>:
    AnchorLayout:
        padding: [50, 50, 50, 50]
        anchor_x: 'center'
        anchor_y: 'center'
        AnchorLayout:
            anchor_x: 'center'
            anchor_y: 'center'
            Button:
                size_hint: (.3, .1)
                text: 'Сохранить'
                on_release: root.show_save()
        AnchorLayout:
            anchor_x: 'center'
            anchor_y: 'bottom'
            Button:
                size_hint: (.3, .1)
                text: 'Выход'
                on_press: root.exit_app()


<SaveDialog>:
    text_input: text_input
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        FileChooserListView:
            id: filechooser
            on_selection: text_input.text = self.selection and self.selection[0] or ''

        TextInput:
            id: text_input
            size_hint_y: None
            height: 30
            multiline: False

        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: "Cancel"
                on_release: root.cancel()

            Button:
                text: "Save"
                on_release: root.save(filechooser.path, text_input.text)

""")

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

        self._use_classic: bool = True
        self._shuffle: bool = False

    def validate_goto_next_screen(self):
        try:
            if self._questions_count is None:
                raise ValueError
            self._questions_count = int(self._questions_count)
        except ValueError as exc:
            self._dismiss_popup()
            self._show_error("Для начала выберете количество вопросов числом")
            return
        except Exception as exc:
            self._dismiss_popup()
            self._show_error(''.join(exc.args))
            return

        try:
            tickets = tickets_generator(
                GlobalStore['questions_to_answers'], self._questions_count, use_classic=True
            )
        except Exception as exc:
            self._dismiss_popup()
            self._show_error(''.join(exc.args))
            return

        if self._shuffle:
            try:
                GlobalStore['questions_to_answers'] = shuffle_if_needed(
                    GlobalStore['questions_to_answers'],
                    with_shuffle_q=self._shuffle,
                    with_shuffle_a=self._shuffle,
                )
            except Exception as exc:
                self._dismiss_popup()
                self._show_error(''.join(exc.args))
                return

        GlobalStore['tickets'] = tickets
        GlobalStore['questions_count'] = self._questions_count

        self.manager.current = 'save_questions_to_screen'

    def on_text_handler(self):
        self._questions_count = self.ids['input_text'].text

    def checkbox_click_classic(self):
        self._use_classic = not self._use_classic

    def checkbox_click_shuffle(self):
        self._shuffle = not self._shuffle


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


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


if __name__ == '__main__':
    # resource_add_path(resource_path('app/gui'))
    app = MainApp()
    app.run()
