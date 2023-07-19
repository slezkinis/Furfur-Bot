import sqlite3


class SQL():
    def __init__(self, name = 'data.db') -> None:
        conn = sqlite3.connect(name)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS students(
        discord_id INT,
        name TEXT,
        group_id INT,
        dvmn_link TEXT,
        skips INT);
        """)
        conn.commit()
        cur.execute("""CREATE TABLE IF NOT EXISTS groups(
        channel_id INT,
        days TEXT,
        start_time TEXT,
        end_time TEXT
        );
        """)
        conn.commit()
        cur.execute("""CREATE TABLE IF NOT EXISTS working_of(
        student_id INT,
        group_id INT,
        date TEXT,
        start_time TEXT,
        end_time TEXT
        );
        """)
        conn.commit()

        cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?);", (1119554223579873310, 'saturday', '12:00', '14:00'))
        conn.commit()

        cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?);", (1119556931296698539, 'saturday', '14:00', '16:00'))
        conn.commit()

        cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?);", (1119557155801026622, 'monday, thursday', '11:00', '12:00'))
        conn.commit()

        cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?);", (1119557293596479559, 'monday, wednesday', '17:00', '18:00'))
        conn.commit()

        cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?);", (1119557472559042620, 'monday, wednesday', '18:00', '19:00'))
        conn.commit()

        cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?);", (1119557596907577404, 'monday, wednesday', '19:00', '20:00'))
        conn.commit()

        cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?);", (1119557679505997944, 'tuesday, thursday', '18:00', '19:00'))
        conn.commit()

        cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?);", (1119557752419794964, 'tuesday, thursday', '19:00', '20:00'))
        conn.commit()

        cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?);", (1119557849857667202, 'wednesday, friday', '16:00', '17:00'))
        conn.commit()
        conn.close()