Auth System — собственная система аутентификации и авторизации
Данный проект представляет собой backend-приложение, реализующее полный цикл аутентификации и авторизации пользователей с собственной системой разграничения доступа на основе ролей (RBAC) и разрешений (permissions).
Решение не использует готовые «коробочные» механизмы фреймворков (Django/DRF и т.п.) — вся логика разработана самостоятельно в соответствии с требованиями технического задания.

Основные возможности
Регистрация, логин, логаут пользователя (email + пароль)

Обновление профиля (ФИО, email) авторизованным пользователем

Мягкое удаление аккаунта (is_active=False) с возможностью удаления как самим пользователем, так и администратором

JWT-аутентификация (access + refresh токены) с проверкой типа токена

Собственная RBAC: роли (admin, user, viewer) и разрешения (например, users:read, users:delete)

Администрирование:

просмотр всех пользователей (включая неактивных)

назначение/изменение ролей пользователям

просмотр списка ролей и разрешений

получение статистики системы

Автоматическое создание начальных данных (роли и разрешения) при первом запуске

Логирование всех значимых действий (через loguru) с ротацией файлов

Стек технологий
Компонент	Технология
Web framework	FastAPI
ORM	Tortoise ORM
Database	PostgreSQL
Аутентификация	JWT (python-jose) + passlib (bcrypt)
Валидация данных	Pydantic V2
Логирование	loguru
ASGI сервер	Uvicorn
Управление секретами	Pydantic Settings + .env файл
Схема базы данных
Система состоит из трёх основных таблиц и двух промежуточных (многие-ко-многим).

Таблица users
Поле	Тип	Описание
id	UUID (PK)	Уникальный идентификатор
email	string(255)	Email, уникальный, индекс
password_hash	string(255)	Хеш пароля (bcrypt)
first_name	string(100)	Имя
last_name	string(100)	Фамилия
patronymic	string(100)	Отчество (опционально)
is_active	boolean	Активен (мягкое удаление)
is_verified	boolean	Подтверждён ли email (задел на будущее)
is_superuser	boolean	Флаг суперпользователя (резерв)
created_at	datetime	Дата создания
updated_at	datetime	Дата обновления
deleted_at	datetime	Дата мягкого удаления (опционально)
Таблица roles
Поле	Тип	Описание
id	Int (PK)	
name	string(50)	Уникальное имя роли
description	text	Описание
is_active	boolean	Активна ли роль
created_at	datetime	
Таблица permissions
Поле	Тип	Описание
id	Int (PK)	
name	string(100)	Человекочитаемое имя
code	string(100)	Уникальный код (например, users:read)
description	text	
module	string(50)	Модуль (users, resources и т.д.)
created_at	datetime	
Связи многие-ко-многим
user_roles – связывает users и roles (пользователь может иметь несколько ролей)

role_permissions – связывает roles и permissions (роль может содержать несколько разрешений)

Все связи реализованы через промежуточные таблицы с использованием ManyToManyField Tortoise ORM.

Система разграничения прав (собственная RBAC)
Принцип работы
При регистрации пользователь получает роль user по умолчанию.

Роль admin имеет все права (без явного назначения разрешений) — это зашито в логике check_permission.

Каждое действие (доступ к эндпоинту) проверяется через зависимости FastAPI:

Depends(get_current_user) – проверяет JWT и возвращает объект User

Depends(require_roles(["admin"])) – проверяет наличие одной из перечисленных ролей

Depends(check_permission("users:read")) – проверяет наличие конкретного разрешения (с учётом привилегии admin)

Доступные роли (создаются автоматически)
Роль	Описание
admin	Полный доступ ко всем ресурсам
user	Обычный пользователь
viewer	Только чтение (задел на будущее)

name	code	module
Просмотр пользователей	users:read	users
Создание пользователей	users:create	users
Удаление пользователей	users:delete	users
Просмотр ресурсов	resources:read	resources
Администратор может добавлять/изменять роли и разрешения через API (эндпоинты администрирования).

API эндпоинты
Базовый префикс: /api/v1
Документация OpenAPI доступна после запуска по адресу: http://localhost:8000/docs

Аутентификация и профиль (/auth)
Метод	Эндпоинт	Описание	Требуемые права
POST	/auth/register	Регистрация нового пользователя	публичный
POST	/auth/login	Вход, получение access + refresh токенов	публичный
POST	/auth/logout	Выход (логгирование, клиент удаляет токены)	get_current_user
GET	/auth/me	Получить свой профиль	get_current_user
PUT	/auth/me	Обновить свои данные (ФИО, email)	get_current_user
POST	/auth/refresh	Обновить access-токен по refresh-токену	публичный (с refresh)
Управление пользователями (/users)
Метод	Эндпоинт	Описание	Требуемые права
GET	/users/	Список активных пользователей (с пагинацией)	users:read
GET	/users/{user_id}	Профиль пользователя по ID	get_current_user
DELETE	/users/{user_id}	Мягкое удаление (владелец или users:delete)	владелец или users:delete
Администрирование (/admin) – только роль admin
Метод	Эндпоинт	Описание
GET	/admin/users	Список всех пользователей (вкл. неактивных)
PUT	/admin/users/{user_id}/role?role_name=	Назначить новую роль пользователю
GET	/admin/roles	Список всех ролей
GET	/admin/permissions	Список всех разрешений
GET	/admin/stats	Статистика (кол-во пользователей, ролей, разрешений)
Установка и запуск
Требования
Python 3.9+

PostgreSQL (локально или через Docker)

Git

1. Клонирование репозитория
bash
git clone https://github.com/urHATuIILe/fastapi-auth-tt.git
cd fastapi-auth-tt
2. Настройка виртуального окружения
bash
python -m venv .venv
source venv/bin/activate      # Linux/Mac
.venv\Scripts\activate         # Windows
3. Установка зависимостей
bash
pip install -r requirements.txt
(если файла requirements.txt нет – установите вручную: fastapi uvicorn tortoise-orm passlib[bcrypt] python-jose pydantic-settings loguru asyncpg)

4. Настройка переменных окружения
Создайте файл .env в корне проекта:

env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=auth_system

JWT_SECRET=ваш_очень_длинный_секретный_ключ_минимум_32_символа
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

DEBUG=True
Для production укажите DEBUG=False и используйте надёжный JWT_SECRET.

5. Запуск приложения
bash
python run.py
После запуска будут автоматически:

созданы таблицы в БД (если DEBUG=True)

заполнены начальные роли (admin, user, viewer) и разрешения

6. Создание первого администратора
Зарегистрируйте обычного пользователя через API /auth/register с любым email, например admin@test.com(уже есть готовый код с этим юзером в make_admin.py).
Затем выполните скрипт:

bash
python make_admin
Скрипт назначит пользователю с email admin@test.com роль admin.
Теперь вы можете использовать его для доступа к админским эндпоинтам.

Тестирование и примеры
1. Регистрация
bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "StrongPass123!",
    "password_confirm": "StrongPass123!",
    "first_name": "Иван",
    "last_name": "Петров",
    "patronymic": "Иванович"
  }'
2. Вход
bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "StrongPass123!"}'
Ответ: {"access_token": "...", "refresh_token": "...", "token_type": "bearer", "expires_in": 1800}

3. Получение списка пользователей (требуется users:read)
bash
curl -X GET http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer <access_token>"
4. Админ: назначить роль
bash
curl -X PUT "http://localhost:8000/api/v1/admin/users/123e4567-e89b-12d3-a456-426614174000/role?role_name=admin" \
  -H "Authorization: Bearer <admin_access_token>"
5. Мягкое удаление своего аккаунта
bash
curl -X DELETE http://localhost:8000/api/v1/users/123e4567-... \
  -H "Authorization: Bearer <access_token>"
Все эндпоинты интерактивно документированы в Swagger: http://localhost:8000/docs

Заключение
Разработанное приложение полностью соответствует требованиям технического задания:

✅ Реализована собственная система аутентификации (JWT, регистрация, логин, логаут, обновление профиля)

✅ Мягкое удаление с флагом is_active=False

✅ Собственная система разграничения доступа (RBAC) с ролями и разрешениями, гибкими проверками через зависимости FastAPI

✅ API для администратора по изменению прав пользователей (назначение ролей, просмотр ролей/разрешений)

✅ 401 / 403 ошибки при отсутствии аутентификации или недостаточных правах

✅ Чёткое разделение между аутентификацией (кто ты) и авторизацией (что тебе можно)

✅ Использован стек FastAPI + PostgreSQL (с асинхронным ORM Tortoise)

Проект готов к локальному развёртыванию и может служить основой для более крупных систем с тонкой настройкой прав доступа.

