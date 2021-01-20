-- https://learnxinyminutes.com/docs/ru-ru/lua-ru/ ссылка для быстрого ознакомления с основами языка LUA

-- This script changes LEDs colors in a random manner

-- Simplification and caching table.unpack calls
local unpack = table.unpack
-- Base pcb number of RGB LEDs
local ledNumber = 4
-- RGB LED control port initialize
local leds = Ledbar.new(ledNumber)

-- Function changes color on all LEDs
local function changeColor(col)
    for i=0, ledNumber - 1, 1 do
        leds:set(i, unpack(col))
    end
end

-- Functions that stops LEDs Timer and switches all LEDs to red
local function emergency()
    -- Stopping timer
    timerRandomLED:stop()
    -- Changing LEDs color after 1 second since timer function will be called
    -- 1 more timer after it is stopped
    Timer.callLater(1, function () changeColor({1, 0, 0}) end)
end

-- Event processing function called automatically by autopilot
function callback(event)
    -- Calls emergency() when voltage on the battery drops below Flight_com_landingVol value
    if (event == Ev.LOW_VOLTAGE2) then
        emergency()
    end
end

-- Creating timer, that changes each LED value to a random value every second
timerRandomLED = Timer.new(1, function ()
    -- Generating random value for each parameter in RGB form
    color = {math.random(), math.random(), math.random()}
    -- Calling color change function with generated values
    changeColor(color)
end)
-- Starting timer created above
timerRandomLED:start()

