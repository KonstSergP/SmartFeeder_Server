# SmartFeeder_Server

SmartFeeder - это программа, реализующая функциональность сервера для беличьей кормушки с автоматическим обнаружением белок и человеческих рук и системой удаленного управления. Программа управляет соединениями между кормушками и мобильными приложениями, обрабатывает потоковое видео, хранит и предоставляет записанные видео.

[Программа кормушки](https://github.com/KonstSergP/SmartFeeder_Feeder)

Используемые библиотеки:
- Flask-SocketIO: Коммуникация в реальном времени между кормушками и клиентами
- SQLite: База данных для хранения кормушек и пользователей
- Gunicorn/Eventlet: WSGI-сервер с поддержкой Socket.IO



### Установка
```
git clone https://github.com/KonstSergP/SmartFeeder_Server.git

cd SmartFeeder_Server

make install
```

#### Для использования трансляций необходимо установить nginx
```
sudo apt install
sudo apt upgrade

wget https://nginx.org/download/nginx-1.24.0.tar.gz
tar zxf nginx-1.24.0.tar.gz
git clone https://github.com/arut/nginx-rtmp-module.git

cd nginx-1.24.0
./configure —add-module=./nginx-rtmp-module
make
make install
cd ..
sudo ln -f app/settings/nginx.conf /usr/local/nginx/conf/nginx.conf
```


### Запуск

```
# Запустить nginx
sudo /usr/local/nginx/sbin/nginx

# Запустить
make run

# Запустить с использованием gunicorn
make preview

# Запустить вручную
python main.py
```


#### HTTP эндпоинты
- GET /feeders - Список всех подключенных кормушек
- GET /videos - Список всех сохраненных видео
- GET /video/\<path> - Получить конкретный видеофайл
- POST /upload - Загрузить видеофайл с кормушки
#### События Socket.IO
- connect - Подключение кормушки или клиента
- disconnect - Обработка отключения
- stream start - Начать просмотр видеопотока с кормушки
- stream stop - Прекратить просмотр видеопотока
- stream stopped - вызывает сервер, когда видеопоток был прерван


### Структура проекта

```
SmartFeeder_Server/
├── app/                      # Основной код приложения
│   ├── settings/             # Конфигурационные файлы
│   ├── storage/              # База данных и хранилище видео
│   ├── connection_handler.py # Управление подключениями устройств
│   ├── http_controllers.py   # HTTP API эндпоинты
│   ├── server.py             # Создание экземпляра сервера
│   └── socket_controllers.py # Обработчики событий Socket.IO
├── tests/                    # Тесты
├── main.py                   # Главная точка входа
├── Makefile                  # Команды сборки и запуска
└── requirements.txt          # зависимости
```

### Разработка и тестирование
```
# Запуск тестов с отчетом о покрытии
make coverage

# Очистка временных файлов
make clean

# Полная очистка, включая виртуальное окружение
make deepclean
```

### Настройка
Настройки хранятся в файлах settings.toml и gunicorn.py и могут быть изменены.
