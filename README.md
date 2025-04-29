# 🛡️ Censor — Инструмент автоматической цензуры медиа

**Censor** — это система, предназначенная для автоматической цензуры аудио, изображений и видео. Она обнаруживает запрещённые объекты и фразы и скрывает их с помощью блюра, пикселизации или подавления звука.

---

## 🧰 Возможности

| Тип контента | Поддержка цензуры | Метод                  |
|--------------|-------------------|------------------------|
| 🎧 Аудио      | ✅ | Запикивание            |
| 🖼️ Изображения | ✅ | Пикселизация           |
| 🎞️ Видео      | ✅ | По кадрам, с трекингом |

---

## 🗂️ Структура проекта

```dir
Censor/
├── AudioProcessingTool/
│   ├── resources/
│   │   ├── vosk-model
│   │   └── censor_sound.mp3
│   ├── audio2text_timestamps.py
│   ├── gigachat_integration.py
│   ├── speech2censored.py
│   ├── video2audio.py
│   └── README.md
├── MediaProcessingTool/
│   ├── models/
│   │   ├── nudenet.pt
│   │   └── cigarette.pt
│   ├── censor_models.py
│   ├── detect_and_blur.py
│   └── README.md
├── temp_file_manager.py
├── requirements.txt
└── README.md  ← (этот файл)

```

---

## ⚙️ Установка и запуск

### 🔽 1. Клонируем репозиторий
```bash
git clone https://github.com/ilushka-obnimashka/Censor.git
cd Censor
git checkout master
```

### 🐍 2. Создаём и активируем виртуальное окружение
```bash
python -m venv venv

# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

> [!Note]
> **Внимание:** 
> После активации окружения ваш терминал или командная строка изменятся, и вы увидите имя виртуального окружения в начале строки:
> ```bash
> (name) user@comp:~$
> ```

### 📦 3. Устанавливаем зависимости
```bash
pip install -r requirements.txt
```

---

## 🎧 Модуль обработки аудио
### 🔧 Подготовка
1. Перейди в директорию:
```bash
cd AudioProcessingTool
```
2. Распакуй модель VOSK:
```bash
unzip resources/vosk-model-small-ru-0.22.zip -d resources/
```

### ▶️ Запуск
```bash
python resources/speech2censored.py audio_example.wav
```
👉 Получишь файл `censor_audio_example.wav` с запиканной нецензурной лексикой.  
📄 Подробности: [Audio README](AudioProcessingTool/README.md)

---

## 🖼️ Модуль обработки изображений и видео
### 🔧 Подготовка
1. Перейди в директорию:
```bash
cd VisualProcessingTool
```
2. Распакуйте модели:
```bash
unzip models.zip
```

### ▶️ Пример обработки видео
```bash
python VisualProcessingTool/models/detect_and_blur.py \
  parse input.mp4 \
  --black-list cigarette --black-list MALE_GENITALIA_EXPOSED \
  --pixelation \
  --output-path output.mp4
```
👉 Получишь файл `output.mp4` с пикселизированными нежелательными обьектами.  
📄 Поддерживаемые классы и детали в [Media README](VisualProcessingTool/README.md)

---

## 🧪 Полезные команды разработчику

| Операция | Команда |
|----------|---------|
| Установка пакета | `pip install <имя>` |
| Определённая версия | `pip install <имя==версия>` |
| Список зависимостей | `pip freeze` |
| Обновление `requirements.txt` | `pip freeze > requirements.txt` |
| Деактивация окружения | `deactivate` |

> [!Note]
> **Внимание:** 
> После деактивации окружения ваш терминал или командная строка примет прежний вид.


---

## 👥 Авторы проекта

- 🔧 Зеленков Никита
- 🧠 Трушкин Илья
- 🧮 Комаревцев Ян
- 🎓 Наставник: Максим Емельянов

---

## 📌 Цель проекта

Создать удобный инструмент для автоматической модерации медиаконтента:  
**телеканалы, блогеры, онлайн-курсы, образовательные платформы — это для вас!**
