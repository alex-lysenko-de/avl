# Development Deployment и обновление Windows-приложения

**Статус:** Technical Baseline
**Назначение:** описание процесса сборки, публикации, доставки и обновления клиентского Windows-приложения на этапе разработки.

---

# 1. Назначение документа

Данный документ описывает техническую архитектуру и workflow доставки новых версий локального Windows-приложения заказчику.

Архитектура предназначена прежде всего для периода активной разработки, когда приложение ещё постоянно изменяется и не требуется полноценная система установки и автоматического обновления.

Основная цель:

> Максимально простой и надёжный процесс доставки новой версии заказчику без необходимости устанавливать на его компьютере Python, Git, IDE, виртуальное окружение, Docker или инструменты сборки.

На этапе разработки **не используются полноценный installer и отдельный Updater.exe**.

Обновление выполняется вручную через:

```text
Update Client
      ↓
update.bat
      ↓
PowerShell script
      ↓
GitHub Releases
      ↓
скачивание последнего релиза
      ↓
backup базы данных
      ↓
обновление файлов приложения
      ↓
миграция базы данных
      ↓
запуск приложения
```

В дальнейшем механизм может быть заменён на полноценный installer/updater без изменения общей модели публикации релизов.

---

# 2. Основной принцип

Используется следующая архитектура:

```text
Developer
    │
    │ git push
    ▼
GitHub Repository
    │
    ▼
GitHub Actions
    │
    ├── tests
    ├── build
    ├── packaging
    └── release
            │
            ▼
      GitHub Release
            │
            ├── application ZIP
            └── manifest.json
                    │
                    ▼
              Client Computer
                    │
                    ▼
                update.bat
                    │
                    ▼
              PowerShell
                    │
                    ▼
             latest Release
                    │
                    ▼
          application update
```

Google Drive в процессе доставки обновлений **не используется**.

Google Drive используется только для пользовательских данных и резервных копий.

---

# 3. Распределение ответственности между системами

Каждая система имеет одну основную задачу.

| Система             | Назначение                                 |
| ------------------- | ------------------------------------------ |
| Git                 | контроль версий исходного кода             |
| GitHub Repository   | хранение исходного кода                    |
| GitHub Actions      | автоматическое тестирование и сборка       |
| GitHub Releases     | публикация готовых версий приложения       |
| `manifest.json`     | описание опубликованной версии             |
| `version.txt`       | информация об установленной версии         |
| `update.bat`        | пользовательская точка запуска обновления  |
| PowerShell          | техническая реализация процесса обновления |
| SQLite              | локальная рабочая база данных              |
| Alembic             | миграции базы данных                       |
| Google Drive        | резервные копии и пользовательские файлы   |
| Windows Application | конечный продукт                           |

Системы не должны использоваться для чужих задач без необходимости.

В частности:

* GitHub не используется для хранения пользовательской базы;
* Google Drive не используется как основной источник обновлений;
* Git не устанавливается на компьютере заказчика;
* Python не устанавливается на компьютере заказчика.

---

# 4. GitHub Releases

## 4.1. GitHub Releases является источником дистрибутива

Готовые версии приложения публикуются в GitHub Releases.

Каждая опубликованная версия содержит как минимум:

```text
ClientApp-v0.0.17.zip
manifest.json
```

Пример:

```text
GitHub
└── Releases
    ├── v0.0.15
    ├── v0.0.16
    └── v0.0.17  ← latest
```

Для обновления используется последний опубликованный GitHub Release.

---

# 5. Использование latest Release

Приложение обновления не должно искать последнюю версию путём анализа списка файлов или ручной настройки имени ZIP.

GitHub предоставляет понятие:

```text
latest release
```

Именно последний опубликованный стабильный Release считается актуальным.

Updater получает информацию о последнем Release и определяет:

```text
latest release
    ↓
asset
    ↓
application ZIP
```

Это позволяет не изменять `update.bat` после каждого выпуска новой версии.

Например, после публикации:

```text
v0.0.17
```

а затем:

```text
v0.0.18
```

`update.bat` автоматически начинает получать `v0.0.18`.

Никаких изменений в клиентской установке не требуется.

---

# 6. Manifest

Несмотря на наличие GitHub Releases, проект использует дополнительный файл:

```text
manifest.json
```

Manifest является небольшим описанием опубликованной версии.

Пример:

```json
{
    "version": "0.0.17",
    "package": "ClientApp-v0.0.17.zip",
    "sha256": "..."
}
```

В дальнейшем manifest может быть расширен.

Например:

```json
{
    "version": "0.0.17",
    "package": "ClientApp-v0.0.17.zip",
    "sha256": "...",
    "min_supported_version": "0.0.12",
    "migration_required": true
}
```

Manifest не является источником истины для определения того, какой Release является последним.

Последний Release определяется GitHub.

Manifest описывает содержимое и параметры конкретного опубликованного Release.

---

# 7. Проверка целостности дистрибутива

После скачивания ZIP обновляющий скрипт должен проверить его checksum.

Используется SHA-256.

Процесс:

```text
download ZIP
     ↓
calculate SHA-256
     ↓
compare with manifest
     ↓
checksum OK
     ↓
continue update
```

Если checksum не совпадает:

```text
update failed
```

Файлы не должны устанавливаться.

Это защищает от повреждённого или неполностью скачанного архива.

---

# 8. Версия приложения

Версия проекта хранится в одном основном месте.

Предпочтительный вариант:

```text
pyproject.toml
```

Например:

```toml
[project]
version = "0.0.17"
```

`pyproject.toml` является источником версии проекта.

Другие файлы не должны редактироваться вручную только для изменения номера версии.

---

# 9. Генерация version.txt

При сборке автоматически создаётся:

```text
version.txt
```

Например:

```text
0.0.17
```

Этот файл входит в дистрибутив.

На компьютере заказчика он находится рядом с программной частью приложения.

Например:

```text
ClientApp/
    app/
        ClientApp.exe
        version.txt
```

`version.txt` используется для определения установленной версии и отображения версии пользователю.

---

# 10. Отображение версии пользователю

Версия должна быть видна в интерфейсе приложения.

Предполагаемое место:

```text
Help
└── About
```

или:

```text
О программе
```

Например:

```text
Client Application

Version: 0.0.17
```

Это позволяет заказчику визуально проверить, какая версия установлена.

Версия в `version.txt` и версия, отображаемая в интерфейсе, должны соответствовать.

---

# 11. Что входит в ZIP

В ZIP входит только программная часть приложения.

Пример:

```text
ClientApp-v0.0.17.zip

app/
    ClientApp.exe
    *.dll
    *.pyd
    другие необходимые файлы

migrations/
    ...
    
version.txt
```

Конкретная структура зависит от способа упаковки PyInstaller.

---

# 12. Что НЕ входит в ZIP

В дистрибутив не должны входить пользовательские данные.

В частности:

```text
data/
database.sqlite
backups/
```

не являются частью программного релиза.

Также в ZIP не должны попадать:

* персональные данные клиента;
* рабочая база данных;
* backup базы;
* пользовательские документы;
* пользовательские секреты;
* пароли;
* API tokens;
* другие локальные настройки, зависящие от конкретного компьютера.

Это принципиальное разделение:

```text
PROGRAM
    ≠
USER DATA
```

---

# 13. Конфигурационные файлы

Пользовательский конфигурационный файл не должен поставляться в ZIP как готовая конфигурация конкретного клиента.

Вместо этого приложение должно уметь самостоятельно создавать и обновлять конфигурацию.

Предпочтительный механизм:

```text
Application starts
       ↓
read config
       ↓
config does not exist?
       ├── yes → create default config
       └── no  → continue
       ↓
check required keys
       ↓
missing keys?
       ├── yes → add defaults / initialize
       └── no  → continue
```

Таким образом, новый параметр конфигурации может появиться в новой версии приложения без необходимости вручную заменять конфигурационный файл клиента.

---

# 14. Разделение программных и пользовательских настроек

Файлы приложения и пользовательские настройки должны быть разделены.

Например:

```text
C:\ClientApp\
    app\
    migrations\
    update\
```

и отдельно:

```text
C:\ClientAppData\
    config\
    data\
    backups\
```

Либо другая эквивалентная структура.

Главный принцип:

> Обновление приложения не должно уничтожать пользовательскую конфигурацию.

---

# 15. Секреты и первоначальная настройка

Некоторые настройки могут содержать секретные значения:

* API keys;
* пароли;
* токены;
* credentials;
* другие чувствительные параметры.

Они не должны находиться:

* в Git;
* в GitHub Release;
* в ZIP приложения;
* в исходном коде.

При первоначальной установке заказчику необходимо один раз передать или ввести необходимые секреты.

После этого они сохраняются локально.

Новая версия приложения не должна требовать повторной передачи этих секретов, если они уже существуют.

Если появится новый обязательный секрет, приложение должно корректно определить его отсутствие и запросить первоначальную настройку.

---

# 16. PowerShell и update.bat

Основной пользовательский интерфейс обновления:

```text
update.bat
```

PowerShell используется как технический исполнитель.

Пользователь не должен вручную запускать `.ps1`.

Схема:

```text
Update Client
     ↓
update.bat
     ↓
PowerShell
     ↓
update.ps1
```

---

# 17. Почему используется BAT

BAT является максимально простой точкой входа для пользователя.

Он:

* запускается двойным кликом;
* не требует Python;
* может запускать PowerShell;
* может отображать сообщения об ошибках;
* может предоставить пользователю инструкции, если возникла проблема.

На рабочем столе создаётся ярлык:

```text
Update Client
```

который запускает:

```text
update.bat
```

---

# 18. Запуск PowerShell без изменения системной политики

Не следует требовать от пользователя вручную изменять системную Execution Policy.

Необходимо запускать PowerShell таким образом, чтобы скрипт мог работать независимо от глобальной политики пользователя, в пределах разрешённых Windows механизмов.

Предпочтительная схема запуска:

```text
powershell.exe
    -NoProfile
    -ExecutionPolicy Bypass
    -File update.ps1
```

или эквивалентный безопасный способ.

Важно:

`ExecutionPolicy Bypass` относится к конкретному запуску PowerShell и не должен требовать изменения системной политики Windows.

Пользователь не должен выполнять вручную:

```text
Set-ExecutionPolicy ...
```

---

# 19. Обработка ошибок запуска PowerShell

`update.bat` должен проверять результат запуска PowerShell.

Если PowerShell не запустился или выполнение завершилось ошибкой, пользователь должен получить понятное сообщение.

Например:

```text
Не удалось запустить обновление.

Возможная причина:
PowerShell недоступен или запуск скриптов заблокирован системой.

Техническая информация:
...

Обратитесь к разработчику и передайте этот текст.
```

Не следует показывать пользователю бессмысленный stack trace, если его невозможно использовать для диагностики.

Технический лог должен сохраняться отдельно.

---

# 20. Лог обновления

Каждый запуск обновления должен создавать log-файл.

Например:

```text
logs/
    update_2026-08-09_151430.log
```

В лог желательно записывать:

* текущую версию;
* найденную последнюю версию;
* URL;
* начало скачивания;
* размер файла;
* checksum;
* результат проверки;
* backup;
* распаковку;
* миграции;
* результат обновления;
* ошибки.

Это особенно важно в период разработки, когда заказчик может сообщить:

> «Обновление не работает».

Вместо археологических раскопок по удалённому компьютеру разработчик получает log.

---

# 21. Общий workflow обновления

Полный процесс:

```text
User starts Update Client
        ↓
update.bat
        ↓
PowerShell update.ps1
        ↓
check application is not running
        ↓
read local version.txt
        ↓
request latest GitHub Release
        ↓
read manifest
        ↓
determine latest package
        ↓
download ZIP
        ↓
verify SHA-256
        ↓
create database backup
        ↓
extract ZIP to temporary directory
        ↓
replace application files
        ↓
run database migration
        ↓
write new version.txt
        ↓
cleanup temporary files
        ↓
launch application
```

---

# 22. Приложение должно быть закрыто

Обновление нельзя выполнять, пока основное приложение использует заменяемые файлы.

Перед обновлением проверяется:

```text
ClientApp.exe is running?
```

Если да:

```text
Закройте приложение и повторите обновление.
```

На этапе разработки не требуется принудительно завершать процесс.

Принудительное завершение может привести к:

* потере данных;
* повреждению незаписанных документов;
* некорректному завершению транзакции;
* другим нежелательным эффектам.

---

# 23. Staging directory

ZIP не должен распаковываться непосредственно поверх работающей установки.

Используется временная директория.

Например:

```text
C:\ClientAppUpdate\
    v0.0.17\
        app\
        migrations\
        version.txt
```

Процесс:

```text
download
   ↓
verify
   ↓
extract to temporary directory
   ↓
validate
   ↓
replace application
```

Это позволяет обнаружить проблемы до замены рабочей версии.

---

# 24. Замена файлов приложения

После успешной проверки ZIP:

```text
temporary app
      ↓
existing app
```

Заменяется только программная часть.

Не затрагиваются:

```text
data/
backups/
user config/
user documents/
```

---

# 25. Миграции базы данных

После установки файлов новой версии необходимо выполнить миграции базы данных.

Используется:

```text
Alembic
```

Схема:

```text
SQLite
   ↓
Alembic
   ↓
migration 001
   ↓
migration 002
   ↓
migration 003
   ↓
current schema
```

Рабочая база не заменяется новой пустой базой.

---

# 26. Способ запуска миграций

Для обновления приложение должно поддерживать специальный режим запуска:

```text
ClientApp.exe --migrate
```

или эквивалентный механизм.

Это необходимо явно реализовать в приложении.

Без этого автоматизация миграций будет вынуждена напрямую управлять внутренностями Python-приложения из BAT/PowerShell, что создаёт ненужную связанность.

Рекомендуемый вариант:

```text
update.bat
    ↓
update.ps1
    ↓
ClientApp.exe --migrate
    ↓
Alembic
    ↓
SQLite
```

---

# 27. Поведение режима `--migrate`

При запуске:

```text
ClientApp.exe --migrate
```

приложение:

1. загружает конфигурацию;
2. определяет расположение базы;
3. запускает Alembic;
4. выполняет необходимые migrations;
5. возвращает exit code;
6. завершает работу.

GUI в этом режиме не требуется.

Пример:

```text
ClientApp.exe --migrate
```

Успешное завершение:

```text
exit code 0
```

Ошибка:

```text
exit code != 0
```

`update.ps1` анализирует результат.

---

# 28. Почему миграция должна быть частью приложения

Это позволяет избежать ситуации:

```text
PowerShell
    ↓
знает детали SQLite
    ↓
знает Alembic
    ↓
знает внутреннюю структуру проекта
```

Вместо этого:

```text
PowerShell
    ↓
ClientApp.exe --migrate
    ↓
Application
    ↓
Alembic
```

PowerShell знает только внешний контракт:

```text
--migrate
```

Это уменьшает связанность deployment-скрипта с Python-кодом.

---

# 29. Backup перед миграцией

Backup базы является обязательным.

Перед запуском:

```text
ClientApp.exe --migrate
```

создаётся backup.

Схема:

```text
current database
       ↓
backup
       ↓
migration
```

Если migration завершается успешно:

```text
success
```

Если migration завершается ошибкой:

```text
failure
       ↓
update considered failed
       ↓
backup remains available
```

---

# 30. Формат backup

Предварительный формат:

```text
database_2026-08-09_151430.sqlite.zip
```

Пример:

```text
Backups/
    database_2026-08-09_151430.sqlite.zip
    database_2026-08-08_101210.sqlite.zip
    database_2026-08-07_173005.sqlite.zip
```

ZIP используется для уменьшения размера и удобства хранения.

---

# 31. Google Drive для backup

Google Drive используется для синхронизации backup-файлов.

Предпочтительная архитектура:

```text
Client PC
    │
    ▼
Google Drive synchronized folder
    │
    ▼
Cloud
    │
    ▼
Developer PC
```

То есть backup физически создаётся на компьютере заказчика, после чего Google Drive автоматически синхронизирует его в облако.

Разработчик получает локальную копию через собственную синхронизацию Google Drive.

---

# 32. Backup directory

Конкретный путь должен быть настраиваемым.

Например:

```text
Google Drive\
    ClientApp\
        Backups\
```

На компьютере клиента:

```text
C:\Users\User\Google Drive\ClientApp\Backups\
```

На компьютере разработчика:

```text
D:\Google Drive\ClientApp\Backups\
```

Конкретные пути могут отличаться.

Приложение должно работать с настроенным путём, а не предполагать конкретную букву диска.

---

# 33. Почему backup не хранится в Git

SQLite database не должна помещаться в Git repository.

Причины:

* персональные данные;
* история Git сохраняет старые версии;
* бинарная база плохо подходит для Git;
* backup и version control имеют разные задачи.

Используется:

```text
GitHub
    ↓
source code + releases

Google Drive
    ↓
user data backups
```

---

# 34. Версионирование

Используется формат:

```text
MAJOR.MINOR.PATCH
```

Например:

```text
0.0.1
0.0.2
0.1.0
1.0.0
```

На этапе разработки допускается использование:

```text
0.x.y
```

---

# 35. Источник версии

Основной источник:

```text
pyproject.toml
```

Например:

```toml
[project]
name = "client-app"
version = "0.0.17"
```

Build system получает эту версию автоматически.

На основании неё создаются:

```text
v0.0.17
ClientApp-v0.0.17.zip
version.txt
manifest.json
```

---

# 36. Один источник истины

Не допускается ситуация, когда разработчик должен вручную менять:

```text
pyproject.toml
version.txt
manifest.json
имя ZIP
GitHub Release
```

Версия задаётся один раз.

Остальные значения генерируются автоматически.

Схема:

```text
pyproject.toml
      │
      ▼
   0.0.17
      │
 ┌────┼───────────────┐
 ▼    ▼               ▼
ZIP  manifest      version.txt
 │
 ▼
GitHub Release v0.0.17
```

---

# 37. GitHub Actions

После:

```text
git push
```

запускается GitHub Actions.

Pipeline:

```text
git push
   ↓
checkout
   ↓
setup Python
   ↓
install dependencies
   ↓
pytest
   ↓
build application
   ↓
PyInstaller
   ↓
create ZIP
   ↓
create manifest
   ↓
calculate SHA-256
   ↓
create GitHub Release
   ↓
upload assets
```

---

# 38. Ошибка тестов

Если:

```text
pytest
```

завершается ошибкой:

```text
build
```

не выполняется.

GitHub Release не создаётся.

Следовательно, заказчик не получает версию, которая не прошла автоматические тесты.

Основной принцип:

```text
tests failed
     ↓
no release
```

---

# 39. Ошибка сборки

Если PyInstaller или другой packaging tool завершился ошибкой:

```text
no release
```

Только полностью успешно собранная версия может быть опубликована.

---

# 40. Создание Release

GitHub Actions автоматически создаёт Release.

Например:

```text
Release
v0.0.17
```

Assets:

```text
ClientApp-v0.0.17.zip
manifest.json
```

Release помечается как обычный стабильный release.

Необходимо избегать ситуации, когда development/pre-release автоматически становится `latest`, если updater должен устанавливать только стабильные версии.

---

# 41. GitHub Repository

На текущем этапе repository предполагается **public**.

Это существенно упрощает доставку приложения.

Клиенту не нужны:

* GitHub account;
* Git;
* GitHub token;
* GitHub CLI;
* credentials разработчика.

Он только скачивает опубликованный release.

---

# 42. Безопасность public repository

Public repository означает, что исходный код проекта потенциально доступен другим людям.

Это допустимо только при условии, что в repository отсутствуют:

* пароли;
* API keys;
* tokens;
* database;
* персональные данные;
* приватные клиентские документы;
* другие секреты.

Особенно важно использовать:

```text
.gitignore
```

для исключения:

```text
.env
*.secret
database.sqlite
backups/
local_config/
```

и других локальных данных.

---

# 43. Пользовательские секреты

Секреты клиента никогда не передаются через GitHub.

При первоначальной настройке они:

* вводятся вручную;
* либо передаются через отдельный безопасный механизм первоначальной настройки.

После сохранения они остаются на компьютере клиента.

Обновление приложения не должно удалять их.

---

# 44. Автоматическое создание конфигурации

Приложение должно уметь работать с отсутствующим конфигурационным файлом.

Пример:

```text
config.json отсутствует
        ↓
application starts
        ↓
create config.json
        ↓
write default values
        ↓
continue
```

Если в новой версии появился новый параметр:

```text
old config
    ↓
application detects missing key
    ↓
adds default value
    ↓
continues
```

Это позволяет не поставлять новый конфигурационный файл при каждом обновлении.

---

# 45. Реальный workflow разработчика

Разработчик изменяет код:

```text
code
 ↓
tests
 ↓
git commit
 ↓
git push
```

После этого GitHub Actions выполняет:

```text
pytest
 ↓
build
 ↓
package
 ↓
release
```

Если всё успешно:

```text
GitHub Release v0.0.17
```

становится доступным.

Разработчик не должен вручную копировать ZIP на компьютер заказчика.

---

# 46. Реальный workflow заказчика

Заказчик получает сообщение:

```text
Вышла новая версия.
Запустите Update Client.
```

Он запускает ярлык:

```text
Update Client
```

который вызывает:

```text
update.bat
```

Далее обновление выполняется автоматически.

---

# 47. Пользовательский сценарий обновления

Пример интерфейса консоли:

```text
Client Application Update
=========================

Current version: 0.0.16
Checking GitHub for latest release...

Latest version: 0.0.17

New version found.

Downloading...
[####################] 100%

Verifying package...
OK

Creating database backup...
OK

Installing application...
OK

Running database migrations...
OK

Update completed successfully.

Starting application...
```

Если обновлений нет:

```text
Current version: 0.0.17

Latest version: 0.0.17

Application is already up to date.
```

---

# 48. Если обновление не удалось

Обновление должно останавливаться при критической ошибке.

Например:

```text
download failed
checksum failed
backup failed
migration failed
```

В таких случаях:

```text
update = failed
```

Нельзя сообщать пользователю:

```text
Update completed successfully
```

если хотя бы один критический этап завершился ошибкой.

---

# 49. Последовательность операций

Рекомендуемый порядок:

```text
1. Check application is closed
2. Read current version
3. Get latest release
4. Determine package
5. Download package
6. Verify SHA-256
7. Extract package to staging
8. Validate staging
9. Create database backup
10. Replace application files
11. Run migration
12. Verify migration result
13. Update version.txt
14. Remove temporary files
15. Start application
```

Если возможно, backup следует создавать **до любых операций, способных изменить пользовательские данные**.

---

# 50. Что делать при ошибке migration

Пример:

```text
v0.0.16
   ↓
backup
   ↓
install v0.0.17
   ↓
migration
   ↓
ERROR
```

Update должен сообщить об ошибке и сохранить backup.

Автоматический rollback базы на первом этапе не является обязательным.

Однако архитектура должна оставлять возможность восстановить:

```text
database.sqlite
```

из:

```text
backup
```

---

# 51. Разделение application и data

Фундаментальное правило:

```text
Application files
        ≠
User data
```

Например:

```text
C:\ClientApp\
    app\
    migrations\
    update.bat
    update.ps1

C:\ClientAppData\
    data\
        database.sqlite
    config\
        config.json
    backups\
        ...
    logs\
        ...
```

Конкретная структура может быть изменена при реализации, но логическое разделение обязательно.

---

# 52. Почему installer пока не нужен

На этапе разработки установка выполняется вручную.

Первоначальная установка:

```text
1. Создать каталог
2. Скопировать application files
3. Создать data directories
4. Создать config
5. Создать update.bat
6. Создать ярлык Update Client
7. Настроить Google Drive backup directory
```

После этого повторная ручная установка не требуется.

Все последующие изменения приходят через:

```text
update.bat
```

---

# 53. Почему Updater.exe пока не нужен

На этапе разработки отдельный executable updater не требуется.

Используются:

```text
update.bat
update.ps1
```

Это позволяет:

* быстро менять механизм обновления;
* легко диагностировать ошибки;
* не собирать отдельный updater;
* не поддерживать дополнительный executable;
* не создавать installer;
* минимизировать количество инфраструктуры.

В будущем:

```text
update.bat + update.ps1
```

могут быть заменены на:

```text
Updater.exe
```

без изменения GitHub Release workflow.

---

# 54. Будущая эволюция

Текущая архитектура:

```text
GitHub Release
      ↓
update.bat
      ↓
PowerShell
```

может в будущем стать:

```text
GitHub Release
      ↓
Updater.exe
```

или:

```text
GitHub Release
      ↓
Installer / Updater
```

При этом GitHub Releases, versioning, manifest и разделение application/data могут остаться без изменений.

---

# 55. Google Drive

Google Drive не участвует в распространении программного обеспечения.

Он используется для:

```text
database backups
user files
archives
```

Не используется:

```text
application update distribution
```

Это принципиальное разделение.

---

# 56. Итоговая архитектура

```text
                         DEVELOPER
                             │
                             │ git push
                             ▼
                     ┌───────────────┐
                     │    GitHub     │
                     │  Repository   │
                     └───────┬───────┘
                             │
                             ▼
                     GitHub Actions
                             │
                    ┌────────┴────────┐
                    │                 │
                  pytest            build
                    │                 │
                    └────────┬────────┘
                             │
                             ▼
                     Package / ZIP
                             │
                             ▼
                     manifest.json
                             │
                             ▼
                     GitHub Release
                             │
                             │ latest
                             ▼
                    CLIENT COMPUTER
                             │
                       Update Client
                             │
                             ▼
                        update.bat
                             │
                             ▼
                       update.ps1
                             │
                 ┌───────────┴───────────┐
                 │                       │
          GitHub latest             local version
                 │                       │
                 └───────────┬───────────┘
                             │
                             ▼
                       compare/check
                             │
                             ▼
                         download
                             │
                             ▼
                       SHA-256 check
                             │
                             ▼
                       database backup
                             │
                             ├──────────────► Google Drive
                             │
                             ▼
                       staging directory
                             │
                             ▼
                    replace application
                             │
                             ▼
                      --migrate
                             │
                             ▼
                          Alembic
                             │
                             ▼
                           SQLite
                             │
                             ▼
                       update version
                             │
                             ▼
                       start application
```

---

# 57. Финальный workflow проекта

В результате весь процесс сводится к следующему:

```text
DEVELOPER

изменение кода
      ↓
git commit
      ↓
git push
      ↓
GitHub Actions
      ↓
tests
      ↓
build
      ↓
ZIP
      ↓
manifest
      ↓
GitHub Release
      ↓
      ↓
      ↓
CLIENT

Update Client
      ↓
update.bat
      ↓
update.ps1
      ↓
latest GitHub Release
      ↓
download
      ↓
verify
      ↓
backup
      ↓
update
      ↓
migration
      ↓
start application
```

---

# 58. Архитектурные принципы

На текущем этапе необходимо придерживаться следующих принципов:

1. **GitHub является источником программных релизов.**
2. **Google Drive является хранилищем пользовательских backup-файлов.**
3. **GitHub Releases используются для распространения приложения.**
4. **Последний стабильный Release является актуальной версией.**
5. **Manifest используется для описания пакета и проверки целостности.**
6. **`version.txt` хранит установленную версию.**
7. **`pyproject.toml` является источником номера версии проекта.**
8. **Пользовательские данные не входят в программный ZIP.**
9. **Пользовательская конфигурация не заменяется при обновлении.**
10. **Секреты никогда не попадают в GitHub.**
11. **Перед миграцией базы создаётся backup.**
12. **Backup синхронизируется через Google Drive.**
13. **Миграции выполняются через Alembic.**
14. **Приложение предоставляет режим `--migrate`.**
15. **PowerShell запускается через `update.bat`.**
16. **Пользователь не должен вручную изменять Execution Policy.**
17. **Каждое обновление должно иметь лог.**
18. **Неуспешный build или test не должен создавать доступный клиенту Release.**
19. **Installer и Updater.exe на этапе разработки не требуются.**
20. **Архитектура должна позволять заменить BAT/PowerShell полноценным updater в будущем.**

---

# 59. Минимальный набор файлов проекта

Предварительно в repository должны присутствовать:

```text
project/
│
├── src/
│
├── tests/
│
├── migrations/
│
├── scripts/
│   ├── build.ps1
│   ├── package.ps1
│   └── create_manifest.ps1
│
├── deployment/
│   ├── update.bat
│   └── update.ps1
│
├── pyproject.toml
├── alembic.ini
├── .gitignore
│
└── .github/
    └── workflows/
        └── release.yml
```

Конкретные названия файлов могут быть изменены.

Главное, чтобы deployment-инфраструктура была отделена от исходного кода приложения.

---

# 60. Результат

Данная схема обеспечивает:

* отсутствие Python у заказчика;
* отсутствие Git у заказчика;
* отсутствие ручной сборки;
* отсутствие ручного копирования новых версий;
* отсутствие installer на этапе разработки;
* отсутствие отдельного Updater.exe;
* автоматическую сборку;
* автоматическое создание GitHub Release;
* автоматическое определение последней версии;
* проверку целостности ZIP;
* автоматический backup базы;
* автоматические Alembic migrations;
* сохранение пользовательских настроек;
* резервное копирование через Google Drive;
* возможность последующего перехода к полноценному updater/installer.

Главный пользовательский workflow при этом остаётся максимально простым:

```text
Разработчик:
    git push

Заказчик:
    Update Client
```

Всё остальное выполняется автоматически.
