# Отчёт по лабораторной работе №3

Выполнили: Генне Константин K3240 и Савченко Анастасия K3241

## Техническое задание

1. Написать “плохой” CI/CD файл, который работает, но в нем есть не менее пяти “bad practices” по написанию CI/CD
2. Написать “хороший” CI/CD, в котором эти плохие практики исправлены
3. В Readme описать каждую из плохих практик в плохом файле, почему она плохая и как в хорошем она была исправлена, как исправление повлияло на результат
4. Прочитать историю про Васю (она быстрая, забавная и того стоит): https://habr.com/ru/articles/689234/   ✔️

# Основная часть

### CI/CD: что это?

**CI/CD (Continuous Integration и Continuous Delivery/Deployment)** — процесс, позволяющий автоматизировать сборку, тестирование и деплой.

**Как применяется и используется CI/CD**:

Пример: Разработчику падает новая задачка. Предположим разработчик сделал новую ветку, написал у себя локально новую фичу и она вроде бы работает. Но что произойдет, когда он начнет ее пушить?) Запустится процесс pipeline ci/cd :) Если все джобы пайплайна пройдут успешно, никаких ошибок не будет отловлено, у нас задеплоятся изменения на сайт. Ура! Таким образом нам не нужно заходить на сервер и ручками все развертывать и деплоить, работать с докером, все будет автоматизировано.

**Для этой лабораторной работы создадим мини-проект, где будем проверять пайпланы**:
- Для работы будем использовать **GitHub Actions**.
- Создали маленький проект **Hello, World!** с основным скриптом `hello.py`, юнит-тестом `test_hello.py` и пустым `requirements.txt`.

### "Плохой" файл
```yml
name: CI/CD bad_practices

on:
  push:
    branches:
      - master
  pull_request:
    branches:
      - master

jobs:
  all_in_one:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - uses: actions/setup-python@v2

      - run: pip install -r requirements.txt

      - run: python hello.py

      - run: python -m unittest discover

      - run: echo "Deploying application..."
```
### Проверка работы:
![image](https://github.com/user-attachments/assets/aa519f7e-f3b4-4017-a814-8bf206142b9f)
### "Что тут плохо" или "Проблемы при отсутствии хороших практик в CI/CD":

- **НЕ задается фиксированная версия среды (OS)**:
  Использование `ubuntu-latest` вместо конкретной версии может привести к проблемам со стабильностью и совместимостью, поскольку среда выполнения может измениться без нашего ведома.

- **НЕ задаются фиксированные версии действий `actions`, зависимостей и других инструментов**:
  Это может повлечь проблемы с совместимостью и непредсказуемое поведение, например, разный результат при разных запусках.

- **Отсутствуют названия и пояснения действий**:
  Отсутствие хороших описательных названий затрудняет понимание кода другими людьми (или самим собой через месяц) и работу с логами.

- **Все выполняется в одном блоке кода (т.е. нет разделения на джобы)**:
  Это уменьшает гибкость и масштабируемость процесса, затрудняет отладку и может увеличивать время выполнения.

- **Отсутствие кэширования зависимостей**:
  Неэффективно каждый раз загружать и устанавливать их заново, это увеличивает время выполнения процесса и требует дополнительных ресурсов.

### "Хороший" файл 
```yml
name: CI/CD good_practices


on:
  push:
    branches:
      - master
  pull_request:
    branches:
      - master

jobs:
  build:
    name: build_job
    runs-on: ubuntu-20.04

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python 3.9
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

      - name: Run Hello World script
        run: python hello.py

  test:
    name: test_job
    runs-on: ubuntu-20.04
    needs: build

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python 3.9
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Run tests
        run: python -m unittest discover

  deploy:
    name: deploy_job
    runs-on: ubuntu-20.04
    needs: test

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python 3.9
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Deploy Application
        run: echo "Deploying application..."
```
### Проверка работы:
![image](https://github.com/user-attachments/assets/58ae87cf-7c4b-430a-b780-d117e8f0d49e)
### Best Practices:

1. **Фиксированная версия OS**:
   Задание определенной версии, например, `ubuntu-20.04`, обеспечивает стабильность и уверенность, что она не изменится без нашего вмешательства.

2. **Фиксированные версии зависимостей и `actions`**:
   Это обеспечивает предсказуемость и стабильность процесса, помогает избежать возможных сбоев от обновления инструментов.
   ```yml
   steps:
     - name: Checkout repository
       uses: actions/checkout@v4  # Фиксированная версия действия для проверки кода

     - name: Set up Python 3.9
       uses: actions/setup-python@v4  # Фиксированная версия действия настройки Python
       with:
         python-version: '3.9'  # Фикс. версия Python

     - name: Cache dependencies
       uses: actions/cache@v3  # Фикс. версия для кэширования
   
3. **У каждого шага есть поясняющее название `(- name:)`**:
   Это здорово повышает читабельность кода, упрощает работу с логами и отладку.
   ```yml
   name: build_job
    - name: Checkout repository
    - name: Set up Python 3.9
    - name: Cache dependencies
    - name: Install dependencies
    - name: Run Hello World script
    name: test_job
     - name: Run tests
    name: deploy_job
     - name: Deploy Application

4. **Процесс разделен на несколько джоб**:
   - `build_job`: собирает проект, кэширует и устанавливает зависимости
   - `test_job`: запускает тесты
   - `deploy_job`: отвечает за развертывание

   Это структурирует код и дает больше возможностей для масштабирования и отладки.

5. **Джобы связаны между собой с помощью `needs:`**:
   Появляется контроль последовательности выполнения. Зависимая джоба не начнется, если нужная ей завершилась провалом. Например, тесты (`test_job`) не начнутся, если сборка (`build_job`) завершилась с ошибкой.

6. **Зависимости кэшируются перед установкой**:
   Благодаря кэшу их не нужно каждый раз загружать заново, что сокращает время сборки.



_______
# Выводы

Пока выполняли лабу познакомились с GitHub Actions и GitLab, узнали о пайплайназ и джобах, написали несколько best practices
И познали занак бесконечности

![image](https://github.com/user-attachments/assets/4943abe3-9474-43c3-89f3-bd8983528be7)

# Дополнительные скрины

На всякий случай вот еще скрины и ссылка на репозиторий, где запускались пайплайны: [GitHub Hello Repository](https://github.com/Gppovrm/cicd) 

- для BAD
![image](https://github.com/user-attachments/assets/54793cb1-a319-4b83-adfe-49a9c725bb4d)
![image](https://github.com/user-attachments/assets/f30a4cdb-edf5-4d09-9b08-96c19d224943)

- для GOOD
![image](https://github.com/user-attachments/assets/42416fe8-5b81-41e7-b172-f48b3adb918c)
![image](https://github.com/user-attachments/assets/14dae8a2-eae6-4fc0-b22c-b64fb59758f1)

