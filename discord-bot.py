import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import schedule
from schedule import repeat, every
from pprint import pprint

from db import SQL


db = SQL()

async def job(channel: discord.TextChannel, guild: discord.Guild, members, name):
    await channel.send(f'🚨Всем привет! Это проверка!🚨')
    guild = bot.get_guild(int(SERVER_ID))
    voice_channels_names = [i.name for i in guild.voice_channels]
    voice_channel = guild.voice_channels[voice_channels_names.index(name)]
    was = []
    for member in members:
        user = guild.get_member(member['id'])
        if member['id'] not in [i.id for i in voice_channel.members]:
            await user.send('Привет! Тебя не было на занятиях! Ай-ай-ай!') #TODO Добавить к базе данных!
        else:
            was.append(user.name)
    await channel.send(f'Сегодня на занятиях были: {", ".join(was)}')

@repeat(every(10).seconds)
def start_update():
    asyncio.run_coroutine_threadsafe(update(), bot.loop)

async def update():
    # schedule.every(10).seconds.do(lambda channel: asyncio.run_coroutine_threadsafe(job(channel), bot.loop), channel)
    # print('Update')
    loop = asyncio.get_event_loop()
    guild = bot.get_guild(int(SERVER_ID))
    groups = await loop.run_in_executor(None, db.get_all_groups)
    database = dict()
    for group in groups:
        group_name = guild.get_channel(group['voice_chat_id']).name
        hour, _ = group['start_time'].split(':')
        time = ':'.join((hour, '30'))
        members = await loop.run_in_executor(None, db.get_all_students_for_group, group['role_id'])
        database[group_name] = {'days': group['days'].split(', '), 'time': time, 'channel_id': group['channel_id'], 'members': [{'name': i['name'], 'id': i['discord_id']} for i in members]}
    # database = {'Занятие ПН-СР 19:00': {'days': ['monday', 'wednesday', 'tuesday'], 'time': '17:13', 'channel_id': 1120389774243549247, 'members': [{'name': 'Farfur', 'id': 306436605541875724}, {'name': 'Ivan', 'id': 691174001451466772}]}} # Здесь нужно получить данные именно в таком формате
    schedule.clear('check')
    # guild = bot.get_guild(int(SERVER_ID))
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
    # schedule.every().minute.do(asyncio.run_coroutine_threadsafe(update(), bot.loop))
    # pprint(schedule.jobs)



async def send_info():
    # schedule.every(10).seconds.do(lambda channel: asyncio.run_coroutine_threadsafe(job(channel), bot.loop), channel)
    loop = asyncio.get_event_loop()
    guild = bot.get_guild(int(SERVER_ID))
    groups = await loop.run_in_executor(None, db.get_all_groups)
    database = dict()
    for group in groups:
        group_name = guild.get_channel(group['voice_chat_id']).name
        hour, _ = group['start_time'].split(':')
        time = ':'.join((hour, '30'))
        members = await loop.run_in_executor(None, db.get_all_students_for_group, group['role_id'])
        database[group_name] = {'days': group['days'].split(', '), 'time': time, 'channel_id': group['channel_id'], 'members': [{'name': i['name'], 'id': i['discord_id']} for i in members]}
    # print('LOCAL')
    # database = {'Занятие ПН-СР 19:00': {'days': ['monday', 'wednesday', 'tuesday'], 'time': '17:13', 'channel_id': 1120389774243549247, 'members': [{'name': 'Farfur', 'id': 306436605541875724}, {'name': 'Ivan', 'id': 691174001451466772}]}} # Здесь нужно получить данные именно в таком формате
    # schedule.clear()
    # guild = bot.get_guild(int(SERVER_ID))
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
    # schedule.every().minute.do(lambda: asyncio.run_coroutine_threadsafe(update(), bot.loop))
    # schedule.every().minute.do(asyncio.run_coroutine_threadsafe(update(), bot.loop))
    # print(len(schedule.jobs))

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


@bot.command(name='echo') # Заглушка! В дальнейшем, можно добавить команду и использовать код
async def help(ctx):
    loop = asyncio.get_event_loop()
    guild = bot.get_guild(int(SERVER_ID))
    groups = await loop.run_in_executor(None, db.get_all_groups)
    database = dict()
    for group in groups:
        group_name = guild.get_channel(group['voice_chat_id'])
        print(group_name)

@bot.command() # Функция регистрации. Проверяет все данные и отправляет обратную связь
async def reg(ctx, name=None, last_name=None, group_id=None, *, devman_url=None):
    loop = asyncio.get_running_loop()
    if name is None or last_name is None or group_id is None or devman_url is None:
        await ctx.reply('Мне кажется, что ты какой-то из аргументов не указал:( Проверь!')
        return
    author = ctx.message.author
    students_ids = await loop.run_in_executor(None, db.get_all_students_ids)
    if author.id in students_ids:
        await ctx.reply('### Ты уже зарегестрирован в базе данных!\nЕсли ты хочешь изменить свою групппу или думаешь, что я ошибся, то обратись к Михаилу!')
        return
    all_groups = await loop.run_in_executor(None, db.get_all_groups_ids)
    guild = bot.get_guild(int(SERVER_ID))
    if int(group_id) > len(all_groups):
        await ctx.reply('Такой группы не существует! Проверь правильность ввода данных')
        return
    role = guild.get_role(all_groups[int(group_id) - 1])
    user = guild.get_member(author.id)
    await user.add_roles(role)
    await loop.run_in_executor(None, db.add_student, (author.id, f'{name} {last_name}', role.id, devman_url, 0))
    await ctx.reply(f'Теперь ты назначен в группу {role.name}')


def main():
    bot.run(os.getenv('DISCORD_TOKEN'))


if __name__ == '__main__':
    main()