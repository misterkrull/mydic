import argparse
import os
import random
import subprocess
from db import DB, MAX_RATING
from typing import Any


CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
DICTIONARIES_FOLDER = "dictionaries"
DICTIONARIES_FOLDER_PATH = os.path.join(CURRENT_FOLDER, DICTIONARIES_FOLDER)
CURRENT_DICTIONARY_FILE = os.path.join(DICTIONARIES_FOLDER, "_current_dictionary.txt")
CURRENT_DICTIONARY_FILE_PATH = os.path.join(CURRENT_FOLDER, CURRENT_DICTIONARY_FILE)


DESCRIPTION_HEAD = """\
Программа mydic
Автор - Ярослав Круль, 2024

Данная программа представляет собой словарь, содержащий английские и русские слова,
а также их рейтинг от 0 до {max_rating}.

Программа выдаёт случайное английское слово и предлагает пользователю вспомнить его перевод.
Если нажать клавишу Enter, то программа покажет перевод этого слова,
а также отобразит текущий рейтинг словарной пары и предложит его обновить.
Можно указать новый рейтинг и нажать Enter или ничего не вводить и нажать Enter
(в последнем случае рейтинг останется прежним).
После этого программа покажет новое случайное английское слово - и всё повторится сначала.
Чтобы выйти из программы, нужно в строке с английским словом набрать символ 'q' или 'й'
и нажать Enter.

Рейтинг влияет на частоту отображения слова: если рейтинг равен {max_rating}, то вероятность выпадения
данного слова наивысшая, а при рейтинге 0 слово не выпадает никогда.\
"""

DESCRIPTION_ADD_COMMAND = ("Добавить новое слово в словарь\n"
                           "    Формат: mydic add английское_слово русское_слово стартовый_рейтинг")

DESCRIPTION_COUNT_COMMAND = ("Узнать текущее количество слов в словаре")

DESCRIPTION_DEL_COMMAND = ("Удалить слово из словаря (по id в базе данных или по английскому слову)\n"
                           "    Формат: mydic del (id | английское_слово)")

DESCRIPTION_DICT_COMMAND = ("Сменить словарь\n"
                            "    Формат: mydic dict имя_словаря\n"
                            "    Также доступны следующие команды:\n"
                            "        mydic dict current      Вывести название текущего словаря\n"
                            "        mydic dict list         Вывести список имеющихся словарей\n"
                            "        mydic dict open         Открыть папку со словарями в Проводнике")


# если пользователь введёт: mydic add чтототам
def add_command(args: argparse.Namespace, db: DB) -> None:
    word_en, word_ru, rating = args.word_en, args.word_ru, args.rating
    if 0 <= rating <= MAX_RATING:
        db.insert(word_en, word_ru, rating)
        print(f'Словарная пара "{word_en}" - "{word_ru}" со стартовым рейтингом {rating} успешно добавлена!')
    else:
        print(f"Некорректные данные: рейтинг должен быть от 0 до {MAX_RATING}")


def count_command(copy_db: list[Any], MAX_RATING: int, RATING_TO_WEIGHT: dict, current_dictionary: str) -> None:
    rating_counts = [0] * (MAX_RATING + 1)
    try:
        for el in copy_db:
            rating_counts[el[3]] += 1
    except:
        print("Невозможно подсчитать количество слов по каждому рейтингу"
              "Судя по всему, в базе данных словаря некорректные значения рейтинга")
        
    print(f"Имя текущего словаря:        {current_dictionary}")
    print(f"Количество слов в словаре:   {len(copy_db)}")
    
    total_weight = sum(rating_counts[i] * RATING_TO_WEIGHT[i] for i in range(MAX_RATING + 1))
    print(f"Суммарный вес всех слов:     {total_weight}")
    print()
    print(" Рейтинг    Вес одного     Количество      Шанс выпадения     Шанс выпадения слова")
    print("               слова          слов          одного слова       с данным рейтингом")
    
    digits_rating = len(str(MAX_RATING))
    digits_rating_to_weight = len(str(max(RATING_TO_WEIGHT.values())))
    digits_rating_counts = len(str(max(rating_counts)))
    for i in range(MAX_RATING + 1):
        print(' ' * max(4 - digits_rating // 2, 0) + f"{i:{digits_rating}d}" + \
                ' ' * max(6 - (digits_rating - 1) // 2, 0), end='')
        print(' ' * max(6 - digits_rating_to_weight // 2, 0) + f"{RATING_TO_WEIGHT[i]:{digits_rating_to_weight}d}" + \
                ' ' * max(8 - (digits_rating_to_weight - 1) // 2, 0), end='')
        print(' ' * max(6 - digits_rating_counts // 2, 0) + f"{rating_counts[i]:{digits_rating_counts}d}" + \
                ' ' * max(8 - (digits_rating_counts - 1) // 2, 0), end='')
        print(f"{(RATING_TO_WEIGHT[i] / total_weight * 100):13.8f} %", end='')
        print(f"{(RATING_TO_WEIGHT[i] / total_weight * 100 * rating_counts[i]):20.8f} %")
        


# если пользователь введёт: mydic del чтототам
def del_command(args: argparse.Namespace, db: DB) -> None:
    try:
        id_or_word_en = int(args.id_or_word_en)
        del_mode_by = "id"
        found_entries = db.search_by_id(id_or_word_en)
    except ValueError:
        id_or_word_en = args.id_or_word_en
        del_mode_by = "word_en"
        found_entries = db.search_by_word_en(id_or_word_en)
    
    if not found_entries:
        print(f"Не найдено ни одной записи с {del_mode_by}={id_or_word_en}")
        return
    print(f"Найдены следующие записи с {del_mode_by}={id_or_word_en}:")
    for entry in found_entries:
        print(f"id={entry[0]}   {entry[1]}   {entry[2]}   rating={entry[3]}")
    ans = input("Удалить? (Y/y/Д/д - да, любые другие символы - нет) ")
    if ans in {'Y', 'y', 'Д', 'д'}:
        if del_mode_by == "id":
            db.delete_by_id(id_or_word_en)
        else:
            db.delete_by_word_en(id_or_word_en)
        print("Удалено!")


def dict_command(args: argparse.Namespace, db: DB, current_dictionary: str) -> None:

    if args.dictionary_name == "list":
        files = os.listdir(DICTIONARIES_FOLDER_PATH)
        db_files = [os.path.splitext(f)[0] for f in files if f.endswith('.db')]

        print("Список имеющихся словарей:")
        print(*db_files, sep='\n')
        return
    
    if args.dictionary_name == "open":
        try:
            # Открываем Проводник Windows с указанным путем
            subprocess.Popen(['explorer', DICTIONARIES_FOLDER_PATH])
            print(f"Папка со словарями открылась в Проводнике")
        except Exception as e:
            print(f"Ошибка при открытии Проводника: {e}")
        return
    
    if args.dictionary_name == "current":
        print(f"Текущий словарь: {current_dictionary}")
        return
    
    try:
        with open(CURRENT_DICTIONARY_FILE_PATH, 'w') as cur_dict_file:
            cur_dict_file.write(args.dictionary_name)
        print("Словарь успешно сменён!")
        print(f"Текущий словарь: {args.dictionary_name}")
    except OSError as e:
        print(f"Ошибка при открытии файла, хранящего имя текущего словаря: {e}")


# основной алгоритм программы
def choice_algorhytm(max_rand: int,
                     number_of_words: int,
                     RATING_TO_WEIGHT: dict,
                     copy_db: list[Any],
                     rating_from: int,
                     rating_to: int,
                     single_pass_flags: list[bool]
                    ) -> int:
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
        random_number = random.randrange(0, max_rand)  # выбираем случайную ячейку таблицы
        index = random_number % number_of_words  # вычисляем номер столбца от 0 до number_of_words-1
        # далее сравниваем вес слова (от 0 до MAX_WEIGHT) 
        #                        с номером строки текущей ячейки (от 0 до MAX_RATING-1)
        # тем самым мы определяем, стоит ли в ячейке 0 или x
        if RATING_TO_WEIGHT[copy_db[index][3]] > random_number // number_of_words:	
            # если условие выполняется, то значит в текущей ячейке стоит x
            # а это значит - мы победили и нашли слово
            # остаётся проверить, что рейтинг найденного слова попадает в заданные границы,
            # а также что слово непройдено (для режима '--once')
            #   (да, не самый оптимальный алгоритм, но пока так)
            if (rating_from <= copy_db[index][3] <= rating_to) and not single_pass_flags[index]:
                return index
            # (в частности, если рейтинг слова ноль, то всегда будет перезапуск
            #  а если рейтинг равен MAX_RATING, то всегда будет "мы победили"
            #  что и требуется)
        # а если условие не проходит, то в ячейке 0 и мы "перебрасываем кости" 


# если пользователь введёт просто mydic (основной режим программы)
def learning(MAX_WEIGHT: int, 
             number_of_words: int, 
             RATING_TO_WEIGHT: int,
             db: DB,
             copy_db: list[Any],
             rating_from: int,
             rating_to: int,
             tw: bool,
             once: bool
            ) -> None:
            
    if number_of_words == 0:
        print("Ваш словарь пуст!\n"
              "Попробуйте заполнить его несколькими словами с помощью команды:\n"
              "    mydic add английское_слово русское_слово стартовый_рейтинг")
        return
        
    if not (0 <= rating_from <= MAX_RATING):
        print(f"Ошибка: значение минимального рейтинга должно быть в диапазоне от 0 до {MAX_RATING}")
        return
    if not (0 <= rating_to <= MAX_RATING):
        print(f"Ошибка: значение максимального рейтинга должно быть в диапазоне от 0 до {MAX_RATING}")
        return
    if not rating_from <= rating_to:
        print("Ошибка: значение минимального рейтинга не должно превышать максимальное")
        return    
    
    amount_of_words = 0
    for el in copy_db:
        if rating_from <= el[3] <= rating_to:
            amount_of_words += 1
    if amount_of_words > 0:
        print(f"Вы запустили режим тренировки{' в однократном режиме' if once else ''}!")
        print("Количество слов в текущей тренировке:", amount_of_words)
        print()
    else:
        print("Нет ни одного слова в указанном диапазоне рейтинга!")
        return
    
    max_rand = number_of_words * MAX_WEIGHT
    single_pass_flags = [False] * len(copy_db)  # нужен для режима однократного прохождения
    count = 0  # счётчик повторов, выведем в конце
    while amount_of_words:  # если не включен однократный режим (и в нашей выборке есть слова)
                            # то amount_of_words не будет меняться и тут по факту бесконечный цикл
        index = choice_algorhytm(max_rand, number_of_words, RATING_TO_WEIGHT, copy_db,
                                 rating_from, rating_to, single_pass_flags)
        if once:
            single_pass_flags[index] = True
            amount_of_words -= 1
        eng_to_rus = bool(random.randrange(2)) if tw else True            
        
        if eng_to_rus:
            print("Английский       : " + str(copy_db[index][1]), end=" ")
        else:
            print("Русский          : " + str(copy_db[index][2]), end=" ")
        
        quit_symbol = input()
        if quit_symbol in {'q', 'й'}:
            print("Количество повторённых слов:", count)
            break
        count += 1

        if eng_to_rus:
            print("Русский          : " + str(copy_db[index][2]))  
        else:
            print("Английский       : " + str(copy_db[index][1]))
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
        
        if once and amount_of_words % 5 == 0:  # в однократном режиме каждые 5 слов пишем количество оставшихся
            print("Осталось слов: ", amount_of_words)
        print()


def main():    
    try:
        with open(CURRENT_DICTIONARY_FILE_PATH, 'r') as cur_dict_file:
            current_dictionary = cur_dict_file.readline().strip()
    except FileNotFoundError:
        print("Ошибка: не найден файл, хранящий имя текущего словаря.")
        return
    except OSError:
        print("Ошибка: общая ошибка ввода-вывода при открытии файла, хранящего имя текущего словаря.")
        return
    except:
        print("Ошибка: незвестная ошибка, связанная с открытием файла, хранящего имя текущего словаря.")
        return
    
    db_path = os.path.join(CURRENT_FOLDER, DICTIONARIES_FOLDER, current_dictionary + '.db')
    
    try:
        db = DB(db_path, current_dictionary)
    except Exception:
        return
    
    number_of_words = db.count()
    copy_db = db.view()

    RATING_TO_WEIGHT = db.rating_to_weight()
    MAX_WEIGHT = RATING_TO_WEIGHT[MAX_RATING]

    parser = argparse.ArgumentParser(
        description=DESCRIPTION_HEAD.format(max_rating=MAX_RATING),
        formatter_class=argparse.RawTextHelpFormatter  # без этого поля будут игнорироваться символы \n
    )
    parser.add_argument('--from', '-f', type=int, dest='rating_from', default=0, help='Минимальный рейтинг')
    parser.add_argument('--once', '-o', action='store_true', help='Режим однократного прохождения')
    parser.add_argument('--to', '-t', type=int, dest='rating_to', default=MAX_RATING, help='Максимальный рейтинг')
    parser.add_argument('-tw', '--tw', '--two-way', action='store_true', help='Тренировка перевода в обе стороны')
        
    subparsers = parser.add_subparsers(dest='command')

    parser_add = subparsers.add_parser('add', help=DESCRIPTION_ADD_COMMAND)
    parser_add.add_argument('word_en', type=str)
    parser_add.add_argument('word_ru', type=str)
    parser_add.add_argument('rating', type=int)

    parser_count = subparsers.add_parser('count', help=DESCRIPTION_COUNT_COMMAND)

    parser_del = subparsers.add_parser('del', help=DESCRIPTION_DEL_COMMAND)
    parser_del.add_argument('id_or_word_en')

    parser_dict = subparsers.add_parser('dict', help=DESCRIPTION_DICT_COMMAND)
    parser_dict.add_argument('dictionary_name', type=str)

    args = parser.parse_args()

    if args.command == 'add':
        add_command(args, db)
    elif args.command == 'count':
        count_command(copy_db, MAX_RATING, RATING_TO_WEIGHT, current_dictionary)
    elif args.command == 'del':
        del_command(args, db)
    elif args.command == 'dict':
        dict_command(args, db, current_dictionary)
    else:
        learning(MAX_WEIGHT, number_of_words, RATING_TO_WEIGHT, db, copy_db,
            args.rating_from, args.rating_to, args.tw, args.once)


if __name__ == "__main__":
    main()