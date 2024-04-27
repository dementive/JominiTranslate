import os

import tkinter as tk
from tkinter import filedialog

import customtkinter

from third_party.CTkScrollableDropdown.CTkScrollableDropdown import (
    CTkScrollableDropdown,
)
from third_party.CTkToolTip.CTkToolTip import CTkToolTip
from language import NLLBLanguage
from process_yml import ProcessYml

NLLB = os.getcwd() + "/models/nllb-200_600M_int8_ct2"
NLLB_TOKENIZER = os.getcwd() + "/models/flores200_sacrebleu_tokenizer_spm.model"

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Jomini Translate")
        # Set the window size
        window_width = 260
        window_height = 400

        # Calculate the position of the window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_left = int(screen_width / 2 - window_width / 2)
        position_top = int(screen_height / 2 - window_height / 2) + 20

        # Set the window size and position
        self.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")

        self.custom_frame = CustomFrame(self)
        self.custom_frame.pack(fill="both", expand=True)

    def destroy_frame(self):
        self.custom_frame.destroy()
        self.custom_frame = CustomFrame(self)
        self.custom_frame.pack(fill="both", expand=True)

class Args:
    def __init__(self):
        self.path = tk.StringVar(value="tests/english")
        self.source = tk.StringVar()
        self.target = tk.StringVar()
        self.device = tk.StringVar(value="cpu")
        self.beam_size = tk.IntVar()
        self.translation_model = tk.StringVar(value=NLLB)
        self.tokenize_model = tk.StringVar(value=NLLB_TOKENIZER)

    def to_string(self):
        for attribute in self.__dict__:
            setattr(self, attribute, getattr(self, attribute).get())


class CustomFrame(customtkinter.CTkFrame):
    def __init__(self, parent: App):
        super().__init__(parent)
        self.parent = parent
        self.args = Args()
        self.create_widgets()

    def reset(self):
        self.source_box.set("source language")
        self.target_box.set("target language")
        self.beam_size_box.set("1")
        self.args = Args()

    def create_widgets(self):
        def translate_button_callback():
            self.args.to_string()
            ProcessYml(self.args)
            self.reset()

        def select_translation_dir_button_callback():
            directory = filedialog.askdirectory()
            self.args.path.set(directory)
            path_tooltip.configure(message=f"Translating: {directory}")

        def select_translation_model_dir_button_callback():
            directory = filedialog.askdirectory(initialdir="models/")
            self.args.translation_model.set(directory)

        def select_tokenize_model_dir_button_callback():
            file = filedialog.askopenfile(initialdir="models/")
            self.args.tokenize_model.set(str(file))

        def flip_da_switch():
            if self.args.device == "cuda":
                self.args.device.set("cpu")
            else:
                self.args.device.set("cuda")

        WIDGET_WIDTH = 200

        # Create widgets
        select_translation_dir_button = customtkinter.CTkButton(
            self,
            text="Select Directory To Translate",
            command=select_translation_dir_button_callback,
            width=WIDGET_WIDTH,
        )
        path_tooltip = CTkToolTip(select_translation_dir_button, message=f"Select the localization directory to translate.")

        select_model_dir_button = customtkinter.CTkButton(
            self,
            text="Select Translation Model",
            command=select_translation_model_dir_button_callback,
            width=WIDGET_WIDTH,
        )
        CTkToolTip(select_model_dir_button, message=f"Defaults to {NLLB}")

        select_tokenize_model_dir_button = customtkinter.CTkButton(
            self,
            text="Select Tokenize Model",
            command=select_tokenize_model_dir_button_callback,
            width=WIDGET_WIDTH,
        )

        CTkToolTip(select_tokenize_model_dir_button, message=f"Defaults to {NLLB_TOKENIZER}")

        cuda_switch = customtkinter.CTkSwitch(
            self, text="Use Cuda", variable=self.args.device, width=WIDGET_WIDTH, command=flip_da_switch
        )
        CTkToolTip(cuda_switch, message=f"Should cuda be used to do translations on the GPU instead of the CPU?")

        languages = [x.value for x in NLLBLanguage]

        # Source and target languages
        self.source_box = customtkinter.CTkComboBox(
            self, variable=self.args.source, width=WIDGET_WIDTH
        )
        CTkScrollableDropdown(
            self.source_box,
            command=self.source_dropdown_callback,
            values=languages,
            justify="left",
            button_color="transparent",
            height=500
        )
        self.source_box.set("source language")

        CTkToolTip(self.source_box, message=f"Select the source language to translate from.")

        self.target_box = customtkinter.CTkComboBox(
            self, variable=self.args.target, width=WIDGET_WIDTH
        )
        CTkScrollableDropdown(
            self.target_box,
            values=languages,
            justify="left",
            command=self.target_dropdown_callback,
            button_color="transparent",
            height=500
        )
        CTkToolTip(self.target_box, message=f"Select the target language to translate to.")
        self.target_box.set("target language")

        self.beam_size_box = customtkinter.CTkComboBox(
            self, variable=self.args.beam_size, width=WIDGET_WIDTH, values=["1", "4"]
        )
        self.beam_size_box.set("1")
        CTkToolTip(self.beam_size_box, message=f"Select the beam_size to use for translation.")


        translate_button = customtkinter.CTkButton(
            self,
            text="Start Translation",
            command=translate_button_callback,
            width=WIDGET_WIDTH + 10,
        )

        # Place widgets on grid
        PADX = 25
        select_translation_dir_button.grid(row=0, column=1, padx=PADX, pady=10)
        self.source_box.grid(row=1, column=1, padx=PADX, pady=10)
        self.target_box.grid(row=2, column=1, padx=PADX, pady=10)
        select_model_dir_button.grid(row=3, column=1, padx=PADX, pady=10)
        select_tokenize_model_dir_button.grid(row=4, column=1, padx=PADX, pady=10)
        self.beam_size_box.grid(row=5, column=1, padx=PADX, pady=10)
        cuda_switch.grid(row=6, column=1, padx=25, pady=10)
        translate_button.grid(row=7, column=1, padx=PADX, pady=15)

    def source_dropdown_callback(self, choice):
        self.args.source = tk.StringVar(value=choice)
        self.source_box.set(self.args.source.get())

    def target_dropdown_callback(self, choice):
        self.args.target = tk.StringVar(value=choice)
        self.target_box.set(self.args.target.get())
