import gspread
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import warnings

from db import SQL


db = SQL()
warnings.filterwarnings("ignore")

def start_google_sheet():
    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
    # Указываем путь к JSON
    gc = gspread.service_account(filename='mypython-398016-54057ece9503.json')
    sh = gc.open("Furfur's db")
    return sh


def upload_group(sh):
    groups_worksheet = sh.worksheet("Группы")
    groups_data = groups_worksheet.get_all_values()
    db.remove_all_groups()
    for group in groups_data[1:]:
        if group != ['', '', '', '', '', '']:
            db.create_group(group[0], group[1], group[2], group[3], group[4], group[5])
    make_groups_worksheet(sh)


def upload_student(sh):
    student_worksheet = sh.worksheet("Ученики")
    students_data = student_worksheet.get_all_values()
    db.remove_all_students()
    for student in students_data[1:]:
        if student != ['', '', '', '', '']:
            db.add_student([student[0], student[1], student[2], student[3], student[4]])
    make_students_worksheet(sh)


def upload_workings(sh):
    workings_worksheet = sh.worksheet("Отработки")
    workings_data = workings_worksheet.get_all_values()
    db.remove_all_working_of()
    for working in workings_data[1:]:
        if working != ['', '', '', '', '', '', '']:
            db.create_working_of_by_sheet(working[1], working[2], working[3], working[4], working[5], working[6])
    make_working_off_worksheet(sh)


def make_groups_worksheet(sh):
    try:
        worksheet = sh.add_worksheet(title="Группы", rows=100, cols=6)
    except gspread.exceptions.APIError:
        worksheet = sh.worksheet("Группы")
        worksheet.clear()
    groups = db.get_all_groups()
    data = [['ID Дискорд роли', 'Дни проведения занятия', 'Время начала занятия, UTC', 'Время окончания занятия, UTC', 'ID голосового чата',  'ID канала']]
    if groups:
        for group in groups:
            group_data = [str(group['role_id']), group['days'], group['start_time'], group['end_time'], str(group['voice_chat_id']), str(group['channel_id'])]
            data.append(group_data)
    worksheet.update(f'A1:F{len(data)}', data)
    worksheet.format('A1:F1', {'textFormat': {'bold': True}})


def make_students_worksheet(sh):
    students = db.get_all_students()
    try:
        worksheet = sh.add_worksheet(title="Ученики", rows=100, cols="5")
    except gspread.exceptions.APIError:
        worksheet = sh.worksheet("Ученики")
        worksheet.clear()
    data = [['ID Дискорда', 'Имя', 'ID Дискорд роли', 'Ссылка на DVMN', 'Пропуски']]
    for student in students:
        student_data = [str(student['discord_id']), student['name'], str(student['role_id']), student['dvmn_link'], student['skips']]
        data.append(student_data)
    worksheet.update(f'A1:E{len(data)}', data)
    worksheet.format('A1:E1', {'textFormat': {'bold': True}})


def make_working_off_worksheet(sh):
    workings = db.get_all_working_of()
    try:
        worksheet = sh.add_worksheet(title="Отработки", rows=100, cols="7")
    except gspread.exceptions.APIError:
        worksheet = sh.worksheet("Отработки")
        worksheet.clear()
    data = [['ID', 'ID ученика', 'ID Дискорд роли', 'Время начала занятия, UTC', 'Время окончания занятия, UTC', 'Статус визита ученика', 'ID голосового чата',]]
    for working in workings:
        workings_data = [str(working['id']), working['student_id'], str(working['role_id']), working['start_time'], working['end_time'], working['student_visit'], working['voice_id']]
        data.append(workings_data)
    worksheet.update(f'A1:G{len(data)}', data)
    worksheet.format('A1:G1', {'textFormat': {'bold': True}})
                         

# def main():
#     SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#         # If there are no (valid) credentials available, let the user log in.
#         if not creds or not creds.valid:
#             if creds and creds.expired and creds.refresh_token:
#                 creds.refresh(Request())
#             else:
#                 flow = InstalledAppFlow.from_client_secrets_file(
#                     'credentials.json', SCOPES)
#                 creds = flow.run_local_server(port=0)
#             # Save the credentials for the next run
#             with open('token.json', 'w') as token:
#                 token.write(creds.to_json())
#     # Указываем путь к JSON
#     gc = gspread.service_account(filename='mypython-398016-54057ece9503.json')
#     sh = gc.open('test')
#     make_groups_worksheet(sh)
#     make_students_worksheet(sh)
#     make_working_off_worksheet(sh)
#     while True:
#         a = input()
#         if a == '1':
#             upload_group(sh)
#         if a == '2':
#             upload_student(sh)
#         if a == '3':
#             upload_workings(sh)
# main()