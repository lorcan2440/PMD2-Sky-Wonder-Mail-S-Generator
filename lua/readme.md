## Lua - copy-paste Wonder Mail S passwords into Desmume ROM

This is a tool for quickly inputting Wonder Mail S passwords into the game. Some compatibility issues between versions here, but it does work!

### How to use

- Copy a Wonder Mail S password to your clipboard (Ctrl + C)
- Run this Lua script from Desmume
- Go to the in-game screen where you enter a Wonder Mail S password
- Press Ctrl + V while the password entry is empty and the cursor is in the first position (click anywhere on the screen after loading the script to ensure you are in the Desmume window)
- The password should fill itself in from the clipboard - just click END to verify the WMS
- Don't click the touchscreen while the password is filling.


### Requirements to use correctly:

- Windows 10 (64-bit)
- Desmume x86 (32-bit, not 64-bit!)
   (https://sourceforge.net/projects/desmume/files/desmume/0.9.11/desmume-0.9.11-win32.zip/download)
- lua51.dll (32-bit)
   (found as "lua5.1.dll" in https://sourceforge.net/projects/luabinaries/files/5.1.5/Windows%20Libraries/Dynamic/lua-5.1.5_Win32_dll14_lib.zip/download)
- clipboard.dll (this is a Windows 32-bit library, hence all the trouble in compatibility)
   (provided here, sourced from http://files.luaforge.net/releases/jaslatrix/clipboard/1.0.0/clipboard-1.0.0-Lua51.zip)
- In Desmume, make sure frame skip is zero (never)

### Errors:

- `DLL load failed: %1 is not a valid Win32 application`
   means there is a 64-bit / 32-bit mismatch. Ensure all three files (emulator, lua, clipboard) are the 32-bit ones.
   https://stackoverflow.com/questions/19019720/importerror-dll-load-failed-1-is-not-a-valid-win32-application-but-the-dlls
- `lua51.dll was not found. Please get it into your PATH or in the same directory as desmume.exe.`
   Ensure you are using the exact same files as described above - ensure the names are exact.
   Ensure the lua51.dll file is located in the same directory as the DeSmuME_0.9.11_x86.exe.
   If you want to move your lua51.dll file, you can instead add its directory
   to the System Environment Variables (Path).
   https://sourceforge.net/p/desmume/bugs/1628/
   
### Notes:

- This is not intended for TAS - it takes a few seconds to enter the code, which is limited by the touchscreen's sensitivity to fast taps. In theory the password could be entered instantly if the script directly edited the memory, but this is too complicated for me and isn't how this script works.
