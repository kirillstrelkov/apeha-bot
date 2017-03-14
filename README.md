### Бот для игры http://www.apeha.ru/

### WINDOWS используя exe файл
##### УСТАНОВКА КОМПОНЕНТОВ:
0. Установите Google Chrome если не установлен
1. Скачайте драйвер для Google Chrome
 1. chromedriver: https://sites.google.com/a/chromium.org/chromedriver/downloads (**для Windows существует только один chromedriver - 32-битный**)
 2. распакуйте и поместить 'chromedriver.exe' в папку пользователя(пример: C:\Users\max)

##### ЗАПУСК БОТА
**NB**: Бот не поддерживает Flash - необходимо отключить Flash пароль в Арене

1. Скачать архив с приложением: [apehabot_ui_win64.zip](/build/apehabot_ui_win64.zip)
2. Распаковать
3. Запустить **apehabot_ui.exe**
4. Ввести ник и пароль
5. Выбрать уровень астрала
6. Выбрать тактику блокировки - рэндомно или определенные части тела
7. Нажать "Запустить бота"

### WINDOWS используя Python
##### УСТАНОВКА НЕОБХОДИМЫХ КОМПОНЕНТОВ:
1. Скачать и установить Python **2.7**(NB: При установке выбрать все компоненты):
https://www.python.org/downloads/
2. Скачать и запустить:
https://bootstrap.pypa.io/get-pip.py
3. Открыть коммандную строку(cmd.exe) и запустить комманду:
`C:\Python27\Scripts\pip.exe install selenium`
4. Скачать и установить wxPython для 32-bit Python 2.7:
http://www.wxpython.org/download.php

**NB**:
В случае обновления браузера необходимо обновить **selenium**:

Открыть коммандную строку(cmd.exe) и запустить комманду:
`C:\Python27\Scripts\pip.exe install -U selenium`

Если обновился Google Chrome иногда необходимо обновить chromedriver

##### ЗАПУСК БОТА

0. Скачать [архив с кодом](https://github.com/kirillstrelkov/apeha-bot/archive/master.zip) и распаковать
1. Запустить **apehabot_ui.py** который находится в src/apeha/bot/ui/
2. Ввести ник и пароль
3. Выбрать уровень астрала
4. Выбрать тактику блокировки - рэндомно или определенные части тела
5. Нажать "Запустить бота"

### РАБОТА БОТА

1. Проверить вещи игрока(раздеться и одеться)
2. Бесконечно пробывать:
    1. Проверить травмы пользователя(Бот сам будет лечить травмы если есть абилки или свитки)
    2. Проверить астрал пользователя и имя клана
    3. Если надо то восстановиться в замке
    4. Идти в заявку - если есть заявки то вступить или создать свою заявку
    5. Идти обратно в замок
    6. Ждать начало боя
    7. Бой начался, пока жив:
        1. Применить тактику к клонам если надо
        2. Войти в астрал если надо
        3. Поставить клона либо восстановиться
        4. Заблокироваться
        5. Ждать окончания раунда
    8. Ждать окончания боя

### РЕШЕНИЕ ПРОБЛЕМ
Если обновился Google Chrome иногда необходимо обновить chromedriver

Если не запускается браузер - проверить в **Task Manager** работают ли браузеры и остановить их:
* firefox.exe
* chromdriver.exe
* chrome.exe
