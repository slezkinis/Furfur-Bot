import discord
from discord.ext import commands 
from dotenv import load_dotenv
import os
import asyncio
import schedule
from schedule import repeat, every
import datetime
from scheduler import Scheduler
import urllib.parse

from db import SQL
import google_sheet

load_dotenv()


db = SQL()
once_schedule = Scheduler()
sheet = google_sheet.start_google_sheet()


def next_weekday(d, weekday): # Подсчёт даты следующего дня недели
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


async def planed_voice_check(channel: discord.TextChannel, guild: discord.Guild, members, voice_channel): # Используется для проверки участников в голос. канале (не считая отработок)
    # await channel.send(f'🚨Всем привет! Это проверка! Просьба не отключаться от голосового канала ближайшие пару секунд!🚨')
    loop = asyncio.get_event_loop()
    guild = bot.get_guild(int(SERVER_ID))
    was = []
    was_working_of = []
    for member in members:
        user = guild.get_member(member['id'])
        if member['id'] not in [i.id for i in voice_channel.members]:
            was_working_of.append(user)
        else:
            was.append(user.name)
    # await channel.send(f'Сегодня на занятиях были: {", ".join(was)}')
    for student in was_working_of:
        student_info = await loop.run_in_executor(None, db.get_student, student.id)
        new_student_skips = student_info['skips'] + 1
        await loop.run_in_executor(None, db.update_student_skips, new_student_skips, student.id)
        await loop.run_in_executor(None, db.add_skip, student.id, str(datetime.datetime.now().strftime('%d.%m.%Y')))
        groups = await loop.run_in_executor(None, db.get_free_groups_for_working_of, student.id)
        groups_texts_dates = []
        for group in groups:
            days = group['days'].replace('monday', '0').replace('tuesday', '1').replace('wednesday', '2').replace('thursday', '3').replace('friday', '4').replace('saturday', '5').replace('sunday', '6')
            for index in range(len(days.split(', '))):
                date = next_weekday(datetime.date.today(), int(days.split(', ')[index]))
                moscow_time = f'{int(group["start_time"].split(":")[0]) + 3}:{group["start_time"].split(":")[1]}'
                groups_texts_dates.append((f'{date.strftime("%d.%m")} в {moscow_time}', date))
        groups_texts = [f'{num}. {i[0]}' for num, i in enumerate(sorted(groups_texts_dates, key=lambda i: i[1]), 1)]
        if groups_texts:
            await student.send('Привет! Ты пропустил занятие, которое сейчас было! Не переживай, этот пропуск можно отработать:) Вот доступные группы:\n{}\nОтработка идёт один час!\nЧтобы зарегистрироваться на отработку напиши: /work_of <Номер группы (смотри сверху)>'.format('\n'.join(groups_texts))) #TODO Добавить к базе данных!
        else:
            await student.send('Привет! Ты пропустил занятие, которое сейчас было! Не переживай, этот пропуск можно отработать:) Но к сожалению, сейчас нет доступной группы. Сможешь проверить доступные группы через несколько дней с помощью команды: /check')


@repeat(every(10).seconds) # Здесь каждые 10 секунд запускается функция, в которой обновляются данные из дб
def start_update():
    asyncio.run_coroutine_threadsafe(update(), bot.loop)

async def update(): # обновляются данные из дб
    loop = asyncio.get_event_loop()
    guild = bot.get_guild(int(SERVER_ID))
    groups = await loop.run_in_executor(None, db.get_all_groups)
    database = dict()
    for group in groups:
        group_voice_channel = guild.get_channel(group['voice_chat_id'])
        hour, _ = group['start_time'].split(':')
        time = ':'.join((hour, '30'))
        if len(time) != 5:
            time = '0' + time
        members = await loop.run_in_executor(None, db.get_all_students_for_group, group['role_id'])
        database_members = []
        now_week_day = str(datetime.datetime.now().isoweekday()).replace('1', 'monday').replace('2', 'tuesday').replace('3', 'wednesday').replace('4', 'thursday').replace('5', 'friday').replace('6', 'saturday').replace('7', 'sunday')
        for member in members:
            if not member['days'] or now_week_day == member['days']:
                database_members.append({'name': member['name'], 'id': member['discord_id']})
        database[group_voice_channel] = {'days': group['days'].split(', '), 'time': time, 'channel_id': group['channel_id'], 'members': database_members}
    schedule.clear('check')
    for voice_channel, data in database.items():
        channel = bot.get_channel(data['channel_id'])
        for date in data['days']:
            if date == 'monday':
                schedule.every().monday.at(data['time']).do(lambda channel, guild, members, voice_channel: asyncio.run_coroutine_threadsafe(planed_voice_check(channel, guild, members, voice_channel), bot.loop), channel, guild, data['members'], voice_channel).tag('check')
            elif date == 'tuesday':
                schedule.every().tuesday.at(data['time']).do(lambda channel, guild, members, voice_channel: asyncio.run_coroutine_threadsafe(planed_voice_check(channel, guild, members, voice_channel), bot.loop), channel, guild, data['members'], voice_channel).tag('check')
            elif date == 'wednesday':
                schedule.every().wednesday.at(data['time']).do(lambda channel, guild, members, voice_channel: asyncio.run_coroutine_threadsafe(planed_voice_check(channel, guild, members, voice_channel), bot.loop), channel, guild, data['members'], voice_channel).tag('check')
            elif date == 'thursday':
                schedule.every().thursday.at(data['time']).do(lambda channel, guild, members, voice_channel: asyncio.run_coroutine_threadsafe(planed_voice_check(channel, guild, members, voice_channel), bot.loop), channel, guild, data['members'], voice_channel).tag('check')
            elif date == 'friday':
                schedule.every().friday.at(data['time']).do(lambda channel, guild, members, voice_channel: asyncio.run_coroutine_threadsafe(planed_voice_check(channel, guild, members, voice_channel), bot.loop), channel, guild, data['members'], voice_channel).tag('check')
            elif date == 'saturday':
                schedule.every().saturday.at(data['time']).do(lambda channel, guild, members, voice_channel: asyncio.run_coroutine_threadsafe(planed_voice_check(channel, guild, members, voice_channel), bot.loop), channel, guild, data['members'], voice_channel).tag('check')
            elif date == 'sunday':
                schedule.every().sunday.at(data['time']).do(lambda channel, guild, members, voice_channel: asyncio.run_coroutine_threadsafe(planed_voice_check(channel, guild, members, voice_channel), bot.loop), channel, guild, data['members'], voice_channel).tag('check')


async def get_roles_and_notofication(user: discord.Member, role_id: int): # За 10 минут для отработки бот напоминает и выдаёт роль
    guild = bot.get_guild(int(SERVER_ID))
    role = guild.get_role(role_id)
    await user.add_roles(role)
    await user.send(f'Хэй! Ты не забыл, что у тебя через ***10 минут*** занятия? Можешь присоединятся в голосовой канал с названием ***Занятие {role.name}***')


async def check_members_work_of(user: discord.Member, voice_chat_id: int, db_id: int): # Проверка студента на отработке
    loop = asyncio.get_event_loop()
    guild = bot.get_guild(int(SERVER_ID))
    voice_chat_members = [member.id for member in guild.get_channel(voice_chat_id).members]
    if user.id in voice_chat_members:
        await loop.run_in_executor(None, db.update_working_of_visit, db_id, True)
    else:
        student_info = await loop.run_in_executor(None, db.get_student, user.id)
        new_student_skips = student_info['skips'] + 1
        await loop.run_in_executor(None, db.update_student_skips, new_student_skips, user.id)
        groups = await loop.run_in_executor(None, db.get_free_groups_for_working_of, user.id)
        groups_texts_dates = []
        for group in groups:
            days = group['days'].replace('monday', '0').replace('tuesday', '1').replace('wednesday', '2').replace('thursday', '3').replace('friday', '4').replace('saturday', '5').replace('sunday', '6')
            for index in range(len(days.split(', '))):
                date = next_weekday(datetime.date.today(), int(days.split(', ')[index]))
                moscow_time = f'{int(group["start_time"].split(":")[0]) + 3}:{group["start_time"].split(":")[1]}'
                groups_texts_dates.append((f'{date.strftime("%d.%m")} в {moscow_time}', date))
        groups_texts = [f'{num}. {i[0]}' for num, i in enumerate(sorted(groups_texts_dates, key=lambda i: i[1]), 1)]
        if groups_texts:
            await user.send('Привет! Ты пропустил занятие, которое сейчас было! Не переживай, этот пропуск можно отработать:) Вот доступные группы:\n{}\nОтработка идёт один час!\nЧтобы зарегистрироваться на отработку напиши: /work_of <Номер группы (смотри сверху)>'.format('\n'.join(groups_texts))) #TODO Добавить к базе данных!
        else:
            await user.send('Привет! Ты пропустил занятие, которое сейчас было! Не переживай, этот пропуск можно отработать:) Но к сожалению, сейчас нет доступной группы. Сможешь проверить доступные группы через несколько дней с помощью команды: /check')


async def remove_role(user: discord.Member, role_id: int, db_id: int): # После окончания отработки бот забирает роль
    loop = asyncio.get_event_loop()
    guild = bot.get_guild(int(SERVER_ID))
    role = guild.get_role(role_id)
    await user.remove_roles(role)
    work_of = await loop.run_in_executor(None, db.get_working_of_by_id, db_id)
    if work_of['student_visit']:
        await user.send(f'Поздравляю! Ты отработал своё пропущенное занятие! Старйся больше не пропускать!')

async def start_database():
    await update()
    loop = asyncio.get_event_loop()
    await upload_working_of_to_scheldue()
    while True:
        await loop.run_in_executor(None, once_schedule.exec_jobs)
        schedule.run_pending()
        await asyncio.sleep(1)


async def upload_working_of_to_scheldue():
    loop = asyncio.get_event_loop()
    all_working_of = await loop.run_in_executor(None, db.get_all_working_of)
    now = datetime.datetime.now()
    once_schedule.delete_jobs()
    for working_of in all_working_of:
        try:
            start_time = datetime.datetime.strptime(working_of['start_time'], '%Y-%m-%d %H:%M:%S')
        except:
            start_time = datetime.datetime.strptime(working_of['start_time'], '%Y-%m-%d %H:%M')
        end_time = start_time + datetime.timedelta(hours=1)
        if now <= start_time:
            user = bot.get_user(working_of['student_id'])
            once_schedule.once(start_time - datetime.timedelta(minutes=10), lambda user, role_id: asyncio.run_coroutine_threadsafe(get_roles_and_notofication(user, role_id), bot.loop), args=(user, working_of['role_id'], ))
            once_schedule.once(start_time + datetime.timedelta(minutes=15), lambda user, voice_chat_id, db_id: asyncio.run_coroutine_threadsafe(check_members_work_of(user, voice_chat_id, db_id), bot.loop), args=(user, working_of['voice_id'], working_of['id'], )) # TODO
            once_schedule.once(end_time, lambda user, role_id, db_id: asyncio.run_coroutine_threadsafe(remove_role(user, role_id, db_id), bot.loop), args=(user, working_of['role_id'], working_of['id'], ))


SERVER_ID = int(os.getenv('SERVER_ID'))
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID'))


bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())
bot.remove_command('help')


@bot.event
async def on_ready(): # После запуска бота запускается дб и задаётся статус бота
    loop = asyncio.get_event_loop()
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('Python 💻'))
    asyncio.run_coroutine_threadsafe(start_database(), bot.loop)

# Временно убрал код для теста бота
# @bot.event
# async def on_member_join(member): # В дальнейшем, функция echo переедет сюда. Срабатывает, когда человек присоединяется
#     loop = asyncio.get_running_loop()
#     groups = await loop.run_in_executor(None, db.get_all_groups_ids)
#     guild = bot.get_guild(int(SERVER_ID))
#     groups_texts = [f'{num}. {guild.get_role(group_role_id)}' for num, group_role_id in enumerate(groups, 1)]
#     user = bot.get_user(member.id)
#     await user.send('### Привет! Я бот-помощник на сервере Python всё съест! Сейчас тебе нужно выбрать свою группу, в которой ты учишься (лучше уточни родителей или преподавателя). Вот доступные группы:\n{}\nЧтобы зарегистрироваться введи команду прямо ко мне в чат:\n/reg ***<Имя>*** ***<Фамилия>*** ***<ID группы (смотри сверху)>*** ***<ссылка на твой Devman профиль>***\n Вот пример: /reg Фурфур Фурфурный 1 https://dvmn.org/user/furfur/'.format("\n".join(groups_texts)))


@bot.command(name='check') # Используется для проверки пропусков.
async def check_working_of(ctx):
    loop = asyncio.get_event_loop()
    author = ctx.message.author
    guild = bot.get_guild(int(SERVER_ID))
    user = guild.get_member(author.id)
    try:
        user_skips = (await loop.run_in_executor(None, db.get_student, user.id))['skips']
    except TypeError:
        await ctx.reply('Я не нашёл тебя в своей базе данных. Ты уверен, что ты прописывал команду /reg.')
        return
    if not user_skips:
        await ctx.reply('У тебя нет пропусков! Поздравляю:)')
        return
    groups = await loop.run_in_executor(None, db.get_free_groups_for_working_of, user.id)
    groups_texts_dates = []
    for group in groups:
        days = group['days'].replace('monday', '0').replace('tuesday', '1').replace('wednesday', '2').replace('thursday', '3').replace('friday', '4').replace('saturday', '5').replace('sunday', '6')
        for index in range(len(days.split(', '))):
            date = next_weekday(datetime.date.today(), int(days.split(', ')[index]))
            moscow_time = f'{int(group["start_time"].split(":")[0]) + 3}:{group["start_time"].split(":")[1]}'
            groups_texts_dates.append((f'{date.strftime("%d.%m")} в {moscow_time}', date))
    groups_texts = [f'{num}. {i[0]}' for num, i in enumerate(sorted(groups_texts_dates, key=lambda i: i[1]), 1)]
    if groups_texts:
        await ctx.reply('Привет! Cейчас у тебя вот столько пропусков: {}. Не переживай, их можно отработать:) Вот доступные группы:\n{}\nОтработка идёт один час!\nЧтобы зарегистрироваться на отработку напиши: /work_of <Номер группы (смотри сверху)>'.format(user_skips, '\n'.join(groups_texts))) #TODO Добавить к базе данных!
    else:
        await ctx.reply('Привет! Cейчас у тебя вот столько пропусков: {}. Не переживай, их можно отработать:) Но к сожалению, сейчас нет доступной группы. Сможешь проверить доступные группы через несколько дней с помощью команды: /check'.format(user_skips))

@bot.command(name='work_of') # Для записи на отработку
async def add_work_of(ctx, group_number: int = None):
    loop = asyncio.get_event_loop()
    author = ctx.message.author
    guild = bot.get_guild(int(SERVER_ID))
    user = guild.get_member(author.id)
    try:
        student_skips = (await loop.run_in_executor(None, db.get_student, int(author.id)))['skips']
    except TypeError:
        await ctx.reply('Я не нашёл тебя в своей базе данных. Ты уверен, что ты прописывал команду /reg.')
        return
    groups = await loop.run_in_executor(None, db.get_free_groups_for_working_of, user.id)
    working_of_dates = []
    for group in groups:
        days = group['days'].replace('monday', '0').replace('tuesday', '1').replace('wednesday', '2').replace('thursday', '3').replace('friday', '4').replace('saturday', '5').replace('sunday', '6')
        for index in range(len(days.split(', '))):
            date = next_weekday(datetime.datetime.today(), int(days.split(', ')[index]))
            working_of_dates.append((group['start_time'], date.strftime('%Y-%m-%d'), group['role_id'], group['voice_chat_id']))
    all_working_of = sorted(working_of_dates, key=lambda i: i[1])
    if group_number is None:
        await ctx.reply('Ты не указал группу для отработки!')
        return
    if group_number - 1 > len(all_working_of) or group_number < 1:
        await ctx.reply('Такой группы не существует')
        return
    if student_skips == 0:
        await ctx.reply('У тебя нет пропусков! Тебе не надо ничего отрабатывать:) Круто:)')
        return
    selected_working_of = all_working_of[group_number - 1]
    start_time = datetime.datetime.strptime(f'{selected_working_of[1]} {selected_working_of[0]}', '%Y-%m-%d %H:%M')
    end_time = start_time + datetime.timedelta(hours=1)
    id = await loop.run_in_executor(None, db.create_working_of, user.id, selected_working_of[2], start_time, end_time, selected_working_of[3])
    once_schedule.once(start_time - datetime.timedelta(minutes=10), lambda user, role_id: asyncio.run_coroutine_threadsafe(get_roles_and_notofication(user, role_id), bot.loop), args=(user, selected_working_of[2], ))
    once_schedule.once(start_time + datetime.timedelta(minutes=15), lambda user, voice_chat_id, db_id: asyncio.run_coroutine_threadsafe(check_members_work_of(user, voice_chat_id, db_id), bot.loop), args=(user, selected_working_of[3], id, )) # TODO
    once_schedule.once(end_time, lambda user, role_id, db_id: asyncio.run_coroutine_threadsafe(remove_role(user, role_id, db_id), bot.loop), args=(user, selected_working_of[2], id, ))
    role_name =  guild.get_role(selected_working_of[2]).name
    student_info = await loop.run_in_executor(None, db.get_student, user.id)
    new_student_skips = student_info['skips'] - 1
    await loop.run_in_executor(None, db.update_student_skips, new_student_skips, user.id)
    moscow_start_time = start_time + datetime.timedelta(hours=3)
    await ctx.reply(f'Всё! Я записал тебя! ***{moscow_start_time.strftime("%d.%m.%Y %H:%M")}*** подключайся к голосовому каналу ***Занятие {role_name}*** (доступ к нему у тебя откроется за 10 минут до начала). Также перед началом я тебе напомню! Прошу не опаздывать!' )
 

@bot.command(name='echo') # Заглушка! В дальнейшем, можно добавить команду и использовать код
async def help(ctx):
    loop = asyncio.get_running_loop()
    groups = await loop.run_in_executor(None, db.get_all_groups_ids)
    guild = bot.get_guild(int(SERVER_ID))
    groups_texts = [f'{num}. {guild.get_role(group_role_id)}' for num, group_role_id in enumerate(groups, 1)]
    author = ctx.message.author
    user = bot.get_user(author.id)
    await user.send('### Привет! Я бот-помощник на сервере Python всё съест! Сейчас тебе нужно выбрать свою группу, в которой ты учишься (лучше уточни родителей или преподавателя). Вот доступные группы:\n{}\nЧтобы зарегистрироваться введи команду прямо ко мне в чат:\n/reg ***<Имя>*** ***<Фамилия>*** ***<ID группы (смотри сверху)>*** ***<ссылка на твой Devman профиль>***\n Вот пример: /reg Фурфур Фурфурный 1 https://dvmn.org/user/furfur/'.format("\n".join(groups_texts)))


@bot.command() # Функция регистрации. Проверяет все данные и отправляет обратную связь
async def reg(ctx, name=None, last_name=None, role_id=None, *, devman_url=None):
    loop = asyncio.get_running_loop()
    if name is None or last_name is None or role_id is None or devman_url is None:
        await ctx.reply('Мне кажется, что ты какой-то из аргументов не указал:( Проверь!')
        return
    author = ctx.message.author
    students_ids = await loop.run_in_executor(None, db.get_all_students_ids)
    try:
        int(role_id)
    except:
        await ctx.reply('Номер группы должен быть числом! Проверь это!')
        return
    if author.id in students_ids:
        await ctx.reply('### Ты уже зарегестрирован в базе данных!\nЕсли ты хочешь изменить свою групппу или думаешь, что я ошибся, то обратись к Михаилу!')
        return
    url_patrs = urllib.parse.urlparse(devman_url)
    if not (url_patrs.netloc == 'dvmn.org' and '/user/' in url_patrs.path):
        await ctx.reply('Мне кажется, что ссылка ведёт не на твой профиль в Devman! Проверь!')
        return
    all_groups = await loop.run_in_executor(None, db.get_all_groups_ids)
    guild = bot.get_guild(int(SERVER_ID))
    if int(role_id) > len(all_groups) or int(role_id) < 1:
        await ctx.reply('Такой группы не существует! Проверь правильность ввода данных')
        return
    role = guild.get_role(all_groups[int(role_id) - 1])
    user = guild.get_member(author.id)
    await user.add_roles(role)
    await loop.run_in_executor(None, db.add_student, (author.id, f'{name} {last_name}', role.id, devman_url, 0, ''))
    await ctx.reply(f'Теперь ты назначен в группу {role.name}. Проверь, в нашем Discord сервере у тебя должны появится новый текстовый и голосовой каналы. В голосовом будут проходить занятия. Просто подключись к нему за несколько минут до начала. Удачи тебе в обучении и у тебя всё получится:)')


@bot.command() # Функция для админов. Удаляет ученика из базы данных и убирает у него роли
async def unreg(ctx, user: discord.Member = None):
    loop = asyncio.get_running_loop()
    author = ctx.message.author
    author_roles = [role.id for role in author.roles]
    if ADMIN_ROLE_ID in author_roles:
        if user is None:
            await ctx.reply('Ты не указал пользователя, которого нужно удалить!')
            await asyncio.sleep(3)
            await ctx.channel.purge(limit=2)
            return
        await loop.run_in_executor(None, db.remove_student, user.id)
        for role in user.roles:
            if role.id != ADMIN_ROLE_ID:
                try:
                    await user.remove_roles(role)
                except:
                    continue
        await ctx.reply(f'{user} был удалён из базы данных и у него были убраны все роли!')
    else:
        await ctx.reply('У Вас нет права на лево!')
    await asyncio.sleep(3)
    await ctx.channel.purge(limit=2)


@bot.command() # Функция очистки
async def clear(ctx, amount = 3):
    author = ctx.message.author
    author_roles = [role.id for role in author.roles]
    if ADMIN_ROLE_ID in author_roles:
        await ctx.channel.purge(limit=amount + 1)
    else:
        await ctx.reply('У Вас нет права на лево!')
        await asyncio.sleep(3)
        await ctx.channel.purge(limit=2)

@bot.command() # Функция очистки
async def clear_skips(ctx):
    author = ctx.message.author
    if ctx.channel.guild:
        author_roles = [role.id for role in author.roles]
    else:
        guild = bot.get_guild(int(SERVER_ID))
        author_roles = [role.id for role in guild.get_member(author.id).roles]
    if ADMIN_ROLE_ID in author_roles:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, db.remove_all_skips)
        await ctx.reply('Все пропуски удалены из базы данных!')
        await asyncio.sleep(3)
        try:
            await ctx.channel.purge(limit=2)
        except:
            pass
    else:
        await ctx.reply('У Вас нет права на лево!')
        await asyncio.sleep(3)
        await ctx.channel.purge(limit=2)
# @bot.command()
# async def add(ctx):
#     loop = asyncio.get_running_loop()
#     author = ctx.message.author
#     student_info = await loop.run_in_executor(None, db.get_student, author.id)
#     new_student_skips = student_info['skips'] + 1
#     await loop.run_in_executor(None, db.update_student_skips, new_student_skips, author.id)


# @bot.command()
# async def minus(ctx):
#     loop = asyncio.get_running_loop()
#     author = ctx.message.author
#     student_info = await loop.run_in_executor(None, db.get_student, author.id)
#     new_student_skips = student_info['skips'] - 1
#     await loop.run_in_executor(None, db.update_student_skips, new_student_skips, author.id)

@bot.command()
async def help(ctx):
    author = ctx.message.author
    user = bot.get_user(author.id)
    text = '''
Привет! Это список команд:
/reg - Зарегестрироваться в базе данных (/reg Фурфур Фурфурный 1 https://dvmn.org/user/furfur/
/unreg <@user> - Удалить пользователя из базы данных. Только для админа! Пример: /unreg @Furfur
/clear <кол-во сообщений> - Удалить сообщения из чата. Только для админа! По умолчанию: 3 сообщения. Пример: /clear 1
/check - Проверить кол-во пропусков у себя
/work_of <номер группы> - записаться на отработку. Пример: /work_of 1
Если будут вопросы, спрашивай у преподавателя.'''
    await user.send(text)
    try:
        await ctx.channel.purge(limit=1)
    except:
        pass


@bot.command()
async def download(ctx):
    author = ctx.message.author
    if ctx.channel.guild:
        author_roles = [role.id for role in author.roles]
    else:
        guild = bot.get_guild(int(SERVER_ID))
        author_roles = [role.id for role in guild.get_member(author.id).roles]
    if ADMIN_ROLE_ID in author_roles:
        loop = asyncio.get_running_loop()
        loop.run_in_executor(None, google_sheet.make_groups_worksheet, sheet)
        loop.run_in_executor(None, google_sheet.make_students_worksheet, sheet)
        loop.run_in_executor(None, google_sheet.make_working_off_worksheet, sheet)
        loop.run_in_executor(None, google_sheet.make_skips_worksheet, sheet)
        await ctx.reply('База данных выгружена в Excel!')
        await asyncio.sleep(3)
        try:
            await ctx.channel.purge(limit=2)
        except:
            pass
    else:
        await ctx.reply('У Вас нет права на лево!')
        await asyncio.sleep(3)
        await ctx.channel.purge(limit=2)


@bot.command()
async def upload(ctx):
    author = ctx.message.author
    if ctx.channel.guild:
        author_roles = [role.id for role in author.roles]
    else:
        guild = bot.get_guild(int(SERVER_ID))
        author_roles = [role.id for role in guild.get_member(author.id).roles]
    if ADMIN_ROLE_ID in author_roles:
        loop = asyncio.get_running_loop()
        loop.run_in_executor(None, google_sheet.upload_workings, sheet)
        loop.run_in_executor(None, google_sheet.upload_group, sheet)
        loop.run_in_executor(None, google_sheet.upload_student, sheet)
        loop.run_in_executor(None, google_sheet.upload_skip, sheet)
        await upload_working_of_to_scheldue()
        await ctx.reply('Данные из Excel загружены в базу!')
        await asyncio.sleep(3)
        try:
            await ctx.channel.purge(limit=2)
        except:
            pass
    else:
        await ctx.reply('У Вас нет права на лево!')
        await asyncio.sleep(3)
        await ctx.channel.purge(limit=2)

def main(): # Главная функция запуска бота
    bot.run(os.getenv('DISCORD_TOKEN'))


if __name__ == '__main__':
    main()

# Created by slezkinis
