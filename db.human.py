import sqlite3

conn = sqlite3.connect('humandata.db')

sql_create = '''
    create table up (
        location ,
        time ,
        human ,

        )
'''
sql_insert = '''
    insert into up (location,time,human)
    values (ici,16.30,1);
'''  # ข้อมูลตัวแรก


sql_insert = '''
    insert into up (location,time,human)
    values (pky,16.33,1);
'''  # ข้อมูลตัวที่ ๒

conn.commit()  # บันทึกความเปลี่ยนแปลง

sql_select = '''
    select * from up
    '''
