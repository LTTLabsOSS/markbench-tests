@echo off
for /l %%i in (1,1,30) do (
    .\flac-1.4.3-win\Win64\flac.exe --best nin-theslip.wav -f -o output
)