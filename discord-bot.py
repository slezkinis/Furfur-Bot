import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import schedule
from schedule import repeat, every
import datetime

from db import SQL


db = SQL()


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


async def job(channel: discord.TextChannel, guild: discord.Guild, members, name):
    # await channel.send(f'🚨Всем привет! Это проверка! Просьба не отключаться от голосового канала ближайшие пару секунд!🚨')
    loop = asyncio.get_event_loop()
    guild = bot.get_guild(int(SERVER_ID))
    voice_channels_names = [i.name for i in guild.voice_channels]
    voice_channel = guild.voice_channels[voice_channels_names.index(name)]
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
        groups = await loop.run_in_executor(None, db.get_free_groups_for_working_of, student.id)
        print(groups)
        groups_texts = []
        num = 1
        for group in groups:
            days = group['days'].replace('monday', 'понедельник').replace('tuesday', 'вторник').replace('wednesday', 'среда').replace('thursday', 'четверг').replace('friday', 'пятница').replace('saturday', 'суббота').replace('sunday', 'воскресенье')
            for index in range(len(days.split(', '))):
                groups_texts.append(f'{num}. День: {days.split(", ")[index]}\n  Время: в {group["start_time"]}')
                num += 1
        if groups_texts:
            await student.send('Привет! Ты пропустил занятие, которое сейчас было! Не переживай, этот пропуск можно отработать:) Вот доступные группы:\n{}\nОтработка идёт один час!\nЧтобы зарегистрироваться на отработку напиши: /work_of <Номер группы (смотри сверху)>'.format('\n'.join(groups_texts))) #TODO Добавить к базе данных!
        else:
            await student.send('Привет! Ты пропустил занятие, которое сейчас было! Не переживай, этот пропуск можно отработать:) Но к сожалению, сейчас нет доступной группы. Сможешь проверить доступные группы через несколько дней с помощью команды: /check')

@repeat(every(10).seconds)
def start_update():
    asyncio.run_coroutine_threadsafe(update(), bot.loop)


async def update():
    loop = asyncio.get_event_loop()
    guild = bot.get_guild(int(SERVER_ID))
    groups = await loop.run_in_executor(None, db.get_all_groups)
    database = dict()
    for group in groups:
        group_name = guild.get_channel(group['voice_chat_id']).name
        hour, _ = group['start_time'].split(':')
        time = ':'.join((hour, '30'))
        members = await loop.run_in_executor(None, db.get_all_students_for_group, group['role_id'])
        database[group_name] = {'days': group['days'].split(', '), 'time': '14:33', 'channel_id': group['channel_id'], 'members': [{'name': i['name'], 'id': i['discord_id']} for i in members]}
    schedule.clear('check')
    for name, data in database.items():
        channel = bot.get_channel(data['channel_id'])
        # print('; '.join(data['members']))
        for date in data['days']:
            if date == 'monday':
                schedule.every().monday.at(data['time']).do(lambda channel, guild, members, name: asyncio.run_coroutine_threadsafe(job(channel, guild, members, name), bot.loop), channel, guild, data['members'], name).tag('check')
            elif date == 'tuesday':
                schedule.every().tuesday.at(data['time']).do(lambda channel, guild, members, name: asyncio.run_coroutine_threadsafe(job(channel, guild, members, name), bot.loop), channel, guild, data['members'], name).tag('check')
            elif date == 'wednesday':
                schedule.every().wednesday.at(data['time']).do(lambda channel, guild, members, name: asyncio.run_coroutine_threadsafe(job(channel, guild, members, name), bot.loop), channel, guild, data['members'], name).tag('check')
            elif date == 'thursday':
                schedule.every().thursday.at(data['time']).do(lambda channel, guild, members, name: asyncio.run_coroutine_threadsafe(job(channel, guild, members, name), bot.loop), channel, guild, data['members'], name).tag('check')
            elif date == 'friday':
                schedule.every().friday.at(data['time']).do(lambda channel, guild, members, name: asyncio.run_coroutine_threadsafe(job(channel, guild, members, name), bot.loop), channel, guild, data['members'], name).tag('check')
            elif date == 'saturday':
                schedule.every().saturday.at(data['time']).do(lambda channel, guild, members, name: asyncio.run_coroutine_threadsafe(job(channel, guild, members, name), bot.loop), channel, guild, data['members'], name).tag('check')
            elif date == 'sunday':
                schedule.every().sunday.at(data['time']).do(lambda channel, guild, members, name: asyncio.run_coroutine_threadsafe(job(channel, guild, members, name), bot.loop), channel, guild, data['members'], name).tag('check')


#TODO Нужно поменять time
async def send_info():
    await update()
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

load_dotenv()

SERVER_ID = 1119553215856386058

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())
bot.remove_command('help')

@bot.event
async def on_ready():
    asyncio.run_coroutine_threadsafe(send_info(), bot.loop)


@bot.event
async def on_member_join(member): # В дальнейшем, функция echo переедет сюда. Срабатывает, когда человек присоединяется
    loop = asyncio.get_running_loop()
    groups = await loop.run_in_executor(None, db.get_all_groups)
    groups_texts = []
    num = 1
    for group in groups:
        days = group['days'].replace('monday', 'понедельник').replace('tuesday', 'вторник').replace('wednesday', 'среда').replace('thursday', 'четверг').replace('friday', 'пятница').replace('saturday', 'суббота').replace('sunday', 'воскресенье')
        groups_texts.append(f'{num}. Дни: {days}\n  Время: с {group["start_time"]} до {group["end_time"]}')
        num += 1
    user = bot.get_user(member.id)
    await user.send('### Привет! Добро пожаловать в мир Python:) Вот доступные группы:\n{}\nЧтобы зарегистрироваться введи команду:\n/reg ***<Имя>*** ***<Фамилия>*** ***<ID группы (смотри сверху)>*** ***<ссылка на твой Devman профиль>***'.format("\n".join(groups_texts)))


@bot.command(name='check')
async def check_working_of(ctx):
    loop = asyncio.get_event_loop()
    author = ctx.message.author
    guild = bot.get_guild(int(SERVER_ID))
    user = guild.get_member(author.id)
    user_skips = (await loop.run_in_executor(None, db.get_student, user.id))['skips']
    if not user_skips:
        await ctx.reply('У тебя нет пропусков! Поздравляю:)')
        return
    groups = await loop.run_in_executor(None, db.get_free_groups_for_working_of, user.id)
    groups_texts = []
    num = 1
    for group in groups:
        days = group['days'].replace('monday', 'понедельник').replace('tuesday', 'вторник').replace('wednesday', 'среда').replace('thursday', 'четверг').replace('friday', 'пятница').replace('saturday', 'суббота').replace('sunday', 'воскресенье')
        for index in range(len(days.split(', '))):
            groups_texts.append(f'{num}. День: {days.split(", ")[index]}\n  Время: в {group["start_time"]}')
            num += 1
    if groups_texts:
        await ctx.reply('Привет! Cейчас у тебя вот столько пропусков: {}. Не переживай, их можно отработать:) Вот доступные группы:\n{}\nОтработка идёт один час!\nЧтобы зарегистрироваться на отработку напиши: /work_of <Номер группы (смотри сверху)>'.format(user_skips, '\n'.join(groups_texts))) #TODO Добавить к базе данных!
    else:
        await ctx.reply('Привет! Cейчас у тебя вот столько пропусков: {}. Не переживай, их можно отработать:) Но к сожалению, сейчас нет доступной группы. Сможешь проверить доступные группы через несколько дней с помощью команды: /check'.format(user_skips))


@bot.command(name='work_of')
async def add_work_of(ctx, group_number: int = None):
    loop = asyncio.get_event_loop()
    author = ctx.message.author
    guild = bot.get_guild(int(SERVER_ID))
    user = guild.get_member(author.id)
    working_of = []
    groups = await loop.run_in_executor(None, db.get_free_groups_for_working_of, user.id)
    for group in groups:
        days = group['days'].replace('monday', 'понедельник').replace('tuesday', 'вторник').replace('wednesday', 'среда').replace('thursday', 'четверг').replace('friday', 'пятница').replace('saturday', 'суббота').replace('sunday', 'воскресенье')
        for index in range(len(days.split(', '))):
            working_of.append((group['role_id'], group['days'].split(', ')[index]))
    if group_number is None:
        await ctx.reply('Ты не указал группу для отработки!')
        return
    if group_number - 1 > len(working_of) or group_number < 1:
        await ctx.reply('Такой группы не существует')
        return
    
    
    
@bot.command(name='echo') # Заглушка! В дальнейшем, можно добавить команду и использовать код
async def help(ctx):
    loop = asyncio.get_running_loop()
    groups = await loop.run_in_executor(None, db.get_all_groups)
    groups_texts = []
    num = 1
    author = ctx.message.author
    for group in groups:
        days = group['days'].replace('monday', 'понедельник').replace('tuesday', 'вторник').replace('wednesday', 'среда').replace('thursday', 'четверг').replace('friday', 'пятница').replace('saturday', 'суббота').replace('sunday', 'воскресенье')
        groups_texts.append(f'{num}. Дни: {days}\n  Время: с {group["start_time"]} до {group["end_time"]}')
        num += 1
    user = bot.get_user(author.id)
    await user.send('### Привет! Добро пожаловать в мир Python:) Вот доступные группы:\n{}\nЧтобы зарегистрироваться введи команду:\n/reg ***<Имя>*** ***<Фамилия>*** ***<ID группы (смотри сверху)>*** ***<ссылка на твой Devman профиль>***'.format("\n".join(groups_texts)))

@bot.command() # Функция регистрации. Проверяет все данные и отправляет обратную связь
async def reg(ctx, name=None, last_name=None, role_id=None, *, devman_url=None):
    loop = asyncio.get_running_loop()
    if name is None or last_name is None or role_id is None or devman_url is None:
        await ctx.reply('Мне кажется, что ты какой-то из аргументов не указал:( Проверь!')
        return
    author = ctx.message.author
    students_ids = await loop.run_in_executor(None, db.get_all_students_ids)
    if author.id in students_ids:
        await ctx.reply('### Ты уже зарегестрирован в базе данных!\nЕсли ты хочешь изменить свою групппу или думаешь, что я ошибся, то обратись к Михаилу!')
        return
    all_groups = await loop.run_in_executor(None, db.get_all_groups_ids)
    guild = bot.get_guild(int(SERVER_ID))
    if int(role_id) > len(all_groups) or int(role_id) < 1:
        await ctx.reply('Такой группы не существует! Проверь правильность ввода данных')
        return
    role = guild.get_role(all_groups[int(role_id) - 1])
    user = guild.get_member(author.id)
    await user.add_roles(role)
    await loop.run_in_executor(None, db.add_student, (author.id, f'{name} {last_name}', role.id, devman_url, 0))
    await ctx.reply(f'Теперь ты назначен в группу {role.name}')


def main():
    bot.run(os.getenv('DISCORD_TOKEN'))


if __name__ == '__main__':
    main()