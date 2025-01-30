import os
import sqlite3
from typing import Any

# важная системная переменная всей программы: максимально возможный рейтинг
# объявляется в этом файле, т.к. здесь в методе __init__() она нужна
MAX_RATING = 9

class DB:
    def __init__(self, db_path: str, current_dictionary: str):
        # соединяемся с файлом базы данных
        
        if not os.path.exists(db_path):
            print(
                f"Ошибка: файл словаря '{current_dictionary}' не найден.\n"
                f"Файл словаря искался по адресу: {db_path}"
            )
            self.is_connected = False
            raise Exception
        try:
            self.conn = sqlite3.connect(db_path)
            self.cur = self.conn.cursor()
            self.cur.execute("PRAGMA schema_version;")  # проверяем корректность БД
        except sqlite3.Error as e:
            print(
                f"Ошибка при открытии базы данных словаря: {e}\n"
                f"Имя словаря: {current_dictionary}\n"
                f"Адрес файла базы данных словаря: {db_path}"
            )
            self.is_connected = False
            raise Exception
        
        self.is_connected = True
        # если нужной нам таблицы в базе нет — создаём её
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS words "
            "(id INTEGER PRIMARY KEY, word_en TEXT, word_ru TEXT, rating INTEGER)"
        )
        
        # делаем запрос на существование таблицы rating_to_weight
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rating_to_weight'")
        # если таблицы rating_to_weight не существует, то создаём её, заполняя значениями по умолчанию
        if not self.cur.fetchone():
            self.cur.execute("CREATE TABLE rating_to_weight (rating INTEGER PRIMARY KEY, weight INTEGER)")
            self.cur.executemany(
                "INSERT INTO rating_to_weight (rating, weight) VALUES (?, ?)",
                [(i, i) for i in range(MAX_RATING+1)]
            )

        # сохраняем сделанные изменения в базе
        self.conn.commit()

    def __del__(self):
        if self.is_connected:
            self.conn.close()
   
    # просмотр всех записей  (в таблице words)
    def view(self) -> list[Any]:
        # выбираем все записи
        self.cur.execute("SELECT * FROM words")
        # собираем все найденные записи в колонку со строками
        rows = self.cur.fetchall()
        # возвращаем строки с записями
        return rows

    # добавляем новую запись  (в таблицу words)
    def insert(self, word_en: str, word_ru: str, rating: int) -> None:
        # формируем запрос с добавлением новой записи в БД
        self.cur.execute("INSERT INTO words VALUES (NULL,?,?,?)", (word_en, word_ru, rating,))
        # сохраняем изменения
        self.conn.commit()
        
    # # обновляем информацию  (в таблице words)
    # def update(self, id, word_en, word_ru, rating) -> None:
    #     # формируем запрос на обновление записи в БД
    #     self.cur.execute("UPDATE words SET word_en=?, word_ru=?, rating=? WHERE id=?", (word_en, word_ru, rating, id,))
    #     # сохраняем изменения
    #     self.conn.commit()

    # удаляем запись по id  (в таблице words)
    def delete_by_id(self, id: int) -> None:
        # формируем запрос на удаление выделенной записи по внутреннему порядковому номеру
        self.cur.execute("DELETE FROM words WHERE id=?", (id,))
        # сохраняем изменения
        self.conn.commit()

    # удаляем запись по word_en  (в таблице words)
    def delete_by_word_en(self, word_en: str) -> None:
        # формируем запрос на удаление выделенной записи по внутреннему порядковому номеру
        self.cur.execute("DELETE FROM words WHERE word_en=?", (word_en,))
        # сохраняем изменения
        self.conn.commit()

    # ищем запись по id  (в таблице words)
    def search_by_id(self, id: int) -> list[Any]:
        # формируем запрос на поиск по точному совпадению
        self.cur.execute("SELECT * FROM words WHERE id=?", (id,))
        # формируем полученные строки и возвращаем их как ответ
        rows = self.cur.fetchall()
        return rows
    
    # ищем запись по word_en  (в таблице words)
    def search_by_word_en(self, word_en: str) -> list[Any]:
        # формируем запрос на поиск по точному совпадению
        self.cur.execute("SELECT * FROM words WHERE word_en=?", (word_en,))
        # формируем полученные строки и возвращаем их как ответ
        rows = self.cur.fetchall()
        return rows

    # считаем количество слов в таблице words
    def count(self) -> int:
        self.cur.execute('SELECT COUNT(*) FROM words')
        return self.cur.fetchone()[0]
    
    # получаем word_en по id  (в таблице words)
    def get_word_en(self, id: int) -> str:
        self.cur.execute("SELECT word_en FROM words WHERE id=?", (id,))
        [(temp_word_en,)] = self.cur.fetchall()
        return str(temp_word_en)
    
    # получаем word_ru по id  (в таблице words)
    def get_word_ru(self, id: int) -> str:
        self.cur.execute("SELECT word_ru FROM words WHERE id=?", (id,))
        [(temp_word_ru,)] = self.cur.fetchall()
        return str(temp_word_ru)
    
    # получаем rating по id  (в таблице words)
    def get_rating(self, id: int) -> int:
        self.cur.execute("SELECT rating FROM words WHERE id=?", (id,))
        [(temp_rating,)] = self.cur.fetchall()
        return int(temp_rating)
    
    # обновляем рейтинг по id  (в таблице words)
    def refresh_rating(self, id: int, new_rating: int) -> None:
        self.cur.execute("UPDATE words SET rating=? WHERE id=?", (int(new_rating), id,))
        self.conn.commit()

    # экспортируем всю таблицу rating_to_weight в виде словаря
    def rating_to_weight(self) -> dict:
        self.cur.execute("SELECT * FROM rating_to_weight") 
        all_entries = self.cur.fetchall()
        ans = {}
        for entry in all_entries:
            ans[int(entry[0])] = int(entry[1])
        return ans