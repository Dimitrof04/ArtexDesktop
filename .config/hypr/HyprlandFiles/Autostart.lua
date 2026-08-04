local Autoboot = {
    "nm-applet",
    "awww-daemon",
    "ArtexDesktop --ShellBar -i"
}

hl.on("hyprland.start", function()
    for _, Comand in ipairs(Autoboot) do
        os.execute(Comand .. " &")
    end
end)
