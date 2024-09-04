from mydic_header import DB

db = DB()

word_en = input("Английский         : ")
word_ru = input("Русский            : ")
rating  = input("Стартовый рейтинг  : ")

db.insert(word_en, word_ru, rating) 
# print(db.view())