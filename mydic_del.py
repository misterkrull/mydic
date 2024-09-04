from mydic_header import DB

db = DB()

id = int(input("Введите id удаляемой записи: "))

db.delete(id)