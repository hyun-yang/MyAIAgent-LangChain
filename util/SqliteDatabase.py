import logging

from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel

from util.Constants import Constants, DATABASE_MESSAGE


class SqliteDatabase:
    def __init__(self, db_filename=Constants.DATABASE_NAME):
        self.initialize_vars(db_filename)
        self.initialize_db()
        logging.basicConfig(level=logging.INFO)

    def initialize_vars(self, db_filename):
        self.db_filename = db_filename
        self.db = None
        self.model = None

        # Chat
        self.chat_main_table_name = Constants.CHAT_MAIN_TABLE
        self.chat_detail_table_name = Constants.CHAT_DETAIL_TABLE

    def initialize_db(self):
        self.db = QSqlDatabase.addDatabase(Constants.SQLITE_DATABASE)
        self.db.setDatabaseName(self.db_filename)
        if not self.db.open():
            print(f"{DATABASE_MESSAGE.DATABASE_FAILED_OPEN}")
            return

        self.enable_foreign_key()
        self.create_all_tables()

    def enable_foreign_key(self):
        query = QSqlQuery(db=self.db)
        query_string = DATABASE_MESSAGE.DATABASE_PRAGMA_FOREIGN_KEYS_ON
        if not query.exec(query_string):
            print(f"{DATABASE_MESSAGE.DATABASE_ENABLE_FOREIGN_KEY} {query.lastError().text()}")

    def setup_model(self, table_name, filter=""):
        self.model = QSqlTableModel(db=self.db)
        self.model.setTable(table_name)
        self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        if filter:
            self.model.setFilter(filter)
        self.model.select()

    def create_all_tables(self):
        self.create_chat_main()

    def create_chat_main(self):
        query = QSqlQuery()
        query_string = f"""
                        CREATE TABLE IF NOT EXISTS {self.chat_main_table_name} 
                         (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                        )
                        """
        try:
            query.exec(query_string)
        except Exception as e:
            print(f"{DATABASE_MESSAGE.DATABASE_CHAT_CREATE_TABLE_ERROR} {e}")

    def add_chat_main(self, title):
        query = QSqlQuery()
        query.prepare(f"INSERT INTO {self.chat_main_table_name} (title) VALUES (:title)")
        query.bindValue(":title", title)
        try:
            if query.exec():
                chat_main_id = query.lastInsertId()
                self.create_chat_detail(chat_main_id)
                return chat_main_id
        except Exception as e:
            print(f"{DATABASE_MESSAGE.DATABASE_CHAT_ADD_ERROR} {e}")
        return None

    def update_chat_main(self, id, title):
        query = QSqlQuery()
        query.prepare(f"UPDATE {self.chat_main_table_name} SET title = :title WHERE id = :id")
        query.bindValue(":title", title)
        query.bindValue(":id", id)
        try:
            if query.exec():
                return True
        except Exception as e:
            print(f"{DATABASE_MESSAGE.DATABASE_CHAT_UPDATE_ERROR} {e}")
        return False

    def delete_chat_main_entry(self, id):
        try:
            query = QSqlQuery()
            query.prepare(f"DELETE FROM {self.chat_main_table_name} WHERE id = :id")
            query.bindValue(":id", id)
            if not query.exec():
                raise Exception(query.lastError().text())
            logging.info(f"{DATABASE_MESSAGE.DATABASE_CHAT_MAIN_ENTRY_SUCCESS} {id}")
        except Exception as e:
            logging.error(f"{DATABASE_MESSAGE.DATABASE_CHAT_MAIN_ENTRY_FAIL} {id}: {e}")
            return False
        return True

    def delete_chat_main(self, id):
        try:
            if not self.delete_chat_detail(id):
                raise Exception(f"Failed to delete chat details for id {id}")
            if not self.delete_chat_main_entry(id):
                raise Exception(f"Failed to delete chat main entry for id {id}")
        except Exception as e:
            logging.error(f"Error deleting chat main for id {id}: {e}")
            return False
        return True

    def get_all_chat_main_list(self):
        query = QSqlQuery()
        query.prepare(f"SELECT * FROM {self.chat_main_table_name} ORDER BY created_at DESC")
        try:
            if query.exec():
                results = []
                while query.next():
                    id = query.value(0)
                    title = query.value(1)
                    created_at = query.value(2)
                    results.append({'id': id, 'title': title, 'created_at': created_at})
                return results
        except Exception as e:
            print(f"{DATABASE_MESSAGE.DATABASE_RETRIEVE_DATA_FAIL} {self.chat_main_table_name}: {e}")
        return []

    def create_chat_detail(self, chat_main_id):
        query = QSqlQuery()
        chat_detail_table = f"{self.chat_detail_table_name}_{chat_main_id}"
        query_string = f"""
          CREATE TABLE IF NOT EXISTS {chat_detail_table}
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_main_id INTEGER,
                chat_type TEXT,
                chat_model TEXT,   
                chat TEXT,     
                image_data BLOB,     
                elapsed_time TEXT, 
                finish_reason TEXT,            
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(chat_main_id) REFERENCES {self.chat_main_table_name}(id) ON DELETE CASCADE 
            )
         """
        try:
            query.exec(query_string)
        except Exception as e:
            print(f"{DATABASE_MESSAGE.DATABASE_CHAT_DETAIL_CREATE_TABLE_ERROR} {chat_main_id}: {e}")

    def insert_chat_detail(self, chat_main_id, chat_type, chat_model, chat, image_data, elapsed_time, finish_reason):
        chat_detail_table = f"{self.chat_detail_table_name}_{chat_main_id}"
        query = QSqlQuery()
        query.prepare(
            f"INSERT INTO {chat_detail_table} (chat_main_id, chat_type, chat_model, chat, image_data, elapsed_time, finish_reason) "
            f" VALUES (:chat_main_id, :chat_type, :chat_model, :chat, :image_data, :elapsed_time, :finish_reason)")
        query.bindValue(":chat_main_id", chat_main_id)
        query.bindValue(":chat_type", chat_type)
        query.bindValue(":chat_model", chat_model)
        query.bindValue(":chat", chat)
        query.bindValue(":image_data", image_data)
        query.bindValue(":elapsed_time", elapsed_time)
        query.bindValue(":finish_reason", finish_reason)
        try:
            return query.exec()
        except Exception as e:
            print(f"{DATABASE_MESSAGE.DATABASE_CHAT_DETAIL_INSERT_ERROR} {e}")
            return False

    def delete_chat_detail(self, id):
        try:
            query = QSqlQuery()
            table_name = f"{self.chat_detail_table_name}_{id}"
            query.prepare(f"DROP TABLE IF EXISTS {table_name}")
            if not query.exec():
                raise Exception(query.lastError().text())
            logging.info(f"{DATABASE_MESSAGE.DATABASE_DELETE_TABLE_SUCCESS} {table_name}")
        except Exception as e:
            logging.error(f"{DATABASE_MESSAGE.DATABASE_CHAT_DETAIL_DELETE_ERROR} {id}: {e}")
            return False
        return True

    def get_all_chat_details_list(self, chat_main_id):
        chat_detail_table = f"{self.chat_detail_table_name}_{chat_main_id}"
        query = QSqlQuery()
        query.prepare(f"SELECT * FROM {chat_detail_table}")

        try:
            if not query.exec():
                print(f"{DATABASE_MESSAGE.DATABASE_CHAT_DETAIL_FETCH_ERROR} {chat_main_id}: {query.lastError().text()}")
                return []
        except Exception as e:
            print(f"{DATABASE_MESSAGE.DATABASE_EXECUTE_QUERY_ERROR} {e}")
            return []

        chat_details_list = []
        while query.next():
            chat_detail = {
                "id": query.value("id"),
                "chat_main_id": query.value("chat_main_id"),
                "chat_type": query.value("chat_type"),
                "chat_model": query.value("chat_model"),
                "chat": query.value("chat"),
                "image_data": query.value("image_data"),
                "elapsed_time": query.value("elapsed_time"),
                "finish_reason": query.value("finish_reason"),
                "created_at": query.value("created_at")
            }
            chat_details_list.append(chat_detail)

        return chat_details_list
