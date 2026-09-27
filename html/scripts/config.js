const SenntingsPainel = document.getElementsByClassName("window")[0];
const NavBar = document.getElementById("NavCongigBar");

class Settings {
    constructor() {
        this.pages = [];
        this.configData = {}; // Objeto para controlar o estado
    }

    createPage(id) {
        if (!id) return;

        const PageButton = document.createElement("button");
        const Pagediv = document.createElement("div");

        PageButton.innerText = id;
        Pagediv.id = id + "-config";
        
        // Classe CSS solicitada
        Pagediv.classList.add("sentings");
        Pagediv.style.display = "none";

        const Title = document.createElement("h1");
        Title.innerText = id;
        Pagediv.appendChild(Title);

        PageButton.onclick = () => this.openTab(id);

        NavBar.appendChild(PageButton);
        SenntingsPainel.appendChild(Pagediv);

        this.pages.push(Pagediv);

        return {
            createConfig: (name, type, value, minValue = 0, maxValue = 100) => {
                const ConfigTitle = document.createElement("h2");
                ConfigTitle.innerText = name;
                Pagediv.appendChild(ConfigTitle);

                let input;

                if (type === "range" || type === "scroll") {
                    input = document.createElement("input");
                    input.type = "range";
                    input.min = minValue;
                    input.max = maxValue;
                    input.value = value;
                } else if (type === "checkbox" || type === "toggle") {
                    input = document.createElement("input");
                    input.type = "checkbox";
                    input.checked = (value === "true" || value === true);
                } else {
                    input = document.createElement("input");
                    input.type = "text";
                    input.value = value;
                }

                // Identificadores no elemento DOM para leitura na hora de salvar
                input.dataset.section = id;
                input.dataset.key = name;

                Pagediv.appendChild(input);
            }
        };
    }

    openTab(tab) {
        const targetId = tab + "-config";
        this.pages.forEach(page => {
            page.style.display = (page.id === targetId) ? "block" : "none";
        });
    }

    // --- LEITOR PRÓPRIO DE INI (SEM BIBLIOTECAS) ---
    initAutoShutdown() {
        window.addEventListener("pagehide", () => {
            navigator.sendBeacon("http://localhost:18080/api/shutdown");
        });
    }

    parseAndBuildINI(iniContent) {
        const lines = iniContent.split(/\r?\n/);
        let currentSection = "";
        let currentPage = null;

        for (let line of lines) {
            line = line.trim();

            // Ignora linhas vazias e comentários
            if (!line || line.startsWith(";") || line.startsWith("#")) continue;

            // Detecta Nova Aba: [NomeDaAba]
            if (line.startsWith("[") && line.endsWith("]")) {
                currentSection = line.substring(1, line.length - 1).trim();
                currentPage = this.createPage(currentSection);
                this.configData[currentSection] = {};
            } 
            // Detecta Chave = Valor
            else if (line.includes("=") && currentSection) {
                const parts = line.split("=");
                const key = parts[0].trim();
                const value = parts.slice(1).join("=").trim(); // Preserva sinais de '=' no valor se houver

                this.configData[currentSection][key] = value;

                // Auto-Detector de Tipos de Input
                let type = "text";
                if (value === "true" || value === "false") {
                    type = "checkbox";
                } else if (!isNaN(value) && value !== "") {
                    type = "range";
                }

                if (currentPage) {
                    currentPage.createConfig(key, type, value, 0, 100);
                }
            }
        }

        // Abre a primeira página criada automaticamente
        const firstPage = Object.keys(this.configData)[0];
        if (firstPage) this.openTab(firstPage);
    }

    // Busca o arquivo INI no backend C++
    async loadConfigFromAPI() {
        try {
            const response = await fetch("http://localhost:18080/api/config");
            const iniText = await response.text();
            this.parseAndBuildINI(iniText);
        } catch (err) {
            console.error("Erro ao carregar o arquivo do C++:", err);
        }
    }

    // --- FUNÇÃO PARA LER OS DADOS ATUAIS E SALVAR NA API ---
    async saveConfigToAPI() {
        let iniOutput = "";

        // Percorre todas as abas criadas no DOM
        this.pages.forEach(pagediv => {
            const sectionName = pagediv.id.replace("-config", "");
            iniOutput += `[${sectionName}]\n`;

            // Pega todos os inputs dentro desta aba
            const inputs = pagediv.querySelectorAll("input");
            inputs.forEach(input => {
                const key = input.dataset.key;
                let value;

                if (input.type === "checkbox") {
                    value = input.checked ? "true" : "false";
                } else {
                    value = input.value;
                }

                if (key) {
                    iniOutput += `${key} = ${value}\n`;
                }
            });

            iniOutput += "\n";
        });

        // Envia a string formatada no formato INI via POST para a API C++
        try {
            const response = await fetch("http://localhost:18080/api/config", {
                method: "POST",
                headers: { "Content-Type": "text/plain" },
                body: iniOutput
            });

            if (response.ok) {
                console.log("Configurações salvas com sucesso no ~/.config/ArtexDesktop/Hyprland/Config.ini!");
            }
        } catch (err) {
            console.error("Erro ao enviar configurações para a API:", err);
        }
    }
}

// Inicializa e carrega a interface
const settings = new Settings();
settings.loadConfigFromAPI();

// Envia um aviso para fechar o backend ao fechar a aba/janela
window.addEventListener("beforeunload", () => {
    navigator.sendBeacon("http://localhost:17104/api/shutdown");
});