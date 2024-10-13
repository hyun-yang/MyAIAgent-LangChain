from functools import partial

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QSplitter, QComboBox, QLabel, QTabWidget, \
    QGroupBox, QFormLayout, QPushButton, QHBoxLayout, QApplication, QTextEdit, QSpinBox, QListWidget, \
    QFileDialog, QMessageBox

from chat.view.ChatHistory import ChatHistory
from chat.view.ChatWidget import ChatWidget
from chat.view.ImageWidget import ImageWidget
from custom.PromptTextEdit import PromptTextEdit
from util.ChatType import ChatType
from util.Constants import AIProviderName, UI
from util.Constants import Constants
from util.SettingsManager import SettingsManager
from util.Utility import Utility


class ChatView(QWidget):
    submitted_file_signal = pyqtSignal(object)
    submitted_signal = pyqtSignal(str)
    stop_signal = pyqtSignal()
    chat_llm_signal = pyqtSignal(str)
    reload_chat_detail_signal = pyqtSignal(int)

    def __init__(self, model):
        super().__init__()
        self.model = model
        self._settings = SettingsManager.get_settings()
        self._current_chat_llm = Utility.get_settings_value(section="AI_Provider", prop="llm",
                                                            default="Ollama", save=True)
        self.found_text_positions = []

        self.initialize_ui()

    def initialize_ui(self):

        # Top layout
        self.top_layout = QVBoxLayout()
        self.top_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Create buttons
        self.clear_all_button = QPushButton(QIcon(Utility.get_icon_path('ico', 'bin.png')), UI.CLEAR_ALL)
        self.clear_all_button.clicked.connect(lambda: self.clear_all())

        self.copy_all_button = QPushButton(QIcon(Utility.get_icon_path('ico', 'cards-stack.png')), UI.COPY_ALL)
        self.copy_all_button.clicked.connect(lambda: QApplication.clipboard().setText(self.get_all_text()))

        self.reload_button = QPushButton(QIcon(Utility.get_icon_path('ico', 'cards-address.png')), UI.RELOAD_ALL)
        self.reload_button.clicked.connect(lambda: self.reload_chat_detail_signal.emit(-1))

        self.search_text = PromptTextEdit()
        self.search_text.submitted_signal.connect(self.search)
        self.search_text.setPlaceholderText(UI.SEARCH_PROMPT_PLACEHOLDER)

        self.search_text.setFixedHeight(self.clear_all_button.sizeHint().height())
        self.search_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.search_result = QLabel()

        # Create navigation buttons
        self.prev_button = QPushButton(QIcon(Utility.get_icon_path('ico', 'arrow-180.png')), '')
        self.prev_button.clicked.connect(self.scroll_to_previous_match_widget)
        self.next_button = QPushButton(QIcon(Utility.get_icon_path('ico', 'arrow.png')), '')
        self.next_button.clicked.connect(self.scroll_to_next_match_widget)

        # Create a horizontal layout and add the buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.search_text)
        button_layout.addWidget(self.search_result)
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)
        button_layout.addWidget(self.copy_all_button)
        button_layout.addWidget(self.clear_all_button)
        button_layout.addWidget(self.reload_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Add the button layout to the result layout
        self.top_layout.addLayout(button_layout)

        self.top_widget = QWidget()
        self.top_widget.setLayout(self.top_layout)
        self.top_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        # Result View
        self.result_layout = QVBoxLayout()
        self.result_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.result_layout.setSpacing(0)
        self.result_layout.setContentsMargins(0, 0, 0, 0)

        self.result_widget = QWidget()
        self.result_widget.setLayout(self.result_layout)

        # Scroll Area
        self.ai_answer_scroll_area = QScrollArea()
        self.ai_answer_scroll_area.setWidgetResizable(True)
        self.ai_answer_scroll_area.setWidget(self.result_widget)
        self.ai_answer_scroll_area.verticalScrollBar().rangeChanged.connect(self.adjust_scroll_bar)

        # Stop Button
        self.stop_button = QPushButton(QIcon(Utility.get_icon_path('ico', 'minus-circle.png')), 'Stop')
        self.stop_button.clicked.connect(self.force_stop)

        stop_layout = QHBoxLayout()
        stop_layout.setContentsMargins(0, 0, 0, 0)
        stop_layout.setSpacing(0)
        stop_layout.addWidget(self.stop_button)
        stop_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stop_widget = QWidget()
        self.stop_widget.setLayout(stop_layout)
        self.stop_widget.setVisible(False)

        # Prompt View
        self.prompt_text = PromptTextEdit()
        self.prompt_text.submitted_signal.connect(self.handle_submitted_signal)
        self.prompt_text.setPlaceholderText(UI.CHAT_PROMPT_PLACEHOLDER)

        prompt_layout = QVBoxLayout()
        prompt_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        prompt_layout.addWidget(self.prompt_text)
        prompt_layout.setSpacing(0)
        prompt_layout.setContentsMargins(0, 0, 0, 0)

        self.prompt_widget = QWidget()
        self.prompt_widget.setLayout(prompt_layout)
        self.prompt_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        chat_layout = QVBoxLayout()

        chat_layout.addWidget(self.top_widget)
        chat_layout.addWidget(self.ai_answer_scroll_area)
        chat_layout.addWidget(self.stop_widget)
        chat_layout.addWidget(self.prompt_widget)

        chatWidget = QWidget()
        chatWidget.setLayout(chat_layout)

        config_layout = QVBoxLayout()

        self.config_tabs = QTabWidget()
        chat_icon = QIcon(Utility.get_icon_path('ico', 'processor.png'))
        self.config_tabs.addTab(self.create_parameters_tab(), chat_icon, UI.AI_AGENT)
        self.config_tabs.addTab(self.create_chatdb_tab(), chat_icon, UI.AI_AGENT_QA_LIST)

        config_layout.addWidget(self.config_tabs)

        configWidget = QWidget()
        configWidget.setLayout(config_layout)

        mainWidget = QSplitter(Qt.Orientation.Horizontal)
        mainWidget.addWidget(configWidget)
        mainWidget.addWidget(chatWidget)
        mainWidget.setSizes([UI.QSPLITTER_LEFT_WIDTH, UI.QSPLITTER_RIGHT_WIDTH])
        mainWidget.setHandleWidth(UI.QSPLITTER_HANDLEWIDTH)

        main_layout = QVBoxLayout()
        main_layout.addWidget(mainWidget)

        self.setLayout(main_layout)

    def reset_search_bar(self):
        self.found_text_positions = []
        self.search_result.clear()
        self.current_position_index = -1
        self.update_navigation_buttons()

    def search(self, text: str):
        if text and text.strip() and len(text) >= 2:
            self.found_text_positions = []
            self.current_position_index = -1

            search_text_lower = text.lower()

            for i in range(self.result_layout.count()):
                current_widget = self.result_layout.itemAt(i).widget()
                current_text = current_widget.get_original_text()
                current_text_lower = current_text.lower()

                if search_text_lower in current_text_lower:
                    self.found_text_positions.append(i)
                    highlight_text = current_widget.highlight_search_text(current_text, text)
                    current_widget.apply_highlight(highlight_text)
                else:
                    current_widget.show_original_text()

            if self.found_text_positions:
                self.current_position_index = 0
                self.scroll_to_match_widget(self.found_text_positions[self.current_position_index])
        if len(self.found_text_positions) > 0:
            self.search_result.setText(f'{len(self.found_text_positions)} {UI.FOUNDS}')
        else:
            self.search_result.clear()
        self.update_navigation_buttons()
        self.search_text.clear()

    def scroll_to_match_widget(self, position):
        self.ai_answer_scroll_area.ensureWidgetVisible(self.result_layout.itemAt(position).widget())

    def scroll_to_previous_match_widget(self):
        if len(self.found_text_positions) > 0 and self.current_position_index > 0:
            self.current_position_index -= 1
            self.scroll_to_match_widget(self.found_text_positions[self.current_position_index])
            self.update_navigation_buttons()

    def scroll_to_next_match_widget(self):
        if len(self.found_text_positions) > 0 and self.current_position_index < len(self.found_text_positions) - 1:
            self.current_position_index += 1
            self.scroll_to_match_widget(self.found_text_positions[self.current_position_index])
            self.update_navigation_buttons()

    def update_navigation_buttons(self):
        self.prev_button.setEnabled(self.current_position_index > 0)
        self.next_button.setEnabled(self.current_position_index < len(self.found_text_positions) - 1)

    def create_parameters_tab(self):
        layoutWidget = QWidget()
        layout = QVBoxLayout()

        # Tabs for LLM
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_prompt_tabcontent("Router", False), "Router")
        self.tabs.addTab(self.create_prompt_tabcontent("Document", True), "Document")
        self.tabs.addTab(self.create_prompt_tabcontent("RAG", False), "RAG")
        self.tabs.addTab(self.create_prompt_tabcontent("Hallucination", True), "Hallucination")
        self.tabs.addTab(self.create_prompt_tabcontent("Answer", True), "Answer")
        self.tabs.addTab(self.create_openai_tabcontent(AIProviderName.OLLAMA.value), "LangChain")

        layout.addWidget(self.tabs)
        layoutWidget.setLayout(layout)
        return layoutWidget

    def set_default_tab(self, name):
        index = self.tabs.indexOf(self.tabs.findChild(QWidget, name))
        if index != -1:
            self.tabs.setCurrentIndex(index)

    def on_prompt_change(self, name):
        current_text = self.findChild(QComboBox, f"{name}_promptList").currentText()
        prompt_values = Utility.get_system_value(section=f"{name}_Prompt", prefix="prompt",
                                                 default="You are a helpful assistant.", length=3)
        current_prompt = self.findChild(QTextEdit, f"{name}_current_prompt")
        if current_text in prompt_values:
            current_prompt.setText(prompt_values[current_text])
        else:
            current_prompt.clear()

    def save_prompt_value(self, name):
        current_promptList = self.findChild(QComboBox, f"{name}_promptList")
        current_prompt = self.findChild(QTextEdit, f"{name}_current_prompt")
        selected_key = current_promptList.currentText()
        value = current_prompt.toPlainText()
        self._settings.setValue(f"{name}_Prompt/{selected_key}", value)
        self.update_prompt_list(name, Utility.extract_number_from_end(selected_key) - 1)

    def update_prompt_list(self, name, index=0):
        current_promptList = self.findChild(QComboBox, f"{name}_promptList")
        prompt_values = Utility.get_system_value(section=f"{name}_Prompt", prefix="prompt",
                                                 default="You are a helpful assistant.", length=3)
        if current_promptList:
            current_promptList.clear()
            current_promptList.addItems(prompt_values.keys())

        if prompt_values and current_promptList:
            current_promptList.setCurrentIndex(index)

    def on_instruction_change(self, name):
        current_text = self.findChild(QComboBox, f"{name}_instructionList").currentText()
        instruction_values = Utility.get_system_value(section=f"{name}_Instruction", prefix="instruction",
                                                      default="You are a helpful assistant.", length=3)
        current_instruction = self.findChild(QTextEdit, f"{name}_current_instruction")
        if current_text in instruction_values:
            current_instruction.setText(instruction_values[current_text])
        else:
            current_instruction.clear()

    def save_instruction_value(self, name):
        current_instructionList = self.findChild(QComboBox, f"{name}_instructionList")
        current_instruction = self.findChild(QTextEdit, f"{name}_current_instruction")
        selected_key = current_instructionList.currentText()
        value = current_instruction.toPlainText()
        self._settings.setValue(f"{name}_Instruction/{selected_key}", value)
        self.update_instruction_list(name, Utility.extract_number_from_end(selected_key) - 1)

    def update_instruction_list(self, name, index=0):
        instruction_List = self.findChild(QComboBox, f"{name}_instructionList")
        instruction_values = Utility.get_system_value(section=f"{name}_Instruction", prefix="instruction",
                                                      default="You are a helpful assistant.", length=3)
        if instruction_List:
            instruction_List.clear()
            instruction_List.addItems(instruction_values.keys())

        if instruction_values and instruction_List:
            instruction_List.setCurrentIndex(index)

    def retrieve_docs_changed(self, value, name):
        self._settings.setValue(f"{name}_Model_Parameter/retrieve_docs", value)

    def search_result_changed(self, value, name):
        self._settings.setValue(f"{name}_Model_Parameter/search_result", value)

    def max_retry_changed(self, value, name):
        self._settings.setValue(f"{name}_Model_Parameter/max_retry", value)

    def chunk_overlap_changed(self, value, name):
        self._settings.setValue(f"{name}_Model_Parameter/chunk_overlap", value)

    def chunk_size_changed(self, value, name):
        self._settings.setValue(f"{name}_Model_Parameter/chunk_size", value)

    def embedding_changed(self, value, name):
        self._settings.setValue(f"{name}_Model_Parameter/embedding", value)

    def vector_store_changed(self, value, name):
        self._settings.setValue(f"{name}_Model_Parameter/vector_store", value)

    def on_toggle(self):
        sender = self.sender()
        if sender.isChecked():
            print(f'{sender.text()} selected')

    def create_openai_tabcontent(self, name):
        tab_widget = QWidget()
        tab_widget.setObjectName(name)
        layout_main = QVBoxLayout()

        # Langchain Setting Group
        langchain_setting_group = QGroupBox("Langchain setting")
        langchain_setting_group.setObjectName("langchain_setting_group")
        langchain_setting_layout = QFormLayout()

        vector_store_ComboBox = QComboBox()
        vector_store_ComboBox.setObjectName(f"{name}_vector_storeComboBox")
        vector_store_ComboBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        vector_store_ComboBox.addItems(Constants.VECTOR_STORE_LIST)
        vector_store_ComboBox.setCurrentText(
            Utility.get_settings_value(section=f"{name}_Model_Parameter", prop="vector_store",
                                       default="chroma", save=True)
        )
        vector_store_ComboBox.currentTextChanged.connect(lambda value: self.vector_store_changed(value, name))
        langchain_setting_layout.addRow('Vector Store', vector_store_ComboBox)

        embedding_ComboBox = QComboBox()
        embedding_ComboBox.setObjectName(f"{name}_embeddingComboBox")
        embedding_ComboBox.clear()
        embedding_ComboBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.set_embedding_model_list(embedding_ComboBox, name)
        embedding_ComboBox.currentTextChanged.connect(lambda value: self.embedding_changed(value, name))
        langchain_setting_layout.addRow('Embedding', embedding_ComboBox)

        chunk_sizeSpinBox = QSpinBox()
        chunk_sizeSpinBox.setObjectName(f"{name}_chunk_sizeSpinBox")
        chunk_sizeSpinBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        chunk_sizeSpinBox.setRange(100, 128000)
        chunk_sizeSpinBox.setAccelerated(True)
        chunk_sizeSpinBox.setSingleStep(10)
        chunk_sizeSpinBox.setValue(
            int(
                Utility.get_settings_value(section=f"{name}_Model_Parameter", prop="chunk_size",
                                           default="1000", save=True)))
        chunk_sizeSpinBox.valueChanged.connect(lambda value: self.chunk_size_changed(value, name))
        langchain_setting_layout.addRow('Chunk Size', chunk_sizeSpinBox)

        overlapSpinBox = QSpinBox()
        overlapSpinBox.setObjectName(f"{name}_chunk_overlapSpinBox")
        overlapSpinBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        overlapSpinBox.setRange(100, 10000)
        overlapSpinBox.setAccelerated(True)
        overlapSpinBox.setSingleStep(10)
        overlapSpinBox.setValue(
            int(
                Utility.get_settings_value(section=f"{name}_Model_Parameter", prop="chunk_overlap",
                                           default="300", save=True)))
        overlapSpinBox.valueChanged.connect(lambda value: self.chunk_overlap_changed(value, name))
        langchain_setting_layout.addRow('Chunk Overlap', overlapSpinBox)

        retrieve_docsSpinBox = QSpinBox()
        retrieve_docsSpinBox.setObjectName(f"{name}_retrieve_docsSpinBox")
        retrieve_docsSpinBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        retrieve_docsSpinBox.setRange(1, 30)
        retrieve_docsSpinBox.setAccelerated(True)
        retrieve_docsSpinBox.setSingleStep(1)
        retrieve_docsSpinBox.setValue(
            int(
                Utility.get_settings_value(section=f"{name}_Model_Parameter", prop="retrieve_docs",
                                           default="3", save=True)))
        retrieve_docsSpinBox.valueChanged.connect(lambda value: self.retrieve_docs_changed(value, name))
        langchain_setting_layout.addRow('Retrieve Docs', retrieve_docsSpinBox)

        langchain_setting_group.setLayout(langchain_setting_layout)
        layout_main.addWidget(langchain_setting_group)

        # Ollama Model Group
        ollama_model_group = QGroupBox(f"{name} Model")
        ollama_model_group.setObjectName("ollama_model_group")
        ollama_model_layout = QFormLayout()
        ollama_model_label = QLabel(f"{name} Model List")
        ollama_model_list = QComboBox()
        ollama_model_list.setObjectName(f"{name}_ModelList")
        ollama_model_list.clear()

        self.set_ollama_model_list(ollama_model_list, name)

        ollama_model_layout.addRow(ollama_model_label)
        ollama_model_layout.addRow(ollama_model_list)
        ollama_model_group.setLayout(ollama_model_layout)
        layout_main.addWidget(ollama_model_group)

        # Document List Group
        document_list_group = QGroupBox("Data Source")
        document_list_layout = QVBoxLayout()
        document_list_group.setLayout(document_list_layout)

        # Add QListWidget to show selected file list
        filelist_widget = QListWidget()
        filelist_widget.setObjectName(f"{name}_FileList")
        document_list_layout.addWidget(filelist_widget)

        # Add buttons
        buttons_layout = QHBoxLayout()
        select_button = QPushButton(QIcon(Utility.get_icon_path('ico', 'documents-text.png')), "File")
        select_button.setObjectName(f"{name}_SelectButton")

        delete_button = QPushButton(QIcon(Utility.get_icon_path('ico', 'folder--minus.png')), "Remove")
        delete_button.setObjectName(f"{name}_DeleteButton")
        delete_button.setEnabled(False)

        buttons_layout.addWidget(select_button)
        buttons_layout.addWidget(delete_button)

        document_list_layout.addLayout(buttons_layout)

        submit_layout = QHBoxLayout()
        submit_button = QPushButton(QIcon(Utility.get_icon_path('ico', 'inbox-document-text.png')),
                                    "Document Preprocessing")
        submit_button.setObjectName(f"{name}_SubmitButton")
        submit_button.setEnabled(False)

        reset_button = QPushButton(QIcon(Utility.get_icon_path('ico', 'arrow-circle-double.png')),
                                   "Reset")
        reset_button.setObjectName(f"{name}_ResetButton")
        reset_button.clicked.connect(
            lambda: self.toggle_setting_group('langchain_setting_group', 'ollama_model_group'))
        reset_button.setEnabled(False)

        submit_layout.addWidget(submit_button)
        submit_layout.addWidget(reset_button)

        document_list_layout.addLayout(submit_layout)

        select_button.clicked.connect(partial(self.select_files, name))
        delete_button.clicked.connect(partial(self.delete_file, name))
        submit_button.clicked.connect(partial(self.submit_file, name))

        filelist_widget.itemSelectionChanged.connect(partial(self.on_item_selection_changed, name))
        layout_main.addWidget(document_list_group)

        # Tavily Search Group
        tavily_search_group = QGroupBox("Tavily Search Parameters")
        tavily_search_layout = QFormLayout()

        max_retrySpinBox = QSpinBox()
        max_retrySpinBox.setObjectName(f"{name}_max_retrySpinBox")
        max_retrySpinBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        max_retrySpinBox.setRange(1, 10)
        max_retrySpinBox.setAccelerated(True)
        max_retrySpinBox.setSingleStep(1)
        max_retrySpinBox.setValue(
            int(
                Utility.get_settings_value(section=f"{name}_Model_Parameter", prop="max_retry",
                                           default="3", save=True)))
        max_retrySpinBox.valueChanged.connect(lambda value: self.max_retry_changed(value, name))
        tavily_search_layout.addRow('Max Retry', max_retrySpinBox)

        search_resultSpinBox = QSpinBox()
        search_resultSpinBox.setObjectName(f"{name}_search_resultSpinBox")
        search_resultSpinBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        search_resultSpinBox.setRange(1, 10)
        search_resultSpinBox.setAccelerated(True)
        search_resultSpinBox.setSingleStep(1)
        search_resultSpinBox.setValue(
            int(
                Utility.get_settings_value(section=f"{name}_Model_Parameter", prop="search_result",
                                           default="3", save=True)))
        search_resultSpinBox.valueChanged.connect(lambda value: self.search_result_changed(value, name))
        tavily_search_layout.addRow('Search Result', search_resultSpinBox)

        tavily_search_group.setLayout(tavily_search_layout)
        layout_main.addWidget(tavily_search_group)

        tab_widget.setLayout(layout_main)

        return tab_widget

    def toggle_setting_group(self, langchain_setting_group_name, ollama_model_group_name):
        submitButton = self.findChild(QPushButton, f"{self._current_chat_llm}_SubmitButton")
        is_disabled = submitButton.isEnabled()
        submitButton.setEnabled(not is_disabled)

        reset_button = self.findChild(QPushButton, f"{self._current_chat_llm}_ResetButton")
        reset_button.setEnabled(is_disabled)

        langchain_setting_group = self.findChild(QGroupBox, langchain_setting_group_name)
        langchain_setting_group.setEnabled(not is_disabled)

        ollama_model_group = self.findChild(QGroupBox, ollama_model_group_name)
        ollama_model_group.setEnabled(not is_disabled)

    def create_prompt_tabcontent(self, name, instruction):
        tabWidget = QWidget()
        tabWidget.setObjectName(name)
        layoutMain = QVBoxLayout()

        groupSystem = self.create_prompt_layout(name, instruction)
        layoutMain.addWidget(groupSystem)

        tabWidget.setLayout(layoutMain)

        return tabWidget

    def set_ollama_model_list(self, modelList, name):
        modelList.addItems(Utility.get_ollama_ai_model_list())
        llm_model = Utility.get_settings_value(
            section=f"{name}_Model_Parameter",
            prop="model_name",
            default='llama3.2:3b-instruct-fp16',
            save=True
        )
        modelList.setCurrentIndex(modelList.findText(llm_model))
        modelList.currentTextChanged.connect(lambda current_text: self.ollama_model_list_changed(current_text, name))

    def set_embedding_model_list(self, modelList, name):
        modelList.addItems(Utility.get_embedding_model_list())
        llm_model = Utility.get_settings_value(
            section=f"{name}_Model_Parameter",
            prop="embedding",
            default='nomic-ai/nomic-embed-text-v1.5',
            save=True
        )
        modelList.setCurrentIndex(modelList.findText(llm_model))
        modelList.currentTextChanged.connect(lambda current_text: self.embedding_model_list_changed(current_text, name))

    def select_files(self, llm):
        fileListWidget = self.findChild(QListWidget, f"{llm}_FileList")
        selected_files = self.show_file_dialog(llm)
        if selected_files is None:
            selected_files = []
        for file in selected_files:
            fileListWidget.addItem(file)
        self.update_submit_status(llm)

    def delete_file(self, llm):
        fileListWidget = self.findChild(QListWidget, f"{llm}_FileList")
        for item in fileListWidget.selectedItems():
            fileListWidget.takeItem(fileListWidget.row(item))
        self.update_submit_status(llm)

    def update_submit_status(self, llm):
        fileListWidget = self.findChild(QListWidget,
                                        f"{llm}_FileList")
        submitButton = self.findChild(QPushButton,
                                      f"{llm}_SubmitButton")
        submitButton.setEnabled(bool(fileListWidget.count()))

    def on_item_selection_changed(self, llm):
        fileListWidget = self.findChild(QListWidget,
                                        f"{llm}_FileList")
        deleteButton = self.findChild(QPushButton,
                                      f"{llm}_DeleteButton")
        deleteButton.setEnabled(bool(fileListWidget.selectedItems()))

        submitButton = self.findChild(QPushButton,
                                      f"{llm}_SubmitButton")
        submitButton.setEnabled(bool(fileListWidget.count()))

    def show_file_dialog(self, llm=None):
        file_filter = UI.TEXT_PDF_WORD_FILTER

        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter(file_filter)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            return selected_files
        else:
            return None

    def validate_input(self, file_list):
        if not file_list:
            self.show_warning(UI.WARNING_TITLE_SELECT_FILE_MESSAGE)
            return False
        return True

    def submit_file(self, llm):
        args = {
            'device': Utility.get_torch_device(),
            'vector_store': self.get_vector_store(),
            'embedding_model': self.get_embedding_model(),
            'chunk_size': self.get_chunking_size(),
            'chunk_overlap': self.get_chunk_overlap(),
            'retrieve_docs': self.get_retrieve_docs(),
        }
        input_file_path = self.get_selected_file(llm)
        args['file_path'] = input_file_path
        if not self.validate_input(input_file_path):
            return
        if input_file_path:
            self.submitted_file_signal.emit(args)

    def get_selected_file(self, llm):
        fileListWidget = self.findChild(QListWidget, f"{llm}_FileList")
        if fileListWidget.count() == 0:
            return
        return fileListWidget.item(0).text()

    def show_warning(self, message):
        QMessageBox.warning(self, UI.WARNING_TITLE, message)

    def ollama_model_list_changed(self, current_text, name):
        self._settings.setValue(f"{name}_Model_Parameter/model_name", current_text)

    def embedding_model_list_changed(self, current_text, name):
        self._settings.setValue(f"{name}_Model_Parameter/embedding", current_text)

    def stopsequences_changed(self, value, name):
        if name == AIProviderName.OPENAI.value or name == AIProviderName.OLLAMA.value:
            self._settings.setValue(f"{name}_Model_Parameter/stop", value)
        else:
            self._settings.setValue(f"{name}_Model_Parameter/stop_sequences", value)

    def temperature_changed(self, value, name):
        self._settings.setValue(f"{name}_Model_Parameter/temperature", value)

    def topp_changed(self, value, name):
        self._settings.setValue(f"{name}_Model_Parameter/top_p", value)

    def topk_changed(self, value, name):
        self._settings.setValue(f"{name}_Model_Parameter/top_k", value)

    def numpredict_changed(self, value, name):
        self._settings.setValue(f"{name}_Model_Parameter/num_predict", value)

    def maxtokens_changed(self, value, name):
        self._settings.setValue(f"{name}_Model_Parameter/max_tokens", value)

    def maxoutputtokens_changed(self, value, name):
        self._settings.setValue(f"{name}_Model_Parameter/max_output_tokens", value)

    def frequency_penalty_changed(self, value, name):
        self._settings.setValue(f"{name}_Model_Parameter/frequency_penalty", value)

    def presence_penalty_changed(self, value, name):
        self._settings.setValue(f"{name}_Model_Parameter/presence_penalty", value)

    def seed_changed(self, value, name):
        self._settings.setValue(f"{name}_Model_Parameter/seed", value)

    def stream_changed(self, checked, name):
        if checked:
            self._settings.setValue(f"{name}_Model_Parameter/stream", 'True')
        else:
            self._settings.setValue(f"{name}_Model_Parameter/stream", 'False')

    def create_prompt_layout(self, name, instruction=False):
        groupSystem = QGroupBox(f"{name} Prompt")

        promptLayout = QFormLayout()
        promptLabel = QLabel("Select Prompt")
        promptList = QComboBox()
        promptList.setObjectName(f"{name}_promptList")
        prompt_values = Utility.get_system_value(section=f"{name}_Prompt", prefix="prompt",
                                                 default="You are a helpful assistant.", length=3)
        promptList.addItems(prompt_values.keys())
        promptList.currentIndexChanged.connect(lambda: self.on_prompt_change(name))

        current_prompt = QTextEdit()
        current_prompt.setObjectName(f"{name}_current_prompt")
        current_prompt.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        current_prompt.setText(prompt_values['prompt1'])

        save_prompt_button = QPushButton(QIcon(Utility.get_icon_path('ico', 'disk-black.png')), 'Save')
        save_prompt_button.clicked.connect(lambda: self.save_prompt_value(name))

        promptLayout.addRow(promptLabel)
        promptLayout.addRow(promptList)
        promptLayout.addRow(current_prompt)
        promptLayout.addRow(save_prompt_button)

        groupSystem.setLayout(promptLayout)

        if instruction:
            instructionLayout = QFormLayout()
            instructionLabel = QLabel("Select Instruction")
            instructionList = QComboBox()
            instructionList.setObjectName(f"{name}_instructionList")
            instruction_values = Utility.get_system_value(section=f"{name}_Instruction", prefix="instruction",
                                                          default="You are a helpful assistant.", length=3)
            instructionList.addItems(instruction_values.keys())
            instructionList.currentIndexChanged.connect(lambda: self.on_instruction_change(name))

            current_instruction = QTextEdit()
            current_instruction.setObjectName(f"{name}_current_instruction")
            current_instruction.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
            current_instruction.setText(instruction_values['instruction1'])

            save_instruction_button = QPushButton(QIcon(Utility.get_icon_path('ico', 'disk-black.png')), 'Save')
            save_instruction_button.clicked.connect(lambda: self.save_instruction_value(name))

            instructionLayout.addRow(instructionLabel)
            instructionLayout.addRow(instructionList)
            instructionLayout.addRow(current_instruction)
            instructionLayout.addRow(save_instruction_button)

            # Add instruction layout to the main layout
            promptLayout.addRow(instructionLayout)

        return groupSystem

    def create_chatdb_tab(self):
        layoutWidget = QWidget()
        layout = QVBoxLayout()

        self._chat_history = ChatHistory(self.model)

        layout.addWidget(self._chat_history)

        layoutWidget.setLayout(layout)
        return layoutWidget

    def create_system_tab(self):
        layoutWidget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("System"))

        layoutWidget.setLayout(layout)
        return layoutWidget

    def update_ui_submit(self, chatType, image_data, text):
        self.add_user_question(chatType, image_data, text)
        self.stop_widget.setVisible(True)

    def add_user_question(self, chatType, image_data, text):
        if image_data:
            user_question = ImageWidget(chatType, image_data, text)
        else:
            user_question = ChatWidget(chatType, text)
        self.result_layout.addWidget(user_question)

    def adjust_scroll_bar(self, min_val, max_val):
        self.ai_answer_scroll_area.verticalScrollBar().setSliderPosition(max_val)

    def update_ui(self, image_data, response_text):
        ai_answer = ImageWidget(ChatType.AI, image_data, response_text)
        self.result_layout.addWidget(ai_answer)

    def update_ui_finish(self, model, finish_reason, elapsed_time, stream):
        chatWidget = self.get_last_ai_widget()
        self.stop_widget.setVisible(False)

        if chatWidget and chatWidget.get_chat_type() == ChatType.AI:
            chatWidget.set_model_name(
                Constants.MODEL_PREFIX + model + Constants.RESPONSE_TIME + format(elapsed_time, ".2f"))

    def get_last_ai_widget(self) -> ImageWidget | None:
        layout_item = self.result_widget.layout().itemAt(self.result_widget.layout().count() - 1)
        if layout_item:
            last_ai_widget = layout_item.widget()
            if last_ai_widget.get_chat_type() == ChatType.AI:
                return last_ai_widget
        else:
            return None

    def handle_submitted_signal(self, text):
        if text:
            self.submitted_signal.emit(text)

    def start_chat(self):
        self.prompt_text.clear()
        self.prompt_text.setEnabled(False)

    def finish_chat(self):
        self.prompt_text.setEnabled(True)
        self.prompt_text.setFocus()

    def clear_prompt(self):
        self.prompt_text.clear()

    def set_focus(self):
        self.prompt_text.setFocus()

    def set_prompt(self, prompt):
        self.prompt_text.setText(prompt)

    def get_all_text(self):
        question = Utility.get_settings_value(section="AI_Provider", prop="question",
                                              default="[Question]", save=True)

        answer = Utility.get_settings_value(section="AI_Provider", prop="answer",
                                            default="[Answer]", save=True)

        all_previous_qa = []
        for i in range(self.result_layout.count()):
            current_widget = self.result_layout.itemAt(i).widget()
            if current_widget.get_chat_type() == ChatType.HUMAN and len(current_widget.get_text()) > 0:
                all_previous_qa.append(f'{question}: {current_widget.get_text()}')
            elif current_widget.get_chat_type() == ChatType.AI and len(current_widget.get_text()) > 0:
                all_previous_qa.append(f'{answer}: {current_widget.get_text()}')
        return '\n'.join(all_previous_qa)

    def create_prompt_list(self):
        prompt_list = {}

        # Collecting prompts and instructions
        prompt_list['router_instruction'] = self.findChild(QTextEdit, 'Router_current_prompt').toPlainText()
        prompt_list['rag_prompt'] = self.findChild(QTextEdit, 'RAG_current_prompt').toPlainText()

        prompt_list['doc_grader_prompt'] = self.findChild(QTextEdit, 'Document_current_prompt').toPlainText()
        prompt_list['doc_grader_instruction'] = self.findChild(QTextEdit,
                                                               'Document_current_instruction').toPlainText()

        prompt_list['hallucination_grader_prompt'] = self.findChild(QTextEdit,
                                                                    'Hallucination_current_prompt').toPlainText()
        prompt_list['hallucination_grader_instruction'] = self.findChild(QTextEdit,
                                                                         'Hallucination_current_instruction').toPlainText()

        prompt_list['answer_grader_prompt'] = self.findChild(QTextEdit, 'Answer_current_prompt').toPlainText()
        prompt_list['answer_grader_instruction'] = self.findChild(QTextEdit,
                                                                  'Answer_current_instruction').toPlainText()

        return prompt_list

    def clear_all(self):
        target_layout = self.result_layout
        if target_layout is not None:
            while target_layout.count():
                item = target_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

    def force_stop(self):
        self.stop_signal.emit()
        self.stop_widget.setVisible(False)

    @property
    def chat_history(self):
        return self._chat_history

    def get_retrieve_docs(self):
        return self.findChild(QSpinBox, f'{self._current_chat_llm}_retrieve_docsSpinBox').value()

    def get_chunking_size(self):
        return self.findChild(QSpinBox, f'{self._current_chat_llm}_chunk_sizeSpinBox').value()

    def get_chunk_overlap(self):
        return self.findChild(QSpinBox, f'{self._current_chat_llm}_chunk_overlapSpinBox').value()

    def get_vector_store(self):
        return self.findChild(QComboBox, f'{self._current_chat_llm}_vector_storeComboBox').currentText()

    def get_embedding_model(self):
        return self.findChild(QComboBox, f'{self._current_chat_llm}_embeddingComboBox').currentText()

    def get_llm_name(self):
        return self.findChild(QComboBox, f'{self._current_chat_llm}_ModelList').currentText()

    def get_search_result(self):
        return self.findChild(QSpinBox, f'{self._current_chat_llm}_search_resultSpinBox').value()

    def get_max_retries(self):
        return self.findChild(QSpinBox, f'{self._current_chat_llm}_max_retrySpinBox').value()
