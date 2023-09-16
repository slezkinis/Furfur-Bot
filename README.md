# Furfur-Bot
 
Это бот для автоматической прверки посещаемости учеников и автоматического выбора отработок.

### Как установить

1. Создайте файл .env и добавьте токен бота, полученный с сайта [Discord API](https://discord.com/developers/applications). Также добавьте `SERVER_ID`, `ADMIN_ROLE_ID` и `GOOGLE_SHEET_TOKEN_PATH` - путь до Gooogle токена. Вот пример:
```
DISCORD_TOKEN=[TOKEN]
SERVER_ID = 111111111111
ADMIN_ROLE_ID = 222222222222
GOOGLE_SHEET_TOKEN_PATH='token.json'
```

2. Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```powershell
pip install -r requirements.txt
```


### Как запустить

Зайдите в терминал и запустите файл `discord-bot.py`:
```powershell
python3 discord-bot.py
```


Бот запущен:)
