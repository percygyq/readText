::conda activate base
pyinstaller -F .\main.py --name=readText

::generate requirements.txt
::pipreqs ./ --encoding=utf8 --force