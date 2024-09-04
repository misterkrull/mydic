# подключаем библиотеки для работы с базой данных и с рандомом
import sqlite3 
import random

# создаём класс для работы с базой данных
class DB:                        
    # конструктор класса
    def __init__(self):           
        # соединяемся с файлом базы данных
        self.conn = sqlite3.connect("mydic.db")  
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
        # выбираем все записи о покупках
        self.cur.execute("SELECT * FROM words") 
        # собираем все найденные записи в колонку со строками
        rows = self.cur.fetchall()  
        # возвращаем сроки с записями расходов
        return rows

    # добавляем новую запись
    def insert(self, word_en, word_ru, rating):  
        # формируем запрос с добавлением новой записи в БД
        self.cur.execute("INSERT INTO words VALUES (NULL,?,?,?)", (word_en, word_ru, rating,)) 
        # сохраняем изменения
        self.conn.commit()
        

    # # обновляем информацию о покупке
    # def update(self, id, product, price):   
    #     # формируем запрос на обновление записи в БД
    #     self.cur.execute("UPDATE buy SET product=?, price=? WHERE id=?", (product, price, id,))
    #     # сохраняем изменения 
    #     self.conn.commit()

    # удаляем запись
    def delete(self, id):                   
        # формируем запрос на удаление выделенной записи по внутреннему порядковому номеру
        self.cur.execute("DELETE FROM words WHERE id=?", (id,))
        # сохраняем изменения
        self.conn.commit()

    # # ищем запись по названию покупки
    # def search(self, product="", price=""):  
    #     # формируем запрос на поиск по точному совпадению
    #     self.cur.execute("SELECT * FROM buy WHERE product=?", (product,))
    #     # формируем полученные строки и возвращаем их как ответ
    #     rows = self.cur.fetchall()
    #     return rows

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