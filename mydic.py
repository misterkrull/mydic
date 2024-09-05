from mydic_header import DB
import random

db = DB()

MAX_RATING = 8

number_of_words = db.count()
copy_db = db.view()

max_rand = number_of_words * MAX_RATING - 1

while True:

    while True: 
        random_number = random.randrange(0, max_rand, 1)
        index = random_number % number_of_words
        # print(random_number, index, copy_db[index][3], random_number // 8)
        if copy_db[index][3] > random_number // 8:
            break

    print("Английский       : " + str(copy_db[index][1]), end=" ")
    quit_symbol = input()
    if quit_symbol == 'q' or quit_symbol == 'й' :
        break

    print("Русский          : " + str(copy_db[index][2]))
    print("Текущий рейтинг  : " + str(copy_db[index][3]))

    a = input("Новый рейтинг    : ")
    if a != "":
        db.refresh_rating(copy_db[index][0], int(a))
    print()