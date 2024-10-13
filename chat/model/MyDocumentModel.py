from PyQt6.QtCore import QObject, pyqtSignal
from langchain_core.vectorstores import VectorStoreRetriever

from chat.model.MyDocumentThread import MyDocumentThread
from util.Constants import MODEL_MESSAGE, FILE_INDEX_MESSAGE


class MyDocumentModel(QObject):
    thread_started_signal = pyqtSignal()
    thread_finished_signal = pyqtSignal()

    document_preprocess_error_signal = pyqtSignal(str)
    document_preprocess_finished_signal = pyqtSignal(str, str, float)
    retriever_signal = pyqtSignal(VectorStoreRetriever)

    def __init__(self):
        super().__init__()
        self.my_document_thread = None
        self.retriever = None

    def prepare_document(self, args):
        if self.my_document_thread is not None and self.my_document_thread.isRunning():
            print(f"{FILE_INDEX_MESSAGE.THREAD_RUNNING}")
            self.my_document_thread.wait()

        self.my_document_thread = MyDocumentThread(args)
        self.my_document_thread.started.connect(self.thread_started_signal.emit)
        self.my_document_thread.finished.connect(self.handle_thread_finished)

        self.my_document_thread.document_preprocess_error_signal.connect(self.document_preprocess_error_signal.emit)
        self.my_document_thread.document_preprocess_finished_signal.connect(
            self.document_preprocess_finished_signal.emit)

        self.my_document_thread.retriever_signal.connect(self.retriever_signal.emit)
        self.my_document_thread.start()

    def handle_thread_finished(self):
        print(f"{MODEL_MESSAGE.THREAD_FINISHED}")
        self.thread_finished_signal.emit()
        self.my_document_thread = None

    def get_retriever_docs(self, retriever):
        self.retriever = retriever

    def force_stop(self):
        if self.my_document_thread is not None:
            self.my_document_thread.set_force_stop(True)
