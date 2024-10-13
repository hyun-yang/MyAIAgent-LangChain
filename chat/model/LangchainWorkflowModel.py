from PyQt6.QtCore import QObject, pyqtSignal

from chat.model.LangchainWorkflowThread import LangchainWorkflowThread
from util.Constants import MODEL_MESSAGE


class LangchainWorkflowModel(QObject):
    thread_started_signal = pyqtSignal()
    thread_finished_signal = pyqtSignal()
    response_signal = pyqtSignal(str, str)
    response_finished_signal = pyqtSignal(str, str, float, bool)

    def __init__(self):
        super().__init__()
        self.langchain_workflow_thread = None
        self._prompt_list = None
        self._retriever = None
        self._llm_name = None
        self._search_result = None
        self._max_retries = None

    def handle_thread_finished(self):
        print(f"{MODEL_MESSAGE.THREAD_FINISHED}")
        self.thread_finished_signal.emit()
        self.langchain_workflow_thread = None

    def force_stop(self):
        if self.langchain_workflow_thread is not None:
            self.langchain_workflow_thread.set_force_stop(True)

    def run_workflow(self, question):
        if self.langchain_workflow_thread is not None and self.langchain_workflow_thread.isRunning():
            print(f"{MODEL_MESSAGE.THREAD_RUNNING}")
            self.langchain_workflow_thread.wait()

        args = {}
        args["question"] = question
        args["prompt_list"] = self.prompt_list
        args["retriever"] = self.retriever
        args["llm_name"] = self.llm_name
        args["search_result"] = self.search_result
        args["max_retries"] = self.max_retries

        self.langchain_workflow_thread = LangchainWorkflowThread(args)
        self.langchain_workflow_thread.started.connect(self.thread_started_signal.emit)
        self.langchain_workflow_thread.finished.connect(self.handle_thread_finished)
        self.langchain_workflow_thread.response_signal.connect(self.response_signal.emit)
        self.langchain_workflow_thread.response_finished_signal.connect(self.response_finished_signal.emit)
        self.langchain_workflow_thread.start()

    @property
    def retriever(self):
        return self._retriever

    @retriever.setter
    def retriever(self, value):
        self._retriever = value

    @property
    def prompt_list(self):
        return self._prompt_list

    @prompt_list.setter
    def prompt_list(self, value):
        self._prompt_list = value

    @property
    def max_retries(self):
        return self._max_retries

    @max_retries.setter
    def max_retries(self, value):
        self._max_retries = value

    @property
    def llm_name(self):
        return self._llm_name

    @llm_name.setter
    def llm_name(self, value):
        self._llm_name = value

    @property
    def search_result(self):
        return self._search_result

    @search_result.setter
    def search_result(self, value):
        self._search_result = value
