# подключаем библиотеку для работы с базой данных
import sqlite3
import os

MY_PATH = "G:\\codes\\vscode\\mydic"

# создаём класс для работы с базой данных
class DB:                        
    # конструктор класса
    def __init__(self):           
        # соединяемся с файлом базы данных
        self.conn = sqlite3.connect(os.path.join(MY_PATH, "mydic.db")) 
        # создаём курсор для виртуального управления базой данных
        self.cur = self.conn.cursor()    
        # если нужной нам таблицы в базе нет — создаём её
        self.cur.execute(             
            "CREATE TABLE IF NOT EXISTS words (id INTEGER PRIMARY KEY, word_en TEXT, word_ru TEXT, rating INTEGER)") 
        # сохраняем сделанные изменения в базе
        self.conn.commit()  

    # деструктор класса
    def __del__(self):        
        # отключаемся от базы при завершении работы
        self.conn.close()   
   
    # просмотр всех записей
    def view(self):        
        # выбираем все записи
        self.cur.execute("SELECT * FROM words") 
        # собираем все найденные записи в колонку со строками
        rows = self.cur.fetchall()
        # возвращаем строки с записями
        return rows

    # добавляем новую запись
    def insert(self, word_en, word_ru, rating):  
        # формируем запрос с добавлением новой записи в БД
        self.cur.execute("INSERT INTO words VALUES (NULL,?,?,?)", (word_en, word_ru, rating,)) 
        # сохраняем изменения
        self.conn.commit()
        
    # # обновляем информацию
    # def update(self, id, word_en, word_ru, rating):   
    #     # формируем запрос на обновление записи в БД
    #     self.cur.execute("UPDATE words SET word_en=?, word_ru=?, rating=? WHERE id=?", (word_en, word_ru, rating, id,))
    #     # сохраняем изменения 
    #     self.conn.commit()

    # удаляем запись по id
    def delete_by_id(self, id):                   
        # формируем запрос на удаление выделенной записи по внутреннему порядковому номеру
        self.cur.execute("DELETE FROM words WHERE id=?", (id,))
        # сохраняем изменения
        self.conn.commit()

    # удаляем запись по word_en
    def delete_by_word_en(self, word_en):                   
        # формируем запрос на удаление выделенной записи по внутреннему порядковому номеру
        self.cur.execute("DELETE FROM words WHERE word_en=?", (word_en,))
        # сохраняем изменения
        self.conn.commit()

    # ищем запись по id
    def search_by_id(self, id=0):  
        # формируем запрос на поиск по точному совпадению
        self.cur.execute("SELECT * FROM words WHERE id=?", (id,))
        # формируем полученные строки и возвращаем их как ответ
        rows = self.cur.fetchall()
        return rows
    
    # ищем запись по word_en
    def search_by_word_en(self, word_en=""):  
        # формируем запрос на поиск по точному совпадению
        self.cur.execute("SELECT * FROM words WHERE word_en=?", (word_en,))
        # формируем полученные строки и возвращаем их как ответ
        rows = self.cur.fetchall()
        return rows

    def count(self):
        self.cur.execute('SELECT COUNT(*) FROM words')
        return self.cur.fetchone()[0]
    
    def get_word_en(self, id):
        self.cur.execute("SELECT word_en FROM words WHERE id=?", (id,))
        [(temp_word_en,)] = self.cur.fetchall()
        return temp_word_en   
    
    def get_word_ru(self, id):
        self.cur.execute("SELECT word_ru FROM words WHERE id=?", (id,))
        [(temp_word_ru,)] = self.cur.fetchall()
        return temp_word_ru
    
    def get_rating(self, id):
        self.cur.execute("SELECT rating FROM words WHERE id=?", (id,))
        [(temp_rating,)] = self.cur.fetchall()
        return temp_rating
    
    def refresh_rating(self, id, new_rat):
        self.cur.execute("UPDATE words SET rating=? WHERE id=?", (int(new_rat), id,))
        self.conn.commit()