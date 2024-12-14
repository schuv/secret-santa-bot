<br>
<p align="center">
    <img align="center" src="images/logo.png">
    <h3 align="center">Тайный Санта</h3>
    <p align="center">Бот для проведения тайного санты</p>
</p>
<br>


# О проекте
Отличная возможности провести тайного санту прямо через Телеграмм с удобным интерфейсом и незамысловатой логикой. С помощью **открытого кода** у вас есть возможность изменить некоторые аспекты и разместить бота прямо у себя на сервере

Создан для некоммерческих целей с одними лишь светлыми намериниями
# Логика
## Определения
**ID** — это идентификатор Telegram ID, который можно получить [здесь](https://t.me/getmyid_bot)

**Внутренний ID** — это идентификатор, созданный внутри бота. Отображается в меню
## Роли
**Главный Администратор** — это пользователь, имеющий полный доступ к модерации бота. ID внесен в список ```HOST_ADMINS_ID```.

Возможности:
- Удаление пользователя
- Удаление заявки пользователя
- Просмотр заявки пользователя
- Ввод кода подарка

**Модератор** — это пользователь, наделенный дополнительными возможностями. ID должен быть внесен в список ```ADMINS_ID```

Возможности:
- Получать заявки на верификацию от пользователей
- Возможность отклонить/принять заявку
## Верификация
Заявка на вступление в бота отправляется от всех пользователей, первый раз написавших /start. Принимают заявки администраторы из ```ADMINS_ID```
## Ввод предпочтений
Для участия в тайном санте, важно ввести свои предпочтения к подарку. Делается это по нажатию кнопки "Участвовать"

Заявки принимаются **за 1 час до времени подведения итогов**.

Здесь пользователю предлагается ответить на 3 вопроса. По умолчанию: 
1. Чем ты увлекаешься? - Хобби
2. Что бы ты НЕ хотел бы получить в качестве подарка? - Не хотел бы получить как подарок
3. Опиши твои предпочтения в подарке. Предпочтения в подарке

_Вопросы могут быть изменены. Подробности описаны в технической части._

После ответа, заявка пользователя отправляется Главному Администратору.

## Система подведения итогов
В определенное время, указанное в ```RELEASE_TIMESTAMP``` бот:

1. Берет всех пользователей, ответивших на вопросы
2. Смешивает и распределяет по кругу между собой

## Система подарков по коду
**Код** — это произведение Внутреннего ID пользователя на сумма двух случайных чисел в диапазоне от 1000 до 100000 и от 100 до 900

1. Код выдачи можно узнать в меню "Я принес подарок"
2. Его нужно показать Главному Администратору
3. Главный Администратор должен ввести код в системе. Таким образом он узнает Внутренний ID человека, выпавшего тайному санте и закрепит его за подарком. 
4. После этого подарок будет считаться "доставленным"

Для получения подарка, нужно показать свой Внутренний ID из меню Главному Администратору

# Техническая часть
## Общее
Проект написан на Python 3.9 на библиотеке aiogram. Поскольку заняло всего пару дней, качество кода может быть не самым лучшим. Сделано в условиях сжатых сроков, хотя это здесь главное

## Вопросы
Редактируются в _/config/questions.json_ в формате:

```json
{
    "question_type": {
        "name": "Название вопроса",
        "question": "Вопрос, который будет отображаться у пользователя при прохождении ввода предпочтений"
    }
}
```

## Тексты
Ответы бота можно редактировать в _/config/texts.json_

## Запуск
### Настройка переменных окружения
Файл .env с переменными:

_Все значения должны заключаться в кавычки_

```RELEASE_TIMESTAMP``` — это время подведения итогов в Unix timestamp формате

```GIFT_BUY_UNTIL``` — это время в Unix timestamp формате. Время, до которого нужно купить подарок

```BOT_TOKEN``` — это токен бота из BotFather

``HOST_ADMINS_ID`` — это Главные Администраторы (их может быть несколько, добавлять через пробел). Telegram ID через пробел

``ADMINS_ID`` — это Модераторы. Telegram ID через пробел

```DB_URL``` — это строка подключения к БД в формате, нужном для Python SQLAlchemy.

_Пример_:
```.env
BOT_TOKEN = "1487130832:...."
DB_URL = "string://"

HOST_ADMINS_ID = "5827525"
ADMINS_ID = "58567343 85739513"

GIFT_BUY_UNTIL = "1755115200"
RELEASE_TIMESTAMP = "1739390400"
```

### Инициализация БД
Для этого нужно запустить небольшой скрипт из под папки "src". Он создаст необходимые таблицы в базе

```python
from database import engine
from database.models import (
    UserModel,
    SettingsModel
)

UserModel.metadata.create_all(engine)
```

### Запуск через docker-compose
Команда для запуска:

```bash
docker-compose up --build -d
```

# Будущее
Бот нуждается в доработках

- [ ] полноценная админ-панель с возможностью просмотреть/изменить каждого пользователя
- [ ] напоминание что пользователь не купил подарок за два дня до истечения ```GIFT_BUY_UNTIL```
- [ ] добавить рассылки для главного администратора
- [ ] возможность для главного администратора динамично изменять права модераторов (права: принимать коды подарков, делать рассылки, банить пользователей, просмотр заявок и тп.)

# Контакты
https://uw935.ru/
