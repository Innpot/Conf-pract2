# Практическая работа № 2 — вариант 20

Инструмент читает официальный индекс Ubuntu Packages по HTTP(S) и
выводит прямые зависимости пакета. Нужен Python 3.10+. Сборки и
сторонних библиотек нет.

~~~sh
python -m src.main --config examples/ubuntu.ini
python -m unittest discover -s tests -v
~~~

Поддерживаются Packages, Packages.gz, Packages.xz. Поля Pre-Depends
и Depends читаются с продолжениями строк. Выводятся все имена из групп
альтернатив, без ограничений версии и архитектуры; это ещё не план APT.
