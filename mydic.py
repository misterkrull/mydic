from mydic_header import DB
import random

db = DB()

MAX_RATING = 8

number_of_words = db.count()
copy_db = db.view()

max_rand = number_of_words * MAX_RATING

while True:

    # алгоритм выбора случайного слова с соответствующим рейтингу весом (плотностью вероятности)
    # алгоритм работает так: 
    #   нарисуем таблицу с MAX_RATING строками и number_of_words столбцами:
    # 
    #       0 0 0 0 0 x x 0 x 0 0 0 0 ...  MAX_RATING-1 строка
    #       0 0 x 0 0 x x x x 0 x 0 0 ...  ...
    #       x 0 x 0 0 x x x x x x 0 0 ...  2 строка
    #       x x x 0 0 x x x x x x 0 x ...  1 строка
    #       x x x x 0 x x x x x x 0 x ...  0 строка
    # 
    #       3 2 4 1 0 5 5 4 5 3 4 0 2 ...  вес каждого слова (от 0 до MAX_RATING включительно)
    #   
    #   Для реализации случайного выбора слова с заданным весом нужно реализовать равновероятный
    #       выбор из всех отмеченных в таблице x-ов. Можно решить задачу точно, но можно пойти проще:
    #       1. Берём случайную клетку из той таблице и смотрим, чё там
    #       2. Если там 0, то возвращаемся к пункту 1,
    #          а если там x, то выдаём соответствующее слово
    while True:     
        random_number = random.randrange(0, max_rand)	# нумерация ячеек таблицы от 0 до max_rand-1
        index = random_number % number_of_words			# номер столбца (слова) от 0 до number_of_words-1
		# далее сравниваем рейтинг слова (от 0 до MAX_RATING) с номером текущей строки (от 0 до MAX_RATING-1):
        if copy_db[index][3] > random_number // number_of_words:	
            break
            # условие проходит и цикл останавливается (мы победили и нашли слово), если первое больше второго :)
            # в частности, если рейтинг слова ноль, то всегда будет перезапуск
            # а если рейтинг равен MAX_RATING, то всегда будет "мы победили"
            # что и требуется

    print("Английский       : " + str(copy_db[index][1]), end=" ")

    quit_symbol = input()
    if quit_symbol == 'q' or quit_symbol == 'й' :
        break

    print("Русский          : " + str(copy_db[index][2]))
    print("Текущий рейтинг  : " + str(copy_db[index][3]))

    a = input("Новый рейтинг    : ")
    if a != "":
        db.refresh_rating(copy_db[index][0], int(a))
        copy_db[index] = (copy_db[index][0], copy_db[index][1], copy_db[index][2], int(a))

    print()