import os

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QDialog, QMessageBox
from langchain_core.vectorstores import VectorStoreRetriever

from chat.model.LangchainWorkflowModel import LangchainWorkflowModel
from chat.model.MyDocumentModel import MyDocumentModel
from chat.view.ChatView import ChatView
from custom.ChatListModel import ChatListModel
from util.ChatType import ChatType
from util.ConfirmationDialog import ConfirmationDialog
from util.Constants import Constants, UI, LANGCHAIN_CONSTANT
from util.DataManager import DataManager
from util.SettingsManager import SettingsManager
from util.Utility import Utility


class ChatPresenter(QWidget):

    def __init__(self):
        super().__init__()
        self._chat_main_id = None
        self._chat_main_index = None
        self.retriever = None
        self.graph = None
        self.image_data = None
        self.langchain_rag_ready = False
        self.initialize_manager()
        self.initialize_langchain()
        self.initialize_ui()

    def initialize_langchain(self):
        os.environ["TAVILY_API_KEY"] = Utility.get_settings_value(section="Langchain", prop="tavily_api_key",
                                                                  default="TAVILY_API_KEY", save=True)
        os.environ["LANGCHAIN_API_KEY"] = Utility.get_settings_value(section="Langchain", prop="langchain_api_key",
                                                                     default="LANGCHAIN_API_KEY", save=True)
        os.environ["LANGCHAIN_TRACING_V2"] = Utility.get_settings_value(section="Langchain",
                                                                        default="true", prop="langchain_tracing_v2",
                                                                        save=True)
        os.environ["LANGCHAIN_ENDPOINT"] = Utility.get_settings_value(section="Langchain", prop="langchain_endpoint",
                                                                      default="LANGCHAIN_ENDPOINT", save=True)
        os.environ["LANGCHAIN_PROJECT"] = Utility.get_settings_value(section="Langchain", prop="langchain_project",
                                                                     default="LANGCHAIN_PROJECT", save=True)

    def initialize_manager(self):
        self._settings = SettingsManager.get_settings()
        self._database = DataManager.get_database()
        self.llm = Utility.get_settings_value(section="AI_Provider", prop="llm", default="Ollama", save=True)

    def initialize_ui(self):

        # View
        self.chatViewModel = ChatListModel(self._database)
        self.chatViewModel.new_chat_main_id_signal.connect(self.set_chat_main_id)
        self.chatViewModel.remove_chat_signal.connect(self.clear_chat)
        self.chatView = ChatView(self.chatViewModel)

        # Model
        self.workflowModel = LangchainWorkflowModel()
        self.workflowModel.thread_started_signal.connect(self.chatView.start_chat)
        self.workflowModel.thread_finished_signal.connect(self.chatView.finish_chat)
        self.workflowModel.response_signal.connect(self.handle_response_signal)
        self.workflowModel.response_finished_signal.connect(self.handle_response_finished_signal)

        # View signal
        self.chatView.submitted_file_signal.connect(self.document_preprocessing)
        self.chatView.submitted_signal.connect(self.submit)
        self.chatView.stop_signal.connect(self.workflowModel.force_stop)
        self.chatView.chat_llm_signal.connect(self.set_current_llm_signal)
        self.chatView.reload_chat_detail_signal.connect(self.show_chat_detail)

        self.chatView.chat_history.new_chat_signal.connect(self.create_new_chat)
        self.chatView.chat_history.delete_chat_signal.connect(self.confirm_delete_chat)
        self.chatView.chat_history.chat_list.delete_id_signal.connect(self.delete_chat_table)
        self.chatView.chat_history.filter_signal.connect(self.filter_list)

        self.chatView.set_default_tab(self.llm)

        self.initialize_chat_history()

        # Document Model
        self.documentModel = MyDocumentModel()
        self.documentModel.document_preprocess_finished_signal.connect(self.handle_document_preprocess_finished_signal)
        self.documentModel.retriever_signal.connect(self.handle_retriever_signal)

        # View
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.chatView)

        self.setLayout(main_layout)

    def initialize_chat_history(self):
        self.chat_list = self.chatView.chat_history.chat_list
        self.chat_list.chat_id_signal.connect(self.show_chat_detail)

    def set_chat_main_id(self, chat_main_id):
        self.chat_main_id = chat_main_id
        self.view.clear_all()

    @pyqtSlot(str, str)
    def handle_response_signal(self, image_data, response_text):
        if response_text.lower() == 'error':
            # The possible values for image_data here, 'max_retries reached or not supported'.
            QMessageBox.information(self, image_data,
                                    LANGCHAIN_CONSTANT.UNABLE_TO_FIND_AN_ANSWER)
            self.chatView.stop_widget.setVisible(False)
            self.workflowModel.response_finished_signal.emit('N/A', response_text.lower(), 0.0, False)
            return

        self.image_data = image_data
        self.response_text = response_text
        self.chatView.update_ui(self.image_data, response_text)

    @pyqtSlot(str, str, float, bool)
    def handle_response_finished_signal(self, model, finish_reason, elapsed_time, stream):
        last_ai_widget = self.view.get_last_ai_widget()
        if last_ai_widget:
            self.chatView.update_ui_finish(model, finish_reason, elapsed_time, stream)
            self._database.insert_chat_detail(self.chat_main_id, ChatType.AI.value, model,
                                              self.response_text, self.image_data, elapsed_time, finish_reason)

    @property
    def view(self):
        return self.chatView

    @property
    def chat_main_id(self):
        return self._chat_main_id

    @chat_main_id.setter
    def chat_main_id(self, value):
        self._chat_main_id = value

    @pyqtSlot(str)
    def set_current_llm_signal(self, llm_name):
        self.llm = llm_name

    @pyqtSlot(int)
    def clear_chat(self, delete_id):
        if self.chat_main_id == delete_id:
            self.chat_main_id = None
            self.view.clear_all()

    @pyqtSlot()
    def confirm_delete_chat(self):
        if self.chat_main_id:
            title = UI.CONFIRM_DELETION_TITLE
            message = UI.CONFIRM_DELETION_CHAT_MESSAGE
            dialog = ConfirmationDialog(title, message)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.delete_chat(self.chatViewModel.get_index_by_chat_main_id(self.chat_main_id))
        else:
            QMessageBox.information(self, UI.DELETE, UI.CONFIRM_CHOOSE_CHAT_MESSAGE)

    @pyqtSlot(int)
    def delete_chat_table(self, id):
        self._database.delete_chat_main(id)

    @pyqtSlot(str)
    def filter_list(self, text):
        self.chatViewModel.filter_by_title(text)

    def show_chat_detail(self, id):
        if id == -1:
            self.get_chat_detail(self.chat_main_id)
        elif id != self.chat_main_id:
            self.chat_main_id = id
            self.get_chat_detail(self.chat_main_id)

    def get_chat_detail(self, id):
        self.view.clear_all()
        self.view.reset_search_bar()
        chat_detail_list = self._database.get_all_chat_details_list(id)
        for chat_detail in chat_detail_list:
            if chat_detail['chat_type'] == ChatType.HUMAN.value:
                self.view.add_user_question(ChatType.HUMAN, chat_detail['image_data'], chat_detail['chat'])
            else:
                self.view.add_user_question(ChatType.AI, chat_detail['image_data'], chat_detail['chat'])
                self.view.get_last_ai_widget().set_model_name(
                    Constants.MODEL_PREFIX + chat_detail['chat_model']
                    + Constants.RESPONSE_TIME + format(float(chat_detail['elapsed_time']), ".2f"))

    def delete_chat(self, index):
        self.chatViewModel.remove_chat(index)

    def create_new_chat(self, title=Constants.NEW_CHAT):
        self.chatViewModel.add_new_chat(title)

    def add_human_chat(self, text):
        if self.chat_main_id:
            self._database.insert_chat_detail(self.chat_main_id, ChatType.HUMAN.value, None, text, None, None, None)
        else:
            self.create_new_chat()
            self._database.insert_chat_detail(self.chat_main_id, ChatType.HUMAN.value, None, text, None, None, None)

    def update_chat(self, index, new_title):
        self.chatViewModel.update_chat(index, new_title)

    def read_chat(self, index):
        return self.chatViewModel.get_chat(index)

    # Langchain
    @pyqtSlot(str, str, float)
    def handle_document_preprocess_finished_signal(self, model, finish_reason, elapsed_time):
        self.langchain_rag_ready = True
        QMessageBox.information(self, LANGCHAIN_CONSTANT.DOCUMENT_PROCESS_FINISHED,
                                LANGCHAIN_CONSTANT.ENTER_YOUR_PROMPT)

    @pyqtSlot(VectorStoreRetriever)
    def handle_retriever_signal(self, retriever):
        self.retriever = retriever
        self.workflowModel.retriever = retriever
        self.workflowModel.prompt_list = self.chatView.create_prompt_list()
        self.workflowModel.llm_name = self.chatView.get_llm_name()
        self.workflowModel.max_retries = self.chatView.get_max_retries()
        self.workflowModel.search_result = self.chatView.get_search_result()

    @pyqtSlot(object)
    def document_preprocessing(self, args):
        self.documentModel.prepare_document(args)
        self.view.toggle_setting_group('langchain_setting_group', 'ollama_model_group')

    @pyqtSlot(str)
    def submit(self, text):
        if text and text.strip() and self.langchain_rag_ready:
            self.add_human_chat(text)
            self.chatView.update_ui_submit(ChatType.HUMAN, None, text)
            self.workflowModel.run_workflow({"question": text})
        else:
            QMessageBox.warning(self, UI.FILE_INDEXING, UI.RUN_FILE_INDEXING)
