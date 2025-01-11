@echo OFF
echo %t1
echo Stopping old ServiceName version...
net stop "fbr"
echo Uninstalling old ServiceName version...
sc delete "fbr"

echo Installing new ServiceName...
rem DO NOT remove the space after "binpath="!
sc create "fbr" binpath= "D:\ZK\fbr.exe" start= auto

echo Configring ServiceName
sc config "fbr"  start= auto 
sc config "fbr" obj= .\test Password= Ahmed2219990
sc description "fbr" "FBR Push data to Server Created By Ahmed Maher"
net start fbr
echo Starting fbr complete
pause