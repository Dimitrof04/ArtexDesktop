-- Defina o caminho completo para o arquivo (substitua 'seu_usuario' pelo seu nome de usuário real)
local MenuDesktop = "~/.config/DesktopDimitrof04Apps/DektopConfigMenu.py"
local StartMenu   = "~/.config/DesktopDimitrof04Apps/StartMenu.py"
-- Coloque os comandos como strings dentro da tabela
local Autoboot = {
    "waybar",
    "nm-applet", -- Substituído 'NetwokManager' pelo comando gráfico comum ou o binário correto
    "awww-daemon",
}

hl.on("hyprland.start", function()
    os.execute("chmod +x " .. MenuDesktop)
    os.execute("chmod +x " .. StartMenu)
    -- Itera corretamente sobre a tabela usando ipairs
    for _, Comand in ipairs(Autoboot) do
        os.execute(Comand .. " &") -- Executa o comando em segundo plano
    end
end)