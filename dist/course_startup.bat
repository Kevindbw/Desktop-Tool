@echo off
if "%1" == "h" goto begin
mshta vbscript:createobject("wscript.shell").run("""%~0"" h",0)(window.close)&&exit
:begin
cd /d "D:\67678\Develop\Desktop-Tool\dist"
"D:\67678\Develop\Desktop-Tool\dist\Course.exe"
