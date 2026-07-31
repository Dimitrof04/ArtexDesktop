-- Defina o caminho completo para o arquivo (substitua 'seu_usuario' pelo seu nome de usuário real)
local MenuDesktop = "/home/seu_usuario/.config/DesktopDimitrof04Apps/DektopConfigMenu.py"

-- Coloque os comandos como strings dentro da tabela
local Autoboot = {
    "waybar",
    "nm-applet", -- Substituído 'NetwokManager' pelo comando gráfico comum ou o binário correto
    "awww-daemon",
}

hl.on("hyprland.start", function()
    os.execute("chmod +x " .. MenuDesktop)
    -- Itera corretamente sobre a tabela usando ipairs
    for _, Comand in ipairs(Autoboot) do
        os.execute(Comand .. " &") -- Executa o comando em segundo plano
    end
end)