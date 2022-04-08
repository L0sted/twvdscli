twvdscli
====

Это утилита для управления серверами и сервисами в Timeweb Cloud.

# Установка

Потребуются пакеты typer, prettytable, requests. Ставим их из файла:

```commandline
pip3 install --user -r requirements.txt
```

# Запуск

При первом запуске утилита спросит логин и пароль, после чего запишет их в ~/.config/twvdscli.ini в формате base64 через знак ":".