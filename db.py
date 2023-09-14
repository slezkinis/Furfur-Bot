
import sqlite3


class SQL():
    def __init__(self) -> None:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS students(
        discord_id INT,
        name TEXT,
        role_id INT,
        dvmn_link TEXT,
        skips INT);
        """)
        conn.commit()
        cur.execute("""CREATE TABLE IF NOT EXISTS groups(
        role_id INT,
        days TEXT,
        start_time TEXT,
        end_time TEXT,
        voice_chat_id INT,
        text_chat_id INT
        );
        """)
        conn.commit()
        cur.execute("""CREATE TABLE IF NOT EXISTS working_of(
        id INT PRIMARY KEY,
        student_id INT,
        role_id INT,
        start_time TEXT,
        end_time TEXT,
        student_visit BOOL,
        voice_id INT
        );
        """)
        conn.commit()
        # Данные о группах(время в UTC, но надо проверить правильность)
        # cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?, ?, ?);", (1119554223579873310, 'saturday', '09:00', '11:00', 1119555115691548722, 1119555041230069760))
        # conn.commit()

        # cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?, ?, ?);", (1119556931296698539, 'saturday', '11:00', '13:00', 1119556186421866566, 1119556008252035143))
        # conn.commit()

        # cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?, ?, ?);", (1119557155801026622, 'monday, thursday', '08:00', '09:00', 1119562226299318303, 1119562137170366474))
        # conn.commit()

        # cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?, ?, ?);", (1119557293596479559, 'monday, wednesday', '14:00', '15:00', 1119562492260134922, 1119562433133023282))
        # conn.commit()

        # cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?, ?, ?);", (1119557472559042620, 'monday, wednesday', '15:00', '16:00', 1122905299423072368, 1122905860188950619))
        # conn.commit()

        # cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?, ?, ?);", (1119557596907577404, 'monday, wednesday', '16:00', '17:00', 1120389836730286110, 1120389774243549247))
        # conn.commit()

        # cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?, ?, ?);", (1119557679505997944, 'tuesday, thursday', '15:00', '16:00', 1120730337044090890, 1120730234388484136))
        # conn.commit()

        # cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?, ?, ?);", (1119557752419794964, 'tuesday, thursday', '16:00', '17:00', 1120745828504567939, 1120745752755445810))
        # conn.commit()

        # cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?, ?, ?);", (1119557849857667202, 'wednesday, friday', '13:00', '14:00', 1121063191481421904, 1121063123391098991))
        # conn.commit()

        ## Test
        # cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?, ?, ?);", (1119557596907577404, 'monday, friday, saturday, sunday', '09:26', '11:00', 1120389836730286110, 1120389774243549247))
        # conn.commit()
        # cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?, ?, ?);", (1132589392079355904, 'saturday, sunday, monday, tuesday, wednesday, thursday, friday', '20:06', '20:08', 1126820305923493888, 1119576448064294972))
        # conn.commit()
        # conn.close()

    # Students
    def get_all_students(self) -> list:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM students")
        students = cur.fetchall()
        students_data = []
        conn.close()
        for student in students:
            students_data.append(
                {
                    'discord_id': student[0],
                    'name': student[1],
                    'role_id': student[2],
                    'dvmn_link': student[3],
                    'skips': student[4]
                }
            )
        return students_data


    def get_student(self, discord_id: int) -> dict:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM students where discord_id={discord_id}")
        student = cur.fetchone()
        conn.close()
        return {
                    'discord_id': student[0],
                    'name': student[1],
                    'role_id': student[2],
                    'dvmn_link': student[3],
                    'skips': student[4]
        }

    def update_student_skips(self, skips: int, discord_id: int) -> None:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(
        f"UPDATE students SET skips = {skips} WHERE discord_id = {discord_id}"
        )
        conn.commit()
        conn.close()

    def get_all_students_for_group(self, role_id: int) -> list:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM students where role_id={role_id}")
        students = cur.fetchall()
        students_data = []
        conn.close()
        for student in students:
            students_data.append(
                {
                    'discord_id': student[0],
                    'name': student[1],
                    'role_id': student[2],
                    'dvmn_link': student[3],
                    'skips': student[4]
                }
            )
        return students_data

    def get_all_students_ids(self) -> list:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM students")
        otv = [i[0] for i in cur.fetchall()]
        conn.close()
        return otv

    def add_student(self, about_user: list) -> None:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO students VALUES(?, ?, ?, ?, ?);", about_user)
        conn.commit()
        conn.close()

    def remove_student(self, discord_id: int) -> None:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f'DELETE from students WHERE discord_id={discord_id}')
        conn.commit()
        conn.close()

    def remove_all_students(self) -> None:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f'DELETE from students')
        conn.commit()
        conn.close()

    # Groups
    def create_group(self, role_id: int, days: str, start_time: str, end_time: str, voice_chat_id: int, text_chat_id: int) -> None:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO groups VALUES(?, ?, ?, ?, ?, ?);", (role_id, days, start_time, end_time, voice_chat_id, text_chat_id))
        conn.commit()
        conn.close()

    def remove_group(self, role_id: int) -> None:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f'DELETE from groups WHERE role_id={role_id}')
        conn.commit()
        conn.close()

    def remove_all_groups(self) -> None:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f'DELETE from groups')
        conn.commit()
        conn.close()
    
    def get_all_groups(self) -> list:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM groups")
        groups = cur.fetchall()
        groups_data = []
        conn.close()
        for group in groups:
            groups_data.append(
                {
                    'role_id': group[0],
                    'days': group[1],
                    'start_time': group[2],
                    'end_time': group[3],
                    'voice_chat_id': group[4],
                    'channel_id': group[5]
                }
            )
        return groups_data

    def get_all_groups_ids(self) -> list:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM groups")
        otv = [i[0] for i in cur.fetchall()]
        conn.close()
        return otv
    
    def get_groups_where_voice_channel(self, voice_chat_id: int) -> dict:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM groups WHERE voice_chat_id = {voice_chat_id}")
        group = cur.fetchone()
        conn.close()
        return {
                'role_id': group[0],
                'days': group[1],
                'start_time': group[2],
                'end_time': group[3],
                'voice_chat_id': group[4],
                'channel_id': group[5]
        }

    def get_free_groups_for_working_of(self, discord_id: int) -> dict:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM students WHERE discord_id = {discord_id}")
        student = cur.fetchone()
        cur = conn.cursor()
        cur.execute("SELECT * FROM groups")
        groups = cur.fetchall()
        otv = []
        for group in groups:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM students WHERE role_id = {group[0]}")
            students_in_group = len(cur.fetchall())
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM working_of WHERE role_id = {group[0]}")
            working_of_group = len(cur.fetchall())
            if working_of_group + students_in_group <= 4 and group[0] != student[2]:
                otv.append(
                    {
                        'role_id': group[0],
                        'days': group[1],
                        'start_time': group[2],
                        'end_time': group[3],
                        'voice_chat_id': group[4],
                        'channel_id': group[5]
                    }
                )
        conn.close()
        return otv

    #Working_of
    def create_working_of(self, discord_id: int, role_id: int, start_time: str, end_time: str, voice_id: int) -> int:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM working_of")
        id = len(cur.fetchall()) + 1
        cur = conn.cursor()
        cur.execute("INSERT INTO working_of VALUES(?, ?, ?, ?, ?, ?, ?);", (id, discord_id, role_id, start_time, end_time, True, voice_id)) # TODO поменять на False
        conn.commit()
        conn.close()
        return id

    def update_working_of_visit(self, db_id: int, is_visit: bool) -> None:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"UPDATE working_of SET student_visit = {is_visit} WHERE id = {db_id}")
        conn.commit()
        conn.close()

    def get_working_of_by_discord_id(self, discord_id: int) -> dict:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM working_of WHERE student_id={discord_id}")
        working_of = cur.fetchone()
        conn.close()
        return {
            'id': working_of[0],
            'student_id': working_of[1],
            'role_id': working_of[2],
            'start_time': working_of[3],
            'end_time': working_of[4],
            'student_visit': working_of[5],
            'voice_id': working_of[6]
        }

    def get_all_working_of(self) -> list:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM working_of")
        all_working_of = cur.fetchall()
        conn.close()
        data = []
        for working_of in all_working_of:
            data.append({
            'id': working_of[0],
            'student_id': working_of[1],
            'role_id': working_of[2],
            'start_time': working_of[3],
            'end_time': working_of[4],
            'student_visit': working_of[5],
            'voice_id': working_of[6]
            })
        return data

    def remove_all_working_of(self) -> None:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f'DELETE from working_of')
        conn.commit()
        conn.close()