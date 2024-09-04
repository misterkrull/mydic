from mydic_header import DB

# создаём экземпляр базы данных на основе класса
db = DB()

id = int(input("Введите id удаляемой записи: "))
db.delete(id)