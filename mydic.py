from db import DB, MAX_RATING
import random
import argparse


def main():

    db = DB()
    number_of_words = db.count()
    copy_db = db.view()

    RATING_TO_WEIGHT = db.rating_to_weight()
    MAX_WEIGHT = RATING_TO_WEIGHT[MAX_RATING]

    parser = argparse.ArgumentParser(
            description=
                    "Программа mydic\n"
                    "Автор - Ярослав Круль, 2024\n"
                    "\n"
                    "Данная программа представляет собой словарь, содержащий английские и русские слова,\n"
                    f"а также их рейтинг от 0 до {MAX_RATING}.\n"
                    "\n"
                    "Программа выдаёт случайное английское слово и предлагает пользователю вспомнить его перевод.\n"
                    "Если нажать клавишу Enter, то программа покажет перевод этого слова,\n"
                    "а также отобразит текущий рейтинг словарной пары и предложит его обновить.\n"
                    "Можно указать новый рейтинг и нажать Enter или ничего не вводить и нажать Enter\n"
                    "(в последнем случае рейтинг останется прежним).\n"
                    "После этого программа покажет новое случайное английское слово - и всё повторится сначала.\n"
                    "Чтобы выйти из программы, нужно в строке с английским словом набрать символ 'q' или 'й'\n"
                    "и нажать Enter.\n"
                    "\n"
                    f"Рейтинг влияет на частоту отображения слова: если рейтинг равен {MAX_RATING}, то вероятность выпадения\n"
                    "данного слова наивысшая, а при рейтинге 0 слово не выпадает никогда.",
            formatter_class=argparse.RawTextHelpFormatter) # без этого поля будут игнорироваться символы \n
    
    subparsers = parser.add_subparsers(dest='command')

    parser_add = subparsers.add_parser(
                'add', 
                help="Добавить новое слово в словарь\n"
                      "    Формат: mydic add английское_слово русское_слово стартовый_рейтинг")
    parser_add.add_argument('word_en', type=str)
    parser_add.add_argument('word_ru', type=str)
    parser_add.add_argument('rating', type=int)
    
    parser_del = subparsers.add_parser(
                'del', help="Удалить слово из словаря (по id в базе данных или по английскому слову)\n"
                             "    Формат: mydic del (id | английское_слово)")
    parser_del.add_argument('id_or_word_en')
    
    args = parser.parse_args()

    if args.command == 'add':
        word_en, word_ru, rating = args.word_en, args.word_ru, args.rating
        if 0 <= rating <= MAX_RATING:
            db.insert(word_en, word_ru, rating)
            print(f'Словарная пара "{word_en}" - "{word_ru}" со стартовым рейтингом {rating} '
                            'успешно добавлена!')
        else:
            print(f"Некорректные данные: рейтинг должен быть от 0 до {MAX_RATING}")
            
    elif args.command == 'del':
        try:
            id_or_word_en = int(args.id_or_word_en)
            choice = "id"
            found_entries = db.search_by_id(id_or_word_en)
        except ValueError:
            id_or_word_en = args.id_or_word_en
            choice = "word_en"
            found_entries = db.search_by_word_en(id_or_word_en)
        
        if not found_entries:
            print(f"Не найдено ни одной записи с {choice}={id_or_word_en}")
        else:
            print(f"Найдены следующие записи с {choice}={id_or_word_en}:")
            for entry in found_entries:
                print(f"id={entry[0]}   {entry[1]}   {entry[2]}   rating={entry[3]}")
            ans = input("Удалить? (Y/y/Д/д - да, любые другие символы - нет) ")
            if ans in {'Y', 'y', 'Д', 'д'}:
                if choice == "id":
                    db.delete_by_id(id_or_word_en)
                else:
                    db.delete_by_word_en(id_or_word_en)
                print("Удалено!")

    else:
        if number_of_words == 0:
            print("Ваш словарь пуст!\n"
                  "Попробуйте заполнить его несколькими словами с помощью команды:\n"
                  "    mydic add английское_слово русское_слово стартовый_рейтинг")
        else:
            max_rand = number_of_words * MAX_WEIGHT
            while True:

                # алгоритм выбора случайного слова с соответствующим рейтингу весом (плотностью вероятности)
                # алгоритм весьма забавный, постараюсь сейчас объяснить его работу
                # 
                # для иллюстрации алгоритма нарисуем таблицу с MAX_WEIGHT строками и number_of_words столбцами
                #   (в данном примере MAX_WEIGHT=5, это не суть важно)
                # тогда всего в таблице max_rand ячеек (max_rand = number_of_words * MAX_WEIGHT)
                # каждый столбец соответствует какому-то слову
                # в каждой ячейке один из двух символов: 0 или x
                # количество x в столбце равно весу данного слова
                # все x-ы прижаты к верхнему краю
                #
                #       x x x x 0 x x x x x x 0 x ...   0 строка
                #       x x x 0 0 x x x x x x 0 x ...   1 строка
                #       x 0 x 0 0 x x x x x x 0 0 ...   2 строка
                #       0 0 x 0 0 x x x x 0 x 0 0 ...   3 строка
                #       0 0 0 0 0 x x 0 x 0 0 0 0 ...   MAX_WEIGHT-1=4 строка
                # 
                #       3 2 4 1 0 5 5 4 5 3 4 0 2 ...   вес каждого слова (от 0 до MAX_WEIGHT включительно)
                #   
                #   Для реализации случайного выбора слова с заданным весом нужно реализовать равновероятный
                #       выбор из всех отмеченных в таблице x-ов. Можно решить задачу точно, но можно пойти проще:
                #       1. Берём случайную клетку из той таблицы и смотрим, чё там
                #       2. Если там 0, то возвращаемся к пункту 1,
                #          а если там x, то выдаём соответствующее слово
                #
                #   Нумерацию ячеек в таблице выберем следующим образом:
                #       от 0                до   number_of_words-1          0 строка
                #       от number_of_words  до 2*number_of_words-1          1 строка
                #            и т.д.
                while True:     
                    random_number = random.randrange(0, max_rand)	# выбираем случайную ячейку таблицы
                    index = random_number % number_of_words			# вычисляем номер столбца (слова) от 0 до number_of_words-1
                    # далее сравниваем вес слова (от 0 до MAX_WEIGHT) 
                    #                        с номером строки текущей ячейки (от 0 до MAX_RATING-1)
                    # тем самым мы определяем, стоит ли в ячейке 0 или x
                    if RATING_TO_WEIGHT[copy_db[index][3]] > random_number // number_of_words:	
                        # если условие выполняется, то значит в текущей ячейке стоит x
                        # а это значит - мы победили и нашли слово
                        break
                        # (в частности, если рейтинг слова ноль, то всегда будет перезапуск
                        #  а если рейтинг равен MAX_RATING, то всегда будет "мы победили"
                        #  что и требуется)
                    # а если условие не проходит, то в ячейке 0 и мы "перебрасываем кости" 

                print("Английский       : " + str(copy_db[index][1]), end=" ")

                quit_symbol = input()
                if quit_symbol in {'q', 'й'}:
                    break

                print("Русский          : " + str(copy_db[index][2]))
                print("Текущий рейтинг  : " + str(copy_db[index][3]))

                while True:
                    new_rating_str = input("Новый рейтинг    : ")
                    if new_rating_str == "":
                        break
                    try:
                        new_rating = int(new_rating_str)
                        if 0 <= new_rating <= MAX_RATING:
                            db.refresh_rating(copy_db[index][0], new_rating)
                            copy_db[index] = (copy_db[index][0], copy_db[index][1], copy_db[index][2], new_rating)
                            break
                        print(f"Рейтинг должен быть числом от 0 до {MAX_RATING}! Попробуйте снова!")
                    except ValueError:
                        print("Рейтинг должен быть числом, а вы ввели не число! Попробуйте снова!")

                print()


if __name__ == "__main__":
    main()