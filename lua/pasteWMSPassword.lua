--[[
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

-- get code copied to clipboard
while true do
    local key = input.get()
    if key.control and key.V then
        clipboardContent = clipboard.gettext()
        print("Entering code: " .. clipboardContent)  -- give debug message
        password = string.gsub(clipboardContent, '%s', '')  -- clean string
        for i = 0, #password do
            local char = password:sub(i,i)
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
