Приклад телеграм бота з інтернаціоналізацією (інтерфейс з вибором мови/переклада)

Важливі моменти:
1. Наявність файлів з перекладами (тека locales)
2. Встановлення middleware для перекладу
3. Викоритання gettext та lazy_gettext в місцях коду де потрібен переклад.

auto_translate.py - нашвидкоруч створений скрипт для автоматичного перекладу через google translate - працює погано, треба перевіряти переклад.    
