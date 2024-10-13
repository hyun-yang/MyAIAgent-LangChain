import html
import re

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QApplication, QHBoxLayout, QFileDialog, \
    QMessageBox

from custom.ImageDisplay import ImageDisplay
from util.ChatType import ChatType
from util.Constants import Constants, UI
from util.Utility import Utility


class ImageWidget(QWidget):
    def __init__(self, chat_type: ChatType, image_data: str = None, response: str = None):
        super().__init__()
        self.chat_type = chat_type
        self.scale_ratio = Constants.SCALE_RATIO
        self.no_style = True

        self.response_text = response
        self.response_label = QLabel(response)
        self.format_text_label()

        self.image = ImageDisplay(image_data)

        # UI setup
        self.initialize_ui()

    def initialize_ui(self):
        layout = QVBoxLayout(self)
        top_widget = self.create_top_widget()

        image_text_layout = QHBoxLayout()
        image_text_layout.addWidget(self.image)
        image_text_layout.addWidget(self.response_label)

        # Image width = 1/3, Text width = 2/3
        image_text_layout.setStretch(0, 1)
        image_text_layout.setStretch(1, 2)

        layout.addWidget(top_widget)
        layout.addLayout(image_text_layout)

    def create_top_widget(self):

        boldFont = QFont()
        boldFont.setBold(True)

        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)

        human_titlebar_background_color = Utility.get_settings_value(section="Chat_TitleBar_Style", prop="human_color",
                                                                     default="#dfccff",
                                                                     save=True)
        ai_titlebar_background_color = Utility.get_settings_value(section="Chat_TitleBar_Style", prop="ai_color",
                                                                  default="#d8fabe",
                                                                  save=True)

        if self.chat_type != ChatType.HUMAN:
            top_widget.setStyleSheet(f"background-color: {ai_titlebar_background_color}")
        else:
            top_widget.setStyleSheet(f"background-color: {human_titlebar_background_color}")

        padding = Utility.get_settings_value(section="Common_Label_Style", prop="padding",
                                             default="5px",
                                             save=True)

        model_color = Utility.get_settings_value(section="Info_Label_Style", prop="model-color",
                                                 default="green",
                                                 save=True)

        self.model_label = QLabel("")
        self.model_label.setFont(boldFont)

        model_label_style = f"""
                    QLabel {{
                        padding: {padding};
                        color: {model_color};
                    }}
                    """

        self.model_label.setStyleSheet(model_label_style)
        self.model_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        copy_button = QPushButton(QIcon(Utility.get_icon_path('ico', 'disks.png')), "Copy")
        copy_button.clicked.connect(lambda: QApplication.clipboard().setPixmap(self.image.pixmap))

        save_button = QPushButton(QIcon(Utility.get_icon_path('ico', 'disk--plus.png')), "Save")
        save_button.clicked.connect(self.save_image)

        zoomin_button = QPushButton(QIcon(Utility.get_icon_path('ico', 'magnifier-zoom-in.png')), "+Zoom")
        zoomin_button.clicked.connect(self.zoom_in)

        zoomout_button = QPushButton(QIcon(Utility.get_icon_path('ico', 'magnifier-zoom-out.png')), "-Zoom")
        zoomout_button.clicked.connect(self.zoom_out)

        # Create layouts for label and buttons
        model_label_layout = QHBoxLayout()
        model_label_layout.addWidget(self.model_label)
        model_label_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(copy_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(zoomout_button)
        button_layout.addWidget(zoomin_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Add both layouts to the top layout
        top_layout.addLayout(model_label_layout)
        top_layout.addLayout(button_layout)

        return top_widget

    def format_text_label(self):
        self.response_label.setTextFormat(Qt.TextFormat.MarkdownText)
        self.response_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.response_label.setWordWrap(True)
        self.response_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.response_label.setOpenExternalLinks(True)

        padding = Utility.get_settings_value(section="Common_Label_Style", prop="padding",
                                             default="5px",
                                             save=True)
        color = Utility.get_settings_value(section="Common_Label_Style", prop="color",
                                           default="#000000",
                                           save=True)
        font_size = Utility.get_settings_value(section="Common_Label_Style", prop="font-size",
                                               default="14px",
                                               save=True)
        font_family = Utility.get_settings_value(section="Common_Label_Style", prop="font-family",
                                                 default="sans-serif",
                                                 save=True)
        user_text_style = f"""
            QLabel {{
                padding: {padding};
                color: {color};
                font-size: {font_size};
                font-family: {font_family};
            }}
            """
        self.response_label.setStyleSheet(user_text_style)

    def highlight_search_text(self, target_text, search_text):
        color = Utility.get_settings_value(section="AI_Code_Style", prop="color",
                                           default="#ccc",
                                           save=True)
        background_color = Utility.get_settings_value(section="AI_Code_Style", prop="background-color",
                                                      default="#333333",
                                                      save=True)

        # Escape HTML characters
        target_text = html.escape(target_text)

        # Preserve carriage returns and tabs
        target_text = target_text.replace('\n', '<br>')
        target_text = target_text.replace('\t', '&nbsp;' * 4)

        search_text_escaped = re.escape(search_text)
        search_pattern = re.compile(search_text_escaped, re.IGNORECASE)

        matches = search_pattern.findall(target_text)
        for match in matches:
            formatted_code = f'<span style="color: {color}; background-color: {background_color};">{match}</span>'
            target_text = target_text.replace(match, formatted_code)

        return target_text

    def apply_highlight(self, text: str):
        self.response_label.setTextFormat(Qt.TextFormat.RichText)
        self.response_label.setText(text)

    def format_code_snippet(self, text):
        color = Utility.get_settings_value(section="AI_Code_Style", prop="color",
                                           default="#ccc",
                                           save=True)
        background_color = Utility.get_settings_value(section="AI_Code_Style", prop="background-color",
                                                      default="#333333",
                                                      save=True)
        font_size = Utility.get_settings_value(section="AI_Code_Style", prop="font-size",
                                               default="14px",
                                               save=True)
        font_family = Utility.get_settings_value(section="AI_Code_Style", prop="font-family",
                                                 default="monospace",
                                                 save=True)

        code_pattern = re.compile(r'```(\w+)\n(.*?)\n```', re.DOTALL)
        if text:
            matches = code_pattern.findall(text)
            for language, code in matches:
                escaped_code = html.escape('\n' + code)
                formatted_code = (
                    f'<pre style="font-size: {font_size}; font-family: {font_family}; background-color: {background_color}; color: {color};"><code>{escaped_code}</code></pre>')
                text = text.replace(f'```{language}\n{code}\n```', formatted_code)
        return text

    def get_text(self):
        return self.response_label.text()

    def apply_style(self):
        formatted_text = self.format_code_snippet(self.get_original_text())
        self.response_label.setText(formatted_text)

    def get_original_text(self):
        return self.response_text

    def show_original_text(self):
        self.response_label.setText(self.get_original_text())
        if self.no_style:
            self.no_style = False
        else:
            self.apply_style()
            self.no_style = True

    def get_chat_type(self):
        return self.chat_type

    def set_model_name(self, name):
        self.model_label.setText(name)

    def save_image(self):
        file_name, _ = QFileDialog.getSaveFileName(self, UI.SAVE_IMAGE_TITLE, "", UI.SAVE_IMAGE_FILTER)
        if file_name:
            try:
                self.image.pixmap.save(file_name, UI.IMAGE_PNG)
                QMessageBox.information(self, UI.SUCCESS, UI.FILE_COPY_SUCCESS)
            except Exception as e:
                QMessageBox.critical(self, UI.ERROR, f"{UI.FILE_COPY_ERROR} {str(e)}")

    def zoom(self, ratio):
        self.image.scale(ratio, ratio)

    def zoom_in(self):
        self.zoom(self.scale_ratio)

    def zoom_out(self):
        self.zoom(1 / self.scale_ratio)
