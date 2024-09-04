from mydic_header import DB
import random

# создаём экземпляр базы данных на основе класса
db = DB()

number_of_words = db.count()

while True:
    random_number = random.randrange(0, number_of_words * 8 - 1, 1)
    # print(random_number, random_number % number_of_words + 1, db.get_rating(random_number % number_of_words + 1), random_number // 8)

    while db.get_rating(random_number % number_of_words + 1) <= random_number // 8:
        random_number = random.randrange(0, number_of_words * 8 - 1, 1)
        # print(random_number, random_number % number_of_words + 1, db.get_rating(random_number % number_of_words + 1), random_number // 8)

    if input("Английский       : " + str(db.get_word_en(random_number % number_of_words + 1)) + ' ') == 'q':
        exit()

    print("Русский          :", db.get_word_ru(random_number % number_of_words + 1))
    print("Текущий рейтинг  :", db.get_rating(random_number % number_of_words + 1))

    a = input("Новый рейтинг    : ")
    if a != "":
        db.refresh_rating(random_number % number_of_words + 1, int(a))
    print()
    
