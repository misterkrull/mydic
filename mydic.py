from mydic_header import DB
import random

db = DB()

MAX_RATING = 8

number_of_words = db.count()
max_rand = number_of_words * MAX_RATING - 1

while True:

    while True: 
        random_number = random.randrange(0, max_rand, 1)
        id = random_number % number_of_words + 1
        # print(random_number, id, db.get_rating(id), random_number // 8)
        if db.get_rating(id) > random_number // 8:
            break

    print("Английский       : " + str(db.get_word_en(id)), end=" ")
    if input() == 'q':
        break

    print("Русский          : " + str(db.get_word_ru(id)))
    print("Текущий рейтинг  : " + str(db.get_rating(id)))

    a = input("Новый рейтинг    : ")
    if a != "":
        db.refresh_rating(id, int(a))
    print()