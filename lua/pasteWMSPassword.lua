--[[
A lot of compatibility issues between versions here, but it can work.
Requirements to use correctly:

-- Desmume x86 (32-bit, not 64-bit!)
   (https://sourceforge.net/projects/desmume/files/desmume/0.9.11/desmume-0.9.11-win32.zip/download)

-- lua51.dll (32-bit)
   (found as "lua5.1.dll" in https://sourceforge.net/projects/luabinaries/files/5.1.5/Windows%20Libraries/Dynamic/lua-5.1.5_Win32_dll14_lib.zip/download)

-- clipboard.dll (this is a 32-bit library, hence all the trouble in compatibility)
   (provided here, or found in http://files.luaforge.net/releases/jaslatrix/clipboard/1.0.0/clipboard-1.0.0-Lua51.zip)

Errors: 
-- "DLL load failed: %1 is not a valid Win32 application"
   it means there is a 64-bit / 32-bit mismatch. Ensure all three files (emulator, lua, clipboard) are the 32-bit ones.
   https://stackoverflow.com/questions/19019720/importerror-dll-load-failed-1-is-not-a-valid-win32-application-but-the-dlls

-- "lua51.dll was not found. Please get it into your PATH or in the same directory as desmume.exe."
   Ensure you are using the exact same files as described above - ensure the names are exact.
   Ensure the lua51.dll file is located in the same directory as the DeSmuME_0.9.11_x86.exe.
   If you want to move your lua51.dll file, you can instead add its directory
   to the System Environment Variables (Path).
   https://sourceforge.net/p/desmume/bugs/1628/

How to use:
-- Copy a Wonder Mail S password to your clipboard (Ctrl + C)
-- Run this Lua script from Desmume
-- Go to the in-game screen where you enter a Wonder Mail S password
-- Press Ctrl + V while the password entry is empty and the cursor is in the first position
-- The password should fill itself in from the clipboard - just click END to verify the WM
-- Don't click the touchscreen while the password is filling.
]]--

-- lib
require 'clipboard'

-- positions of keys on screen
local xPos = {["C"] = 86, ["F"] = 130, ["H"] = 160, ["J"] = 190, ["K"] = 205, ["M"] = 234,
    ["N"] = 56, ["P"] = 86, ["Q"] = 100, ["R"] = 116, ["S"] = 132, ["T"] = 144, ["W"] = 190,
    ["X"] = 205, ["Y"] = 219, ["0"] = 56, ["1"] = 71, ["2"] = 86, ["3"] = 100, ["4"] = 116,
    ["5"] = 132, ["6"] = 144, ["7"] = 160, ["8"] = 175, ["9"] = 190, ["@"] = 205, ["&"] = 234,
    ["-"] = 56, ["#"] = 86, ["%"] = 116, ["+"] = 175, ["="] = 205}

local yPos = {["C"] = 129, ["F"] = 129, ["H"] = 129, ["J"] = 129, ["K"] = 129, ["M"] = 129,
    ["N"] = 143, ["P"] = 143, ["Q"] = 143, ["R"] = 143, ["S"] = 143, ["T"] = 143, ["W"] = 143,
    ["X"] = 143, ["Y"] = 143, ["0"] = 155, ["1"] = 155, ["2"] = 155, ["3"] = 155, ["4"] = 155,
    ["5"] = 155, ["6"] = 155, ["7"] = 155, ["8"] = 155, ["9"] = 155, ["@"] = 155, ["&"] = 155,
    ["-"] = 169, ["#"] = 169, ["%"] = 169, ["+"] = 169, ["="] = 169}

function sleep (a) 
    local sec = tonumber(os.clock() + a); 
    while (os.clock() < sec) do 
    end 
end

-- get code copied to clipboard
while true do
    local key = input.get()
    if key.control and key.V then
        clipboardContent = clipboard.gettext()
        print("Entering code: " .. clipboardContent)  -- give debug message
        password = string.gsub(clipboardContent, '%s', '')  -- clean string
        for i = 0, #password do
            local char = password:sub(i,i)
            print(char)
            -- trial and error to time the delays right - seems to work
            stylus.set{x=xPos[char], y=yPos[char], touch=true}
            emu.frameadvance()
            stylus.set{x=xPos[char], y=yPos[char], touch=true}
            emu.frameadvance()
            stylus.set{x=xPos[char], y=yPos[char], touch=true}
            emu.frameadvance()
            stylus.set{x=xPos[char], y=yPos[char], touch=false}
            emu.frameadvance()
            emu.frameadvance()
            emu.frameadvance()
        end
    end
    emu.frameadvance()
end
