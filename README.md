# Модуль для выявления аномалий по журналам событий

Для установки виртуального окружения в папке с файлами скриптов программы выполните в консоли следующие команды

```
pip3 -h
pip3 install -r requirements.txt --no-index --find-links 
pip install virtualenv
virtualenv <path_to_local_directory_for_venv>
```

Для активации виртуального окружения выполните команду

```
source mypython/bin/activate //mac
mypthon\Scripts\activate //windows
```

Для запуска программы в папке с файлами скриптов программы выполните в консоли команду 

```
python Main.py "<path_to_log_file>" "<path_to_matcher>"
```

Для деактивации виртуального окружения выполните команду

```
deactivate
```

