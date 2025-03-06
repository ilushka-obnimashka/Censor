## Установка

1. Клонируйте репозиторий:
```bash
    git clone https://github.com/ilushka-obnimashka/Censor.git
    cd Censor
```
2. Переключитесь на нужную ветку proof-of-concept:
```bash
   git checkout proof-of-concept
```
3. Создайте виртуальное окружение:
```bash
   python3 -m venv <name>
```
4. Активируйте виртаульное окружение:
   * 1.1 Для Linux, macOS, Windows (WSL):
   ```bash
   source <name>/bin/activate
   ```
   * 1.1 Windows:
   ```bash
   <name>\Scripts\activate
   ```

> [!Note]
> **Внимание:** 
> После активации окружения ваш терминал или командная строка изменятся, и вы увидите имя виртуального окружения в начале строки:
> ```bash
> (name) user@comp:~$
> ```

5. Установка пакетов и зависимостей:
   ```bash
      pip install -r requirements.txt
   ```

6. Выберите интепретатор в среде разработки:
▎PyCharm:
   1. Откройте настройки проекта (File -> Settings или Ctrl + Alt + S).
   2. Перейдите в раздел Project: <your_project_name> -> Python Interpreter. 
   3. Выберите Add Interpretator -> Add Local Interpretator -> Select existing
   4. Выберите Type: Python. 
   5. Выберите Python path: <project_path>/venv/bin/python3.10
   6. Нажмите OK, чтобы применить изменения.
      (Подробнее https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html#add_local_interpreters)

7. Запустите код

## Для разработчиков:

1. Общая команда установки пакета:
```bash
(name) user@comp:~$ pip install <имя_пакета>
```
2. Общая команда установки пакета конкретной версии:
```bash
(name) user@comp:~$ pip install <имя_пакета==2.5.0>
```
3. Проверка установленных пакетов внутри виртуальной среды:
```bash
(name) user@comp:~$ pip freeze
```
4. Генерация файла зависимостей:
```bash
(name) user@comp:~$ pip freeze > requirements.txt
```

5. Деактивация виртуалього окружения
```bash
   (name) user@comp:~$ pip deactivate
```
> [!Note]
> **Внимание:** 
> После деактивации окружения ваш терминал или командная строка примет прежний вид.
