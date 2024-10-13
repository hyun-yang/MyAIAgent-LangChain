from enum import Enum, auto


class Constants:
    # Application Title
    APPLICATION_TITLE = "MyAIAgent-LangChain/LangGraph/LangSmith/Ollama"

    # Setting file name
    SETTINGS_FILENAME = "settings.ini"

    # App Style
    FUSION = 'Fusion'

    # API Call User Stop
    MODEL_PREFIX = "Model: "
    ELAPSED_TIME = "Elapsed Time: "
    FINISH_REASON = "Finish Reason: "

    FORCE_STOP = "Force Stop"
    NORMAL_STOP = "stop"
    RESPONSE_TIME = " | Response Time : "

    # Ollama Model List
    OLLAMA_MODEL_LIST_SECTION = "Ollama_Model_List"
    OLLAMA_MODEL_LIST = [
        "llama3.2:3b-instruct-fp16",
        "llama3.2:3b-text-fp16",
        "gemma2:27b"
    ]

    # Embedding Model List
    EMBEDDING_LIST_SECTION = "Embedding_Model_List"
    EMBEDDING_LIST = [
        "nomic-ai/nomic-embed-text-v1.5",
        "BAAI/bge-m3",
        "BAAI/bge-base-en-v1.5",
        "BAAI/bge-small-en",
    ]

    # Database
    DATABASE_NAME = "myaiagent.db"
    SQLITE_DATABASE = "QSQLITE"

    CHAT_MAIN_TABLE = "chat_main"
    CHAT_DETAIL_TABLE = "chat_detail"
    CHAT_PROMPT_TABLE = "prompt"

    NEW_CHAT = "New Chat"

    # For splitter
    FILE_TYPE_LIST = [
        "text",
        "pdf",
        "Url"
    ]

    VECTOR_STORE_LIST = [
        "SKLearn",
        "FAISS",
    ]

    RESPONSE_FORMAT_B64_JSON = "b64_json"
    SCALE_RATIO = 1.1

    ABOUT_TEXT = (
        "<b>MyAIAgent</b><br>"
        "Version: 1.0.0<br><br>"
        "Author: Hayden Yang(양 현석)<br>"
        "Github: <a href='https://github.com/hyun-yang'>https://github.com/hyun-yang</a><br><br>"
        "Contact: iamyhs@gmail.com<br>"
    )

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise ValueError(f"Cannot reassign constant '{name}'")
        self.__dict__[name] = value


class LANGCHAIN_CONSTANT:
    # Langchain Constant
    ERROR = "Error"
    MAX_RETRIES_REACHED = "max_retries reached or not supported"
    UNABLE_TO_FIND_AN_ANSWER = "Unable to find an answer that matches the question. Please ask a new question or adjust the Max Retry value."
    ENTER_YOUR_PROMPT = "Enter your prompt"
    DOCUMENT_PROCESS_FINISHED = "Document process finished"

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise ValueError(f"Cannot reassign constant '{name}'")
        self.__dict__[name] = value


class UI:
    FILE = "File"
    VIEW = "View"
    HELP = "Help"

    UI = "UI"
    FOUNDS = "founds"
    NOT_FOUND = "not found"
    METHOD = "Method "

    AI_AGENT = "AI Agent"
    AI_AGENT_QA_LIST = "Agent QA List"

    CHAT = "Chat"
    CHAT_TIP = "Chat"
    CHAT_LIST = "Chat List"

    SETTING = "Setting"
    SETTING_TIP = "Setting"

    CLOSE = "Close"
    CLOSE_TIP = "Exit App"

    ABOUT = "About..."
    ABOUT_TIP = "About"

    ADD = "Add"
    DELETE = "Delete"
    RENAME = "Rename"
    STOP = "Stop"
    SAVE = "Save"
    COPY = "Copy"
    PLAY = "Play"
    PAUSE = "Pause"
    ZOOM_IN = "+Zoom"
    ZOOM_OUT = "-Zoom"
    CLEAR_ALL = "Clear All"
    COPY_ALL = "Copy All"
    RELOAD_ALL = "Reload All"
    OK = "Ok"
    CANCEL = "Cancel"
    SUCCESS = "Success"
    ERROR = "Error"

    FILE_READ_IN_BINARY_MODE = 'rb'
    UTF_8 = "utf-8"

    FILE_COPY_SUCCESS = "Files saved successfully!"
    FILE_COPY_ERROR = "An error occurred: "

    CHAT_PROMPT_PLACEHOLDER = "Enter your prompt here."
    SEARCH_PROMPT_PLACEHOLDER = "Enter your search term."
    SEARCH_PROMPT_DB_PLACEHOLDER = "Search..."
    SELECT_FILE_AND_PROMPT_PLACEHOLDER = "Select file and enter your prompt(optional)"
    IMAGE_EDIT_PROMPT_PLACEHOLDER = (
        "Please select two files.\nThe first file should be the original image file. "
        " \nAnd the second file should be the image file with the mask applied.  "
        " \nThen enter the prompt")

    TITLE = "Title"
    PROMPT = "Prompt"

    EXIT_APPLICATION_TITLE = "Exit Application"
    EXIT_APPLICATION_MESSAGE = "Are you sure you want to exit?"

    SAVE_IMAGE_TITLE = "Save Image"
    SAVE_IMAGE_FILTER = "PNG Files (*.png);;All Files (*)"
    IMAGE_PNG = "PNG"

    WARNING_TITLE = "Warning"
    WARNING_API_KEY_SETTING_MESSAGE = "Please set the Langchain / Tavily API key in Setting"
    WARNING_TITLE_NO_ROW_SELECT_MESSAGE = "No row selected for saving."
    WARNING_TITLE_NO_ROW_DELETE_MESSAGE = "No row selected for deletion."
    WARNING_TITLE_SELECT_FILE_MESSAGE = "Select file first."
    WARNING_TITLE_SELECT_FILE_AND_PROMPT_MESSAGE = "Select file and enter your prompt."
    WARNING_TITLE_NO_PROMPT_MESSAGE = "Enter your prompt."
    UNSUPPORTED_VECTOR_STORE_TYPE = "Unsupported vector store type."

    TEXT_PDF_WORD_FILTER = "Doc (*.txt *.pdf *.docx)"
    TEXT_FILTER = "Text (*.txt)"
    PDF_FILTER = "PDF (*.pdf)"
    WORD_FILTER = "Word (*.docx)"

    CONFIRM_DELETION_TITLE = "Confirm Deletion"
    CONFIRM_DELETION_ROW_MESSAGE = "Are you sure you want to delete the selected row?"
    CONFIRM_DELETION_CHAT_MESSAGE = "Are you sure you want to delete this chat?"
    CONFIRM_CHOOSE_CHAT_MESSAGE = "Choose chat first to delete"

    LABEL_ENTER_NEW_NAME = "Enter new name:"

    FAILED_TO_OPEN_FILE = "Failed to open file: "
    FILE_NOT_EXIST = "File does not exist: "
    MEDIA_NOT_LOADED = "Media is not loaded yet."

    AUDIO_SELECT_FOLDER = "Select Folder"
    AUDIO_SAVE = "Save Audio"

    UNSUPPORTED_FILE_TYPE = "Unsupported file type"

    SETTINGS = "Settings"
    SETTINGS_PIXEL = "px"

    ICON_FILE_ERROR = "Error: The icon file"
    ICON_FILE_NOT_EXIST = "does not exist."

    ITEM_ICON_SIZE = 32
    ITEM_EXTRA_SIZE = 20
    ITEM_PADDING = 5

    QSPLITTER_LEFT_WIDTH = 200
    QSPLITTER_RIGHT_WIDTH = 800
    QSPLITTER_HANDLEWIDTH = 3

    PROGRESS_BAR_STYLE = """
            QProgressBar{
                border: 1px grey;
                border-radius: 5px;            
            }
    
            QProgressBar::chunk {
                background-color: lightgreen;
                width: 10px;
                margin: 1px;
            }
            """

    FILE_INDEXING = "Document Pre-processing"
    RUN_FILE_INDEXING = "Click 'Document Preprocessing' first"

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise ValueError(f"Cannot reassign constant '{name}'")
        self.__dict__[name] = value


class MODEL_CONSTANTS:
    MODEL = "model"

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise ValueError(f"Cannot reassign constant '{name}'")
        self.__dict__[name] = value


class FILE_INDEX_MESSAGE:
    THREAD_RUNNING = "Indexing File : Previous thread is still running!"
    THREAD_FINISHED = "Indexing File : Thread has been finished"
    INVALID_CREATION_TYPE = "Invalid creation type: "
    UNEXPECTED_ERROR = "An unexpected error occurred: "

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise ValueError(f"Cannot reassign constant '{name}'")
        self.__dict__[name] = value


class MODEL_MESSAGE:
    MODEL_UNSUPPORTED = "Unsupported LLM:"
    MODEL_UNSUPPORTED_TYPE = "Unsupported model type"
    THREAD_RUNNING = "Previous thread is still running!"
    THREAD_FINISHED = "LangchainWorkflowModel Thread has been finished"
    INVALID_CREATION_TYPE = "Invalid creation type: "
    UNEXPECTED_ERROR = "An unexpected error occurred: "
    AUTHENTICATION_FAILED_OPENAI = "Authentication failed. The OpenAI API key is not valid."
    AUTHENTICATION_FAILED_GEMINI = "Authentication failed. The Gemini API key is not valid."
    AUTHENTICATION_FAILED_CLAUDE = "Authentication failed. The Claude API key is not valid."

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise ValueError(f"Cannot reassign constant '{name}'")
        self.__dict__[name] = value


class DATABASE_MESSAGE:
    DATABASE_TITLE_ERROR = "Database Error"
    DATABASE_FETCH_ERROR = "Failed to fetch prompt from the database."
    DATABASE_ADD_ERROR = "Failed to add new row from the database."
    DATABASE_DELETE_ERROR = "Failed to delete row from the database."
    DATABASE_UPDATE_ERROR = "Failed to update row from the database."

    DATABASE_CHAT_CREATE_TABLE_ERROR = "Failed to create chat_main table: "
    DATABASE_CHAT_ADD_ERROR = "Failed to add chat main: "
    DATABASE_CHAT_UPDATE_ERROR = "Failed to update chat main: "
    DATABASE_CHAT_MAIN_ENTRY_SUCCESS = "Successfully deleted chat main entry with id: "
    DATABASE_CHAT_MAIN_ENTRY_FAIL = "Failed to delete chat main entry with id "

    DATABASE_CHAT_DETAIL_CREATE_TABLE_ERROR = "Failed to create chat detail table for chat_main_id "
    DATABASE_CHAT_DETAIL_INSERT_ERROR = "Failed to insert chat detail: "
    DATABASE_CHAT_DETAIL_DELETE_ERROR = "Failed to delete chat detail table "
    DATABASE_CHAT_DETAIL_FETCH_ERROR = "Failed to fetch chat details for chat_main_id"

    DATABASE_RETRIEVE_DATA_FAIL = "Failed to retrieve data from "
    DATABASE_DELETE_TABLE_SUCCESS = "Successfully deleted table: "
    DATABASE_EXECUTE_QUERY_ERROR = "Failed to execute query: "

    DATABASE_FAILED_OPEN = "Failed to open database."
    DATABASE_ENABLE_FOREIGN_KEY = "Failed to enable foreign key: "
    DATABASE_PRAGMA_FOREIGN_KEYS_ON = "PRAGMA foreign_keys = ON;"

    NEW_TITLE = "New Title"
    NEW_PROMPT = "New Prompt"


class AIProviderName(Enum):
    OPENAI = 'OpenAI'
    CLAUDE = 'Claude'
    GEMINI = 'Gemini'
    OLLAMA = 'Ollama'


class MainWidgetIndex(Enum):
    CHAT_WIDGET = auto()


def get_ai_provider_names():
    return [ai_provider.value for ai_provider in AIProviderName]
