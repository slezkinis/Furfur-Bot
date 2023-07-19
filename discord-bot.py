import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import schedule

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
            await user.send('Привет! Тебя не было на занятиях! Ай-ай-ай!', tts=True)
        else:
            was.append(user.name)
    await channel.send(f'Сегодня на занятиях были: {", ".join(was)}')


async def update():
    database = {'Занятие ПН-СР 19:00': {'days': ['monday', 'wendsday'], 'time': '19:32', 'channel_id': 1120389774243549247}} # Здесь нужно получить данные именно в таком формате
    schedule.clear()
    for name, data in database.items():
        channel = bot.get_channel(data['channel_id'])
        for date in data['days']:
            if date == 'monday':
                schedule.every().monday.at(data['time']).do(lambda channel, name: asyncio.run_coroutine_threadsafe(job(channel, name), bot.loop), channel, name)
            elif date == 'tuesday':
                schedule.every().tuesday.at(data['time']).do(lambda channel, name: asyncio.run_coroutine_threadsafe(job(channel, name), bot.loop), channel, name)
            elif date == 'wednesday':
                schedule.every().wednesday.at(data['time']).do(lambda channel, name: asyncio.run_coroutine_threadsafe(job(channel, name), bot.loop), channel, name)
            elif date == 'thursday':
                schedule.every().thursday.at(data['time']).do(lambda channel, name: asyncio.run_coroutine_threadsafe(job(channel, name), bot.loop), channel, name)
            elif date == 'friday':
                schedule.every().friday.at(data['time']).do(lambda channel, name: asyncio.run_coroutine_threadsafe(job(channel, name), bot.loop), channel, name)
            elif date == 'saturday':
                schedule.every().saturday.at(data['time']).do(lambda channel, name: asyncio.run_coroutine_threadsafe(job(channel, name), bot.loop), channel, name)
            elif date == 'sunday':
                schedule.every().sunday.at(data['time']).do(lambda channel, name: asyncio.run_coroutine_threadsafe(job(channel, name), bot.loop), channel, name)
    schedule.every(24).hours.do(lambda: asyncio.run_coroutine_threadsafe(update(), bot.loop))


async def send_info():
    # schedule.every(10).seconds.do(lambda channel: asyncio.run_coroutine_threadsafe(job(channel), bot.loop), channel)
    database = {'Занятие ПН-СР 19:00': {'days': ['monday', 'wednesday', 'tuesday'], 'time': '17:13', 'channel_id': 1120389774243549247, 'members': [{'name': 'Farfur', 'id': 306436605541875724}, {'name': 'Ivan', 'id': 691174001451466772}]}} # Здесь нужно получить данные именно в таком формате
    schedule.clear()
    guild = bot.get_guild(int(SERVER_ID))
    for name, data in database.items():
        channel = bot.get_channel(data['channel_id'])
        # print('; '.join(data['members']))
        for date in data['days']:
            if date == 'monday':
                schedule.every().monday.at(data['time']).do(lambda channel, guild, members, name: asyncio.run_coroutine_threadsafe(job(channel, guild, members, name), bot.loop), channel, guild, data['members'], name)
            elif date == 'tuesday':
                schedule.every().tuesday.at(data['time']).do(lambda channel, guild, members, name: asyncio.run_coroutine_threadsafe(job(channel, guild, members, name), bot.loop), channel, guild, data['members'], name)
            elif date == 'wednesday':
                schedule.every().wednesday.at(data['time']).do(lambda channel, guild, members, name: asyncio.run_coroutine_threadsafe(job(channel, guild, members, name), bot.loop), channel, guild, data['members'], name)
            elif date == 'thursday':
                schedule.every().thursday.at(data['time']).do(lambda channel, guild, members, name: asyncio.run_coroutine_threadsafe(job(channel, guild, members, name), bot.loop), channel, guild, data['members'], name)
            elif date == 'friday':
                schedule.every().friday.at(data['time']).do(lambda channel, guild, members, name: asyncio.run_coroutine_threadsafe(job(channel, guild, members, name), bot.loop), channel, guild, data['members'], name)
            elif date == 'saturday':
                schedule.every().saturday.at(data['time']).do(lambda channel, guild, members, name: asyncio.run_coroutine_threadsafe(job(channel, guild, members, name), bot.loop), channel, guild, data['members'], name)
            elif date == 'sunday':
                schedule.every().sunday.at(data['time']).do(lambda channel, guild, members, name: asyncio.run_coroutine_threadsafe(job(channel, guild, members, name), bot.loop), channel, guild, data['members'], name)
    schedule.every(24).hours.do(lambda: asyncio.run_coroutine_threadsafe(update(), bot.loop))
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
    pass


@bot.command(name='echo') # Заглушка! В дальнейшем, можно добавить команду и использовать код
async def help(ctx):
    guild = bot.get_guild(int(SERVER_ID))
    await ctx.reply('### Привет! Добро пожаловать в мир Python:) Вот доступные группы:\n<группы>\nЧтобы зарегистрироваться введи команду:\n/reg ***<Имя>*** ***<Фамилия>*** ***<ID группы (смотри сверху)>*** ***<ссылка на твой Devman профиль>***')


@bot.command() # Функция регистрации. Проверяет все данные и отправляет обратную связь
async def reg(ctx, name=None, last_name=None, group_id=None, *, devman_url=None):
    if name is None or last_name is None or group_id is None or devman_url is None:
        await ctx.reply('Мне кажется, что ты какой-то из аргументов не указал:( Проверь!')
        return
    guild = bot.get_guild(int(SERVER_ID))
    role = guild.get_role(1123656426519265311)
    author = ctx.message.author
    user = guild.get_member(author.id)
    await user.add_roles(role)
    # TODO Здесь нужно добавить в базу данных пользователя. Также добавить проверку, зареган ли пользователь
    await ctx.reply(f'Теперь ты назначен в группу {role.name}')


# @bot.command(name='test') # Тест!
# async def help(ctx):
#     guild = bot.get_guild(int(SERVER_ID))
#     channel = guild.get_channel(1120389836730286110)
#     with open('photo.png', 'wb') as file:
#         channel.members[0].avatar.save(file)
#     # await ctx.reply(f'Вот список тех пользователей, которые находятся в голосовом канале {guild.voice_channels[0].name}: {", ".join([i.name for i in guild.voice_channels[0].members])}')


def main():
    bot.run(os.getenv('DISCORD_TOKEN'))


if __name__ == '__main__':
    main()