@echo OFF
echo %t1
echo Stopping old ServiceName version...
net stop "fbr"
echo Uninstalling old ServiceName version...
sc delete "fbr"


pause