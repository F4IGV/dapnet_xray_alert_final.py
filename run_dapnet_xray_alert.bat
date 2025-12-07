@echo off
REM Lance le script Python pour envoyer la météo solaire sur DAPNET
cd /d "C:\Scripts\DAPNET"   #choose your folder who contain the .py file

py "dapnet_xray_alert.py" >> "C:\Scripts\DAPNET\dapnet_xray_alert.log" 2>&1
