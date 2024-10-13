import os
import time

from PyQt6.QtCore import QThread, pyqtSignal
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader, Docx2txtLoader
from langchain_community.vectorstores import SKLearnVectorStore, FAISS
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from util.Constants import Constants, UI


class MyDocumentThread(QThread):
    document_preprocess_error_signal = pyqtSignal(str)
    document_preprocess_finished_signal = pyqtSignal(str, str, float)
    retriever_signal = pyqtSignal(VectorStoreRetriever)

    def __init__(self, args):
        super().__init__()
        self.device = args['device']
        self.vector_store = args['vector_store']
        self.embedding_model = args['embedding_model']
        self.chunk_size = args['chunk_size']
        self.chunk_overlap = args['chunk_overlap']
        self.retrieve_docs = args['retrieve_docs']
        self.file_path = args['file_path']
        self.force_stop = False

    def run(self):
        self.start_time = time.time()
        try:
            if not os.path.isfile(self.file_path):
                raise FileNotFoundError(f"File not found: {self.file_path}")

            # Document load
            loader = DocumentFactory.create_document_loader(self.file_path)
            docs_list = loader.load()

            # Split documents
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
            )
            doc_splits = text_splitter.split_documents(docs_list)

            # Embedding model
            model_name = self.embedding_model
            model_kwargs = {"device": self.device, 'trust_remote_code': True}
            hf = HuggingFaceEmbeddings(
                model_name=model_name, model_kwargs=model_kwargs
            )

            # Add to vectorDB
            vector_store = VectorStoreFactory.create_vector_store(
                self.vector_store,
                documents=doc_splits,
                embedding=hf,
            )
            retriever = vector_store.as_retriever(k=self.retrieve_docs)
            self.retriever_signal.emit(retriever)
            self.finish_run(self.embedding_model, Constants.NORMAL_STOP)
        except Exception as e:
            self.document_preprocess_error_signal.emit(str(e))

    def set_force_stop(self, force_stop):
        self.force_stop = force_stop

    def finish_run(self, model, finish_reason):
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        self.document_preprocess_finished_signal.emit(model, finish_reason, elapsed_time)


class DocumentFactory:
    @staticmethod
    def create_document_loader(file_path: str):
        if file_path.endswith('.txt'):
            return TextLoader(file_path, encoding='utf-8')
        elif file_path.endswith('.pdf'):
            return PyMuPDFLoader(file_path)
        elif file_path.endswith('.docx'):
            return Docx2txtLoader(file_path)
        else:
            raise ValueError(UI.UNSUPPORTED_FILE_TYPE)


class VectorStoreFactory:
    @staticmethod
    def create_vector_store(vector_store: str, documents, embedding):
        if vector_store.lower() == "sklearn":
            return SKLearnVectorStore.from_documents(
                documents=documents,
                embedding=embedding,
            )
        elif vector_store.lower() == "faiss":
            return FAISS.from_documents(
                documents=documents,
                embedding=embedding,
            )
        else:
            raise ValueError(UI.UNSUPPORTED_VECTOR_STORE_TYPE)
