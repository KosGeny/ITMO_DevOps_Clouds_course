# Отчёт по лабораторной работе №3

Выполнили: Генне Константин K3240 и Савченко Анастасия K3241

## Техническое задание

1. Написать “плохой” CI/CD файл, который работает, но в нем есть не менее пяти “bad practices” по написанию CI/CD
2. Написать “хороший” CI/CD, в котором эти плохие практики исправлены
3. В Readme описать каждую из плохих практик в плохом файле, почему она плохая и как в хорошем она была исправлена, как исправление повлияло на результат
4. Прочитать историю про Васю (она быстрая, забавная и того стоит): https://habr.com/ru/articles/689234/   ✔️

# Основная часть
### Что это? 
Как применяется и используется ci/cd:
Разработчику падает новая задачка. Предположим разработчик сделал новую ветку, написал у себя локально новую фичу и она вроде бы работает. Но что произойдет, когда он начнет ее пушить?) Запустится процесс pipeline ci/cd :) Если все джобы пайплайна пройдут успешно, никаких ошибок не будет отловлено, у нас задеплоятся изменения на сайт. Ура! Таким образом нам не нужно заходить на сервер и ручками все развертывать и деплоить, работать с докером, все будет автоматизировано.
![image](https://github.com/user-attachments/assets/a1637200-4b3f-42ee-b1d7-f166f16b4f7a)

Мини таск, для которого может понадобиться ci/cd: на сайт хотят добавить новую фичу, так,  чтобы она не сломала то, что уже работает и все тесты были успешны
(в упрощенной версии мы просто меняли текст на сайте, ну и соответственно тесты:)  )

### Посмотрим на файлы, а потом рассмотрим что плохо что хорошо
### "Плохой" файл
```yml
name: Lab_3 bad CI/CD

on:
  push:
    branches:
      - main

jobs:
  big_job:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v1

    - name: Install dependencies
      run: npm install

    - name: Lint code
      run: npm run lint

    - name: Build project
      run: npm run build

    - name: Run unit tests
      run: ./unit-tests.sh

    - name: Run integration tests
      run: ./integration-tests.sh

    - name: Deploy to production
      run: ./deploy.sh

```
### "Хороший" файл 
```yml
name: Lab_3 good CI/CD

on: [push, pull_request]

stages:
  - build
  - test
  - deploy

build-job:
  stage: build
  runs-on: ubuntu-20.04
  script:
    - name: Checkout code
      uses: actions/checkout@v2
    - name: Caching npm dependencies
      uses: actions/cache@v2
      with:
        path: ./.cache/npm
        key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
        restore-keys: |
          ${{ runner.os }}-node-
    - name: Install dependencies
      run: npm ci
    - name: Lint code
      run: npm run lint
    - name: Build project
      run: npm run build

test-job:
  stage: test
  runs-on: ubuntu-20.04
  needs: build
  script:
    - name: Checkout code
      uses: actions/checkout@v2
    - name: Caching npm dependencies
      uses: actions/cache@v2
      with:
        path: ./.cache/npm
        key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
        restore-keys: |
          ${{ runner.os }}-node-
    - name: Install dependencies
      run: npm ci
    - name: Run tests
      run: npm test

deploy-job:
  stage: deploy
  runs-on: ubuntu-20.04
  needs: test
  if: github.ref == 'refs/heads/main'
  script:
    - name: Checkout code
      uses: actions/checkout@v2
    - name: Deploy to production
      run: |
        docker-compose down
        docker-compose up -d
```
! Но оба работают
## 1 Использование ubuntu:latest 
### Плохо 
```yml
jobs:
  build:
    runs-on: ubuntu:latest
```
Автоматическое использование последней версии может привести к неожиданным проблемам с интеграцией и совместимостью
### Хорошо
```yml
jobs:
  build:
    runs-on: ubuntu-20.04
```
Для стабильной работы лучше выбрать конкретную версию
## 2 Все в одном pipeline
### Плохо 
```yaml
big_job:
    runs-on: ubuntu-latest
    steps:
      - name: Build
        run: ./build.sh
      - name: Unit tests
        run: ./unit-tests.sh
      - name: Integration tests
        run: ./integration-tests.sh
      - name: Deploy
        run: ./deploy.sh
```

### Хорошо
```yml
stages:
  - build
  - test
  - deploy

build-job:
  stage: build
  runs-on: ubuntu-20.04


test-job:
  stage: test
  runs-on: ubuntu-20.04
  needs: build


deploy-job:
  stage: deploy
  runs-on: ubuntu-20.04
  needs: test

```
Будет лучше разделить пайплайн на этапы (сборка, тесты, деплой). Так CI/CD будет гибче  его станет легче масштабировать. И добавим условия для начала следующего этапа пайплайна, так деплой не сможет начаться, если не были пройдены тесты, а те не начнутся без успешно сборки.
## 3 Отсутствие кэширования
### Плохо 
```yml
jobs:
  big_job:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v1

    - name: Install dependencies
      run: npm install
```

### Хорошо
```yml
test-job:
  stage: test
  runs-on: ubuntu-20.04
  needs: build
  script:
    - name: Checkout code
      uses: actions/checkout@v2
    - name: Caching npm dependencies
      uses: actions/cache@v2
      with:
        path: ./.cache/npm
        key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
        restore-keys: |
          ${{ runner.os }}-node-
    - name: Install dependencies
      run: npm ci
    - name: Run tests
      run: npm test
```
Кэширование позволяет ускорить сборку и тест ci
## 4 npm install
### Плохо 
```yml
- name: Install dependencies
  run: npm install
```
Может привести к медленной работе и несовметимостям
### Хорошо
```yml
- name: Install dependencies
  run: npm ci
```
Исспользование npm ci предотвращает накопление ненужных файлов и ускаряет установку зависимостей, а следовательно и время сборки
## 5 Забыть про линтинг
### Плохо 
### Хорошо
```yml
build-job:
  stage: build
  runs-on: ubuntu-20.04
  script:
    - name: Checkout code
      uses: actions/checkout@v2
    - name: Caching npm dependencies
      uses: actions/cache@v2
      with:
        path: ./.cache/npm
        key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
        restore-keys: |
          ${{ runner.os }}-node-
    - name: Install dependencies
      run: npm ci
    - name: Lint code
      run: npm run lint
```
Линтинг помогает с синтаксическими ошибками в коде, а так же не нужными переменными, и небезопасными функциями
## 6 Чуть про докер
В итоговый файл не вошло но было опробовано пока запускали пайплайны 
### Плохо временные контейнеры от docker build
```yml
build-job:
  stage: build
  script:
    - docker build -t my-backend-image . --rm=false
```
Нет кэширования и удаления временных контейнеров, что нагружает дикс.
### Хорошо
```yml
build-job:
  stage: build
  script:
    - docker build -t my-backend-image .
```
docker build по умолчанию кэширует и удаляет временные контейнеры после сборок.
```yml
test-job:
  stage: test
  script:
    - docker run --rm my-backend-image pytest -s -v
```
Запускаем докер контейнер указываем образ, !не забываем удалить контейнер после всех тестов. -s -v, чтобы видеть все логи :)
_______
# Выводы
Пока мы выполняли лабу познакомились с GitHub Actions и GitLab(пайплайны чекались там), узнали о пайплайназ и джобах,

познали занак бесконечности

![image](https://github.com/user-attachments/assets/4943abe3-9474-43c3-89f3-bd8983528be7)

#### Стадии во время выполнения лабы
Волнующее ожидание:

![Снимок экрана 2024-10-20 162321](https://github.com/user-attachments/assets/0b40d1c6-1f16-43c5-847d-8e8ea9573da5)

Разочарование

![Снимок экрана 2024-10-20 162500](https://github.com/user-attachments/assets/53e2298f-85b6-4dab-958d-ed1c26f13abb)

Нирвана

![Снимок экрана 2024-10-20 164133](https://github.com/user-attachments/assets/2ed2fe93-9b4a-4213-9615-b735a0a8e0c6)


### Мем описывающий лабу
 
![image](https://github.com/user-attachments/assets/a20f86f5-c989-462e-9986-9e5fe610379b)

Когда написали первый минимально работоспособный файл и зачем-то впихнули туда докер, а потом пришло осознание, что нужно этот файл улучшить, а затем еще и ухудшить...

![image](https://github.com/user-attachments/assets/bc5b5029-dc73-4e3b-8111-4f5b68ce5af6)
```yml
stages:
  - build
  - test
  - deploy

build-job:
  stage: build
  script:
    - docker build -t my-backend-image .

test-job:
  stage: test
  script:
    - docker run --rm my-backend-image pytest -s -v

deploy-job:
  stage: deploy
  script:
    - docker compose up -d
```
