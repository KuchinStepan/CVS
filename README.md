# CVS
CVS - консольная реализация системы контроля версий.

Чтобы начать работу с приложением, запустите файл main.py и следуйте подсказкам. Для завершения работы введите команду '0' или 'stop'. Технические требования указаны в файле 'requirements.txt'

## Команды

### init
- **init**  - активация системы контроля версий в выбранной директории

### add
- **add .**  - добавление всех измененных файлов в «коммит индекс»
- **add <имя файла>** или **add <имя файла1>,  <имя файла2> (и т.д.)**  - добавление конкретных файлов в «коммит индекс» (Примечание: имя файлов пишутся относительные и без кавычек)

### commit
- **commit -m '<Сообщение_к_комиту>'**  - создание коммита, с прикреплением сообщения (сообщение не может содержать пробеллы, а так же каждое сообщение должно быть уникальным)
- **commit**  - создание коммита с названием по умолчанию ('com_<номер коммита>')
Примечание: невозможно создавать обособленный от «HEAD» коммит, то есть создать коммит можно только находясь на последнем коммите в данной ветке (альтернативный вариант: создать новую ветку и уже в ней создавать необходимый коммит)

### branch
- **branch <Name>**  - создание ветки с названием Name (возможны только уникальные имена, без пробелов)

### tag
- **tag '<Сообщение_к_тегу>'**  - прикрепление к коммиту тега с сообщением (сообщение не может содержать пробеллы, а так же каждое сообщение к тегу должно быть уникальным)

### checkout
- **checkout <Сообщение_комита>**  - переключение на коммит по его сообщению
- **checkout -t <Собщение_тега>**  - переключение на коммит, к которому привязан тег с введенным сообщением
- **checkout -b <Имя_ветви>**      - переключение на ветку с введенным именем (в этом случае происходит переключение на последний коммит, созданный в данной ветке)

### log
- **log**  - узнать информацию о текущем коммите: имя коммита, в какой ветке находится, когда был создан, список измений (новые, измененные и удаленные файлы будут написаны соответствующими цветами - зеленый, желтый и красный)
- **log <Сообщение_комита>**  - узнать информацию о коммите с соответствующим сообщением

### diff
- **diff**  - просмотреть разницу по всем измененным файлам между текущим и предыдущим коммитом (либо если файлы в текущей дирректории изменен, то разницу измененной версией и версией последнего коммита)
- **diff <Имя_файла>**  - посмотреть разницу выбранного файла между текущим и предыдущим коммитом (либо если файл в текущей дирректории изменен, то разницу измененной версией и версией последнего коммита)
- **diff <Предыдущий_коммит> <Коммит_с_измененным_файлом> <Имя_файла>**  - посмотреть разницу выбранного файла между текущим и предыдущим коммитом (либо если файл в текущей дирректории изменен, то разницу измененной версией и версией последнего коммита)

### show
- **show**       - просмотреть список коммитов в текущей ветке
- **show -all**  - просмотреть список всех коммитов
- **show -b**    - просмотреть список всех веток
- **show -t**    - просмотреть список всех тегов (а также коммитов, на которые ссылаются теги)