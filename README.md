# AviaBlog

Добро пожаловать в AviaBlog! Этот веб-сайт предоставляет возможность добавлять и просматривать информацию о совершенных полетах.

## О проекте

AviaBlog - это веб-сайт, разработанный для фанатов авиации, пилотов и пассажиров, которые хотят делиться информацией о своих полетах. Здесь вы можете добавлять записи о полетах, включая детали вылета и прилета, а также просматривать и комментировать записи других пользователей.

## Функциональность

- Регистрация и аутентификация пользователей c помощью сессий и кук
- Добавление новых записей о полетах
- Просмотр списка совершенных полетов
- Подробная информация о каждом полете
- Возможность удалять и редактировать свой полет
- Возможность комментировать полеты других пользователей (будет в будущем, если руки дойдут)
- Возможность получения своего полета в PDF-формате (будет в будущем, если руки дойдут)

## Технологии

Проект AviaBlog разработан с использованием следующих технологий:

- Django: веб-фреймворк для разработки веб-приложений на языке Python.
- PostgreSQL: реляционная база данных для хранения информации о полетах и пользователях.
- HTML/CSS: используются для создания пользовательского интерфейса и стилизации страниц.
- JavaScript: добавляет интерактивность и динамическое поведение на клиентской стороне.
- Docker: контейнеризация приложения и инфраструктуры, позволяющая легко развертывать и масштабировать проект, а также обеспечивать изоляцию и безопасность.
- Gunicorn: стабильный WSGI-сервер для запуска Django приложения, обеспечивающий быструю обработку запросов и поддержку многопоточности.
- Nginx: высокопроизводительный веб-сервер и обратный прокси, используемый для балансировки нагрузки и обеспечения безопасности приложения.

Проект AviaBlog можно запустить как на локальном хосте, так и в контейнерах Docker с использованием Nginx и Gunicorn.

## Обычная установка и запуск на локальном хосте

1. Перейдите в директорию с вашими проектами.
2. Склонируйте репозиторий на свой локальный компьютер:

```shell
# Windows
> git clone https://github.com/semyonnakrokhin/aviablog_django_docker.git
```

3. Перейдите в каталог проекта:

```shell
# Windows
> cd aviablog_django_docker
```

4. Создайте виртуальное окружение python. Придумайте ему название, например venv_aviablog:

```shell
# Windows
> python -m venv venv_aviablog
```

5. Активируйте виртуальное окружение (не забудьте изменить имя виртуального окружения на свое):

```shell
# Windows
> .\venv_aviablog\Scripts\activate
```

6. Перейдите в корневой каталог Django-сайта:

```shell
# Windows
> cd app
```

7. Установите зависимости:

```shell
# Windows
> pip install -r requirements.txt
```

8. Установите PostgreSQL или убедитесь, что PostgreSQL установлен на вашей машине. Вы можете загрузить и установить PostgreSQL с официального веб-сайта.
9. Создайте новую базу данных PostgreSQL для вашего проекта (убедитесь, что процесс postgres запущен).

- Подключитесь к PostgreSQL (при помощи какого либо клиента) используя стандартного суперпользователя и стандартной базы данных
- Создайте новую базу данных (например, aviablog_db):

```sql
CREATE DATABASE aviablog_db;
```

- Если желаете, можете создать нового пользователя (например aviator) и придумать ему пароль (например qwerty), от которого будете ходить в эту бд:

```sql
CREATE USER aviator WITH PASSWORD 'qwerty';
```

- Дайте новому пользователю все привилегии для работы с базой данных:

```sql
GRANT ALL PRIVILEGES ON DATABASE aviablog_db TO aviator;
```

10. Создайте в корневом каталоге файл .env и заполните его переменными для доступа к бд. Имена переменных не менять, значения вставьте свои:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=aviablog_db
DB_USER=aviator
DB_PASSWORD=qwerty
```
</code></pre>

11. Находясь в корневом каталоге, выполните миграции:

```shell
# Windows
> python manage.py migrate
```

12. В файле fixtures.json лежат тестовые данные для бд. Загрузите их в бд, используя команду:

```shell
# Windows
> python manage.py loaddata fixture.json
```

13. Запустите локальный сервер:

```shell
# Windows
> python manage.py runserver
```
Откройте веб-браузер и перейдите по адресу http://localhost:8000 для доступа к AviaBlog.

## Запуск в контейнерах Docker с использованием Nginx и Gunicorn

1. Перейдите в директорию с вашими проектами.
2. Склонируйте репозиторий на свой локальный компьютер:

```shell
# Linux
> git clone https://github.com/semyonnakrokhin/aviablog_django_docker.git
```

3. Перейдите в каталог проекта:

```shell
# Linux
> cd aviablog_django_docker
```

4. В этой директории создайте файл .env.db со следующим содержанием для создания базы данных и пользователя в контейнере с бд:

```dotenv
POSTGRES_USER=aviator
POSTGRES_PASSWORD=qwerty
POSTGRES_DB=aviablog_db
```

5. В этой же директории создайте файл .env со следующими переменными. Переменные DEBUG, SECRET_KEY, DJANGO_ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, DB_ENGINE, DB_HOST, DB_PORT скопировать из примера и не менять. Значения остальных переменных взять из .env.db

```dotenv
DEBUG=0
SECRET_KEY=django-insecure-kq$tg_*$dolb@eog(zd@993#xtyl*l4%i*c64bi6)f8nlvgn*_
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
CSRF_TRUSTED_ORIGINS=https://localhost:1337 http://localhost:1337
DB_ENGINE=django.db.backends.postgresql
DB_HOST=db
DB_PORT=5432
DB_NAME=aviablog_db
DB_USER=aviator
DB_PASSWORD=qwerty
```

6. Выполните команду находясь в корневой директории проекта:

```shell
# Linux
> docker-compose up -d --build
```
Откройте веб-браузер и перейдите по адресу http://localhost:1337 для доступа к AviaBlog.

7. (Опционально) Для того, чтобы наполнить бд вашими тестовыми данными, выполните команды:

- Для запущенного контейнера aviablog_django_docker-web-1 (у вас может быть другое название) выполните команду для сохранения данных из бд в json-файле

```shell
# Linux
> docker exec aviablog_django_docker-web-1 python manage.py dumpdata flights.AircraftType flights.Airline flights.Airframe flights.FlightInfo flights.Flight flights.UserTrip flights.TrackImage flights.Meal auth.User --indent 2 -o /home/app/web/fixture.json
```

- Скопируйте полученный json-файл к себе на локальный хост:

```shell
# Linux
> docker cp aviablog_django_docker-web-1:/home/app/web/fixture.json $(pwd)/app/fixture.json
```

- Убедитесь, что кодировка полученного файла utf-8:

```shell
# Linux
> file -i app/fixture.json
```

8. Для остановки контейнеров выполните команду:

```shell
# Linux
> docker-compose down
```


## Вклад
Если вы хотите внести свой вклад в AviaBlog, пожалуйста, ознакомьтесь с CONTRIBUTING.md для получения дополнительной информации о том, как начать.

## Авторы
Семен Накрохин
2206095@gmail.com

## Лицензия
Этот проект распространяется под лицензией MIT. Подробности смотрите в файле LICENSE.


