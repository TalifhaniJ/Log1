import os
import csv
import shutil
#from android.storage import primary_external_storage_path
#from android.storage import app_storage_path
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
from kivy.lang import builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
import win32timezone

#primary_ext_storage = primary_external_storage_path()

class WISLogging(App):
    def build(self):
        self.icon = 'icon.png'
        self.store = JsonStore('notes.json')
        self.sm = ScreenManager()
        # Main screen layout with its own style
        self.main_screen = Screen(name='main')
        self.main_layout = BoxLayout(orientation='vertical', padding=[20, 0, 20, 0], spacing=20, y=Window.height-650)

        self.form_layout = GridLayout(cols=2, padding=[20, 10, 20, 10], spacing=10, size_hint_y=None)
        self.form_layout.bind(minimum_height=self.form_layout.setter('height'))

        self.depth_input = TextInput(hint_text='Enter measured depth', size_hint=(1, None), height=40, font_size=16)
        self.note_input = TextInput(hint_text='Enter Profile Description', size_hint=(1, None), height=100, font_size=16, multiline=True)
        self.sidenote_input = TextInput(hint_text='Enter Side notes', size_hint=(1, None), height=40, font_size=16)

        self.form_layout.add_widget(Label(text='Measured Depth:', size_hint=(0.4, None), height=40, font_size=16))
        self.form_layout.add_widget(self.depth_input)
        self.form_layout.add_widget(Label(text='Profile Description:', size_hint=(0.4, None), height=40, font_size=16))
        self.form_layout.add_widget(self.note_input)
        self.form_layout.add_widget(Label(text='Side notes:', size_hint=(0.4, None), height=40, font_size=16))
        self.form_layout.add_widget(self.sidenote_input)
        
        self.save_button = Button(text='Save Profile', size_hint=(1, None), height=60, font_size=16)
        self.save_button.bind(on_press=self.save_note)
        
        self.main_layout.add_widget(self.form_layout)
        self.main_layout.add_widget(self.save_button)
        
        # Button to go to the preview screen
        self.preview_button = Button(text='Preview Notes', size_hint=(1, None), height=60, font_size=16)
        self.preview_button.bind(on_press=self.go_to_preview)
        self.main_layout.add_widget(self.preview_button)

        # Button to go to the list of saved files screen
        self.files_button = Button(text='Track Logs', size_hint=(1, None), height=60, font_size=16)
        self.files_button.bind(on_press=self.go_to_files)
        self.main_layout.add_widget(self.files_button)
        # Add logging descriptors table
        self.main_layout.add_widget(Label(text='RECOMMENDED STANDARD PROCEDURES FOR DESCRIBING PROFILES', font_size=18, bold=True, size_hint=(1, None), height=40))
        self.descriptor_table = GridLayout(cols=2, spacing=15, size_hint_y=None)

        self.descriptor_table.add_widget(Label(text='Soil', font_size=26, bold=True, size_hint_y=None, height=15))
        self.descriptor_table.add_widget(Label(text='Rock', font_size=26, bold=True, size_hint_y=None, height=15))

        soil_descriptors = ['Moisture condition', 'Colour', 'Consistency', 'Structure', 'Origin', 'Inclusions']
        rock_descriptors = ['Colour', 'Weathering', 'Fabric', 'Discontinuities', 'Hardness', 'Rock name']

        for soil, rock in zip(soil_descriptors, rock_descriptors):
            self.descriptor_table.add_widget(Label(text=soil, font_size=16, size_hint_y=None, height=10))
            self.descriptor_table.add_widget(Label(text=rock, font_size=16, size_hint_y=None, height=10))

        self.main_layout.add_widget(self.descriptor_table)

        self.main_screen.add_widget(self.main_layout)
        self.sm.add_widget(self.main_screen)

        # Preview screen layout with its own style
        self.preview_screen = Screen(name='preview')
        self.preview_layout = BoxLayout(orientation='vertical', padding=20, spacing=5, size_hint_y=None)

        # Adjust the height of the preview layout to fill the screen from the top
        self.preview_layout.bind(minimum_height=self.preview_layout.setter('height'))

        self.table_layout = GridLayout(cols=3, spacing=0, padding=[5, 50, 5, 100], size_hint_y=None)
        self.table_layout.bind(minimum_height=self.table_layout.setter('height'))
        
        # Add TextInput for the CSV file name
        self.csv_name_input = TextInput(hint_text='Logging ID', size_hint=(1, None), height=40, font_size=16)
        self.preview_layout.add_widget(self.csv_name_input)
        
        self.table_layout.add_widget(Label(text='Measured Depth', font_size=8, bold=True, size_hint_y=None, height=40))
        self.table_layout.add_widget(Label(text='Note', font_size=8, bold=True, size_hint_y=None, height=40))
        self.table_layout.add_widget(Label(text='Side Note', font_size=8, bold=True, size_hint_y=None, height=40))
        
        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height - 100))
        self.scroll_view.add_widget(self.table_layout)
        
        self.preview_layout.add_widget(self.scroll_view)
        
        
        # Add the save as CSV button to the preview screen
        self.save_csv_button = Button(text='Save Log', size_hint=(1, None), height=40, font_size=16)
        self.save_csv_button.bind(on_press=self.save_as_csv)
        self.preview_layout.add_widget(self.save_csv_button)
        
        # Button to go back to the main screen
        self.back_button = Button(text='Back', size_hint=(1, None), height=40, font_size=16)
        self.back_button.bind(on_press=self.go_to_main)
        self.preview_layout.add_widget(self.back_button)

        self.preview_screen.add_widget(self.preview_layout)
        self.sm.add_widget(self.preview_screen)

        # Files screen layout to show saved files
        self.files_screen = Screen(name='files')
        self.files_layout = BoxLayout(orientation='vertical', padding=20, spacing=5, size_hint_y=None)
        self.files_layout.bind(minimum_height=self.files_layout.setter('height'))

        self.files_table = GridLayout(cols=1, spacing=10, padding=[20, 50, 20, 100], size_hint_y=None)
        self.files_table.bind(minimum_height=self.files_table.setter('height'))

        self.files_scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height - 100))
        self.files_scroll_view.add_widget(self.files_table)
        
        self.files_layout.add_widget(self.files_scroll_view)

        # Button to go back to the main screen
        self.back_files_button = Button(text='Back', size_hint=(1, None), height=40, font_size=16)
        self.back_files_button.bind(on_press=self.go_to_main)
        self.files_layout.add_widget(self.back_files_button)
        
        # Add a button to open the file chooser from the track logs page
        self.save_all_button = Button(text='Save All CSVs to Directory', size_hint=(1, None), height=40, font_size=16)
        self.save_all_button.bind(on_press=self.open_file_chooser)
        self.files_layout.add_widget(self.save_all_button)
        
        self.files_screen.add_widget(self.files_layout)
        self.sm.add_widget(self.files_screen)

        # CSV view screen layout
        self.csv_view_screen = Screen(name='csv_view')
        self.csv_view_layout = BoxLayout(orientation='vertical', padding=20, spacing=5, size_hint_y=None)

        self.csv_table = GridLayout(cols=3, spacing=20, padding=[20, 50, 20, 100], size_hint_y=None)
        self.csv_table.bind(minimum_height=self.csv_table.setter('height'))

        self.csv_scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height - 100))
        self.csv_scroll_view.add_widget(self.csv_table)

        self.csv_view_layout.add_widget(self.csv_scroll_view)

        # Button to go back to the files screen
        self.back_csv_button = Button(text='Back', size_hint=(1, None), height=40, font_size=16)
        self.back_csv_button.bind(on_press=self.go_to_files)
        self.csv_view_layout.add_widget(self.back_csv_button)

        self.csv_view_screen.add_widget(self.csv_view_layout)
        self.sm.add_widget(self.csv_view_screen)

        self.load_notes()

        # Add FileChooser popup for saving files
        self.file_chooser = FileChooserListView(path='.', dirselect=True, filters=['*.csv'])
        self.file_chooser_popup = Popup(title='Select Directory', content=self.file_chooser, size_hint=(0.9, 0.9))
        
        self.save_here_button = Button(text='Save Here', size_hint=(1, None), height=40)
        self.save_here_button.bind(on_press=self.save_all_csvs)
        self.file_chooser_popup.content.add_widget(self.save_here_button)

        return self.sm
    
    def save_note(self, instance):
        depth = self.depth_input.text
        note_content = self.note_input.text
        sidenote_content = self.sidenote_input.text if self.sidenote_input.text else '-'
        
        if depth and sidenote_content and note_content:
            self.store.put(depth, note=note_content, sidenote=sidenote_content)
            self.load_notes()
            self.depth_input.text = ''
            self.note_input.text = ''
            self.sidenote_input.text = ''
    
    def load_notes(self):
        self.table_layout.clear_widgets()
        self.table_layout.add_widget(Label(text='Measured Depth', font_size=16, bold=True, size_hint_y=None, height=40))
        self.table_layout.add_widget(Label(text='Profile Description', font_size=16, bold=True, size_hint_y=None, height=40))
        self.table_layout.add_widget(Label(text='Side Note', font_size=16, bold=True, size_hint_y=None, height=40))
        
        for key in self.store:
            self.table_layout.add_widget(Label(text=key, font_size=14, size_hint_y=None, height=30))
            self.table_layout.add_widget(Label(text=self.store.get(key)['note'], font_size=14, size_hint_y=None, height=30))
            self.table_layout.add_widget(Label(text=self.store.get(key)['sidenote'], font_size=14, size_hint_y=None, height=30))

    def save_as_csv(self, instance):
        csv_name = self.csv_name_input.text if self.csv_name_input.text else 'notes'
        with open(f'{csv_name}.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Measured Depth', 'Profile Description', 'Side Notes'])
            
            for key in self.store:
                sidenote = self.store.get(key).get('sidenote','-')
                sidenote = sidenote if sidenote else '-'
                writer.writerow([key, self.store.get(key)['note'], sidenote])
        
        # Optionally clear the existing notes after saving
        self.store.clear()
        self.load_notes()
        self.csv_name_input.text = ''

    def load_files(self):
        self.files_table.clear_widgets()
        files = [f for f in os.listdir('.') if f.endswith('.csv')]
        for file in files:
            btn = Button(text=file, size_hint_y=None, height=30)
            btn.bind(on_press=lambda x, file=file: self.view_csv(file))
            self.files_table.add_widget(btn)

    def view_csv(self, filename):
        self.csv_table.clear_widgets()
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                for cell in row:
                    self.csv_table.add_widget(Label(text=cell, font_size=14, size_hint_y=None, height=30))
        self.sm.current = 'csv_view'
        
    # Method to open the file chooser popup
    def open_file_chooser(self, instance):
        self.file_chooser_popup.open()

    def go_to_preview(self, instance):
        self.sm.current = 'preview'

    def go_to_files(self, instance):
        self.load_files()
        self.sm.current = 'files'

    def go_to_main(self, instance):
        self.sm.current = 'main'
    def save_all_csvs(self, instance):
        selected_directory = self.file_chooser.path
        files = [f for f in os.listdir('.') if f.endswith('.csv')]
        
        for file in files:
            original_path = os.path.join('.', file)
            new_path = os.path.join(selected_directory, file)
            shutil.move(original_path, new_path)

        self.file_chooser_popup.dismiss()
        self.load_files()  # Reload the files to update the list after moving files

if __name__ == '__main__':
    WISLogging().run()
