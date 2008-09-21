@echo off
set /P action="Do you want to Install (I) or Uninstall (U) the service? "
if /I '%action:~0,1%' equ 'i' goto install
if /I '%action:~0,1%' equ 'u' goto uninstall
echo.
echo ERROR: an option other than I or U was chosen.
pause
exit /b 1
:install
instsrv impserve "%~dp0srvany.exe"
reg add HKLM\SYSTEM\CurrentControlSet\Services\impserve /v Description /d "Local content server and Internet proxy for the 1150/1200 ebooks" /f
reg add HKLM\SYSTEM\CurrentControlSet\Services\impserve /v ImagePath /d "\"%~dp0srvany.exe\"" /f
reg add HKLM\SYSTEM\CurrentControlSet\Services\impserve\Parameters /f
reg add HKLM\SYSTEM\CurrentControlSet\Services\impserve\Parameters /v Application /d "\"%~dp0impserve.exe\"" /f
reg add HKLM\SYSTEM\CurrentControlSet\Services\impserve\Parameters /v AppParameters /d "-l \"%~dp0\impserve.log\"" /f
reg add HKLM\SYSTEM\CurrentControlSet\Services\impserve\Parameters /v AppDirectory /d "\"%~dp0\"" /f
net start impserve
pause
exit /b 0
:uninstall
net stop impserve
instsrv impserve REMOVE
pause
exit /b 0
