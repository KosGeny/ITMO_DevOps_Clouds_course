# Отчёт по лабораторной работе №3*

Выполнили: Генне Константин K3240 и Савченко Анастасия K3241

## Техническое задание
- Поднять секретохранилку
- Описать почему наш способ хорош
- Описать почему хранение секретов в CI/CD переменных репозитория не является хорошей практикой
  
### !Мы выбрали в качестве секретохранилки Doppler тк он легко интегрируется в GitHub Actions

# Интеграция Doppler и GitHub Actions

## Шаг 1: Установка Doppler через командную строку

- Скачиваем и устанавливаем Doppler + Проверяем установленную версию Doppler:
    ```sh
    doppler --version
    ```

- Проверяем, что у нас сейчас нет никаких проектов:
    ```sh
    doppler setup
    ```
    **Ошибка (как и ожидалось)**
    ```
    Doppler Error: you do not have access to any projects
    ```

## Шаг 2: Добавляем секреты работаем с Doppler

### Notes:
### Connection: Doppler –auth– GitHub
### Syncs: CI/CD –sync– GitHub

Мы будем использовать **GitHub Actions**.

1. В Doppler создаем новый проект под названием `doppler_cicd`.
2. Создаем окружение `ci-cd` и добавляем секреты (5 шт):
    - `DATABASE_PASSWORD: unicornHorn123`
    - `API_KEY: magicalRainbowAPI`
    - `ENCRYPTION_KEY: sparkleShine123`
    - `AUTH_TOKEN: glitterCupcakeToken`
    - `SERVER_ENDPOINT: https://enchanted.unicorns.net`
![image](https://github.com/user-attachments/assets/111dd962-9326-4036-bc6e-6a783f987a44)

3. Создаем соединение с GitHub:
    - Переходим в **Integrations** → **Add Sync** → выбираем GitHub → **Install** → **Configure a new Integration**.
![image](https://github.com/user-attachments/assets/dccd19aa-cd54-492f-a78d-7465283769e5)

4. Переходим на страницу проекта, где видим статус синхронизации (**in sync status**).

![image](https://github.com/user-attachments/assets/98078c4a-10b5-4203-a5ea-85221a955661)

5. Переходим по ссылке **Destination**, которая ведет на страницу секретов репозитория, где видим добавленные секреты.

![image](https://github.com/user-attachments/assets/155401a5-462b-4d25-870b-5c4d4b5d26ab)

Но мы вводили 5 секретов а тут види 8 это потому что 3 из них addition of Doppler's standard meta variables, они генерируются автоматически

![image](https://github.com/user-attachments/assets/1da2f2a7-6b01-40ed-b30a-4156764e10f7)

## Шаг 3: Генерация токена и настройка GitHub
Переходим в **Access** и генерируем токен:

![image](https://github.com/user-attachments/assets/a8e927eb-a9ec-4824-9baf-3ef6db71aafa)

Сгенерировав, переходим в репозиторий:
    - **Settings** → **Secrets and variables** → **Actions**.
    - Создаем секрет `DOPPLER_TOKEN`, в него вставляем скопированный токен.

![image](https://github.com/user-attachments/assets/76078e52-7562-44ff-a942-0a2adf7af709)
##  Шаг 4: Наконец пишем CI/CD
## Проверим сделав вывод секретов в логах
название(see_secrets_in_logs.yml)
```yml
name: CI/CD doppler_secrets

on:
  push:
    branches:
      - main

jobs:
  fetch-secrets:
    runs-on: ubuntu-20.04

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Install Doppler CLI
      run: |
        sudo curl -Ls https://cli.doppler.com/install.sh | sudo sh

    - name: Doppler Fetch and Show secrets
      env:
        DOPPLER_TOKEN: ${{ secrets.DOPPLER_TOKEN }}
      run: |
        doppler secrets download --format env --no-file > doppler_secrets.env
        cat doppler_secrets.env
```
И ,наконец, мы видим наши секреты про единорогов в логах:

![image](https://github.com/user-attachments/assets/73d328a3-78bf-469f-8b69-8d4c7134f8d6)

## Если задание состоит именно в том, чтобы не светить секреты в логах, но делать с ними что-то, то вот: 
 название(see_in_logs_secrets_keys_but_not_values.yml)
```yml
name: CI/CD doppler_secrets
on:
  push:
    branches:
      - main

jobs:
  fetch-secrets:
    runs-on: ubuntu-20.04

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Install Doppler CLI
      run: |
        sudo curl -Ls https://cli.doppler.com/install.sh | sudo sh

    - name: Doppler Fetch and Export secrets
      env:
        DOPPLER_TOKEN: ${{ secrets.DOPPLER_TOKEN }}
      run: |
        doppler secrets download --format env --no-file > doppler_secrets.env
        echo "Содержимое doppler_secrets.env:"
        cat doppler_secrets.env
        set -a
        source doppler_secrets.env
        set +a

    - name: Check and Use secrets securely
      env:
        DATABASE_PASSWORD: ${{ secrets.DATABASE_PASSWORD }}
        API_KEY: ${{ secrets.API_KEY }}
        ENCRYPTION_KEY: ${{ secrets.ENCRYPTION_KEY }}
        AUTH_TOKEN: ${{ secrets.AUTH_TOKEN }}
        SERVER_ENDPOINT: ${{ secrets.SERVER_ENDPOINT }}
      run: |
        echo "Проверяем наличие секретов"
        if [ -z "$DATABASE_PASSWORD" ]; then echo "DATABASE_PASSWORD is not set"; exit 1; fi
        if [ -з "$API_KEY" ]; then echo "API_KEY is not set"; exit 1; fi
        if [ -з "$ENCRYPTION_KEY" ]; then echo "ENCRYPTION_KEY is not set"; exit 1; fi
        if [ -з "$AUTH_TOKEN" ]; then echo "AUTH_TOKEN is not set"; exit 1; fi
        if [ -з "$SERVER_ENDPOINT" ]; then echo "SERVER_ENDPOINT is not set"; exit 1; fi
        echo "Все секреты успешно загружены и установлены"
        # Пример использования секретов
        echo "Подключаемся к базе данных"
        echo "Секреты не отображаются в логах"
        # psql -h your_database_host -U your_database_user -d your_database_name -W $DATABASE_PASSWORD < your_sql_script.sql
        echo "Выполняем вызов API"
        # curl -H "Authorization: Bearer $API_KEY" $SERVER_ENDPOINT
```
(видим ключи секретов, но не значения(***) и обязательно проверяем, что секреты получены):

![image](https://github.com/user-attachments/assets/a27455eb-deee-4e6f-9895-0a2f227940e2)

## Вот вообще не светим секреты в логах ( обязательно проверяем, что секреты получены, + в примере использование секретов для подклучения ДБ и API)
название(non_showing_secrets_in_logs.yml)
```yml
name: CI/CD doppler_secrets

on:
  push:
    branches:
      - main

jobs:
  fetch-secrets:
    runs-on: ubuntu-20.04

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Install Doppler CLI
      run: |
        sudo curl -Ls https://cli.doppler.com/install.sh | sudo sh

    - name: Doppler Fetch and Export secrets
      env:
        DOPPLER_TOKEN: ${{ secrets.DOPPLER_TOKEN }}
      run: |
        doppler secrets download --format env --no-file > doppler_secrets.env
        set -a
        source doppler_secrets.env
        set +a

    - name: Check and Use secrets securely
      env:
        DATABASE_PASSWORD: ${{ secrets.DATABASE_PASSWORD }}
        API_KEY: ${{ secrets.API_KEY }}
        ENCRYPTION_KEY: ${{ secrets.ENCRYPTION_KEY }}
        AUTH_TOKEN: ${{ secrets.AUTH_TOKEN }}
        SERVER_ENDPOINT: ${{ secrets.SERVER_ENDPOINT }}
      run: |
        echo "Проверяем наличие секретов"
        if [ -z "$DATABASE_PASSWORD" ]; then echo "DATABASE_PASSWORD is not set"; exit 1; fi
        if [ -z "$API_KEY" ]; then echo "API_KEY is not set"; exit 1; fi
        if [ -z "$ENCRYPTION_KEY" ]; then echo "ENCRYPTION_KEY is not set"; exit 1; fi
        if [ -z "$AUTH_TOKEN" ]; then echo "AUTH_TOKEN is not set"; exit 1; fi
        if [ -z "$SERVER_ENDPOINT" ]; then echo "SERVER_ENDPOINT is not set"; exit 1; fi
        echo "Все секреты успешно загружены и установлены как переменные среды"
        echo "Ура! Секреты не отображаются в логах"
        # Пример использования секретов
        echo "Подключаемся к базе данных"
        # psql -h your_database_host -U your_database_user -d your_database_name -W $DATABASE_PASSWORD < your_sql_script.sql
        echo "Вызов API"
        # curl -H "Authorization: Bearer $API_KEY" $SERVER_ENDPOINT
```
Видим, фразу, что все секреты успешно получины и в примере используем их для подклучения 

![image](https://github.com/user-attachments/assets/ca9ef87e-21bf-44d1-8b0e-7f1f901dfd96)

### Ссылка на репозиторий, где чекались пайплайны:[GitHub doppler_ci/cd Repository](https://github.com/Gppovrm/-doppler_cicd/actions) 

## Итоги
### Почему наш способ (Doppler) красивый:

### Почему хранение секретов в CI/CD переменных репозитория не является хорошей практикой:

## Дополнительный пункт 
  Секреты также очень легко получать, добавлять/удалять, используя командную строку, для этого нужно установить doppler, залогиниться, и выполнить команду `doppler setup`, которая позволит вам выбрать один из ваших проектов doppler, для просмотра используйте команду `doppler setup`:

![Снимок экрана 2024-12-17 153728](https://github.com/user-attachments/assets/6701a40e-47c7-421c-ac99-b91fc7c0e472)
