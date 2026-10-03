const SettingsPainel = document.getElementsByClassName("window")[0];
const NavBar = document.getElementById("NavCongigBar");

// ==========================================
// 1. CLASSE RESPONSÁVEL APENAS PELA API (REQUISIÇÕES)
// ==========================================
class ConfigAPI {
    constructor(baseUrl = "http://localhost:18080") {
        this.baseUrl = baseUrl;
    }

    // Carrega o arquivo INI
    async fetchConfig() {
        const response = await fetch(`${this.baseUrl}/api/config`);
        if (!response.ok) throw new Error("Erro ao carregar configurações");
        return await response.text();
    }

    // Salva a string formatada no backend
    async saveConfig(iniOutput) {
        const response = await fetch(`${this.baseUrl}/api/config`, {
            method: "POST",
            headers: { "Content-Type": "text/plain" },
            body: iniOutput
        });
        if (!response.ok) throw new Error("Erro ao salvar configurações");
        return response;
    }

    // Notifica o encerramento do backend
    sendShutdown(port = "18080") {
        navigator.sendBeacon(`http://localhost:${port}/api/shutdown`);
    }
}


// ==========================================
// 2. CLASSE RESPONSÁVEL APENAS PELA INTERFACE (DOM/UI)
// ==========================================
class ConfigUIBuilder {
    constructor(panelContainer, navBarContainer) {
        this.panelContainer = panelContainer;
        this.navBarContainer = navBarContainer;
        this.pages = [];
    }

    // Cria uma aba/página visual
    createPage(id, onTabClick) {
        if (!id) return null;

        const pageButton = document.createElement("button");
        const pageDiv = document.createElement("div");

        pageButton.innerText = id;
        pageDiv.id = id + "-config";
        
        pageDiv.classList.add("sentings");
        pageDiv.style.display = "none";

        const title = document.createElement("h1");
        title.innerText = id;
        pageDiv.appendChild(title);

        pageButton.onclick = () => onTabClick(id);

        this.navBarContainer.appendChild(pageButton);
        this.panelContainer.appendChild(pageDiv);

        this.pages.push(pageDiv);

        return pageDiv;
    }

    // Adiciona um campo de configuração dentro de uma página
    createConfigField(pageDiv, sectionId, name, type, value, minValue = 0, maxValue = 100) {
        const configTitle = document.createElement("h2");
        configTitle.innerText = name;
        pageDiv.appendChild(configTitle);

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

        input.dataset.section = sectionId;
        input.dataset.key = name;

        pageDiv.appendChild(input);
        return input;
    }

    // Alterna a visibilidade das abas
    openTab(tab) {
        const targetId = tab + "-config";
        this.pages.forEach(page => {
            page.style.display = (page.id === targetId) ? "block" : "none";
        });
    }

    // Lê os inputs do DOM e gera o texto no formato INI
    generateINIText() {
        let iniOutput = "";

        this.pages.forEach(pageDiv => {
            const sectionName = pageDiv.id.replace("-config", "");
            iniOutput += `[${sectionName}]\n`;

            const inputs = pageDiv.querySelectorAll("input");
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

        return iniOutput;
    }
}


// ==========================================
// 3. CLASSE PRINCIPAL (ORQUESTRADORA E PARSER)
// ==========================================
class SettingsManager {
    constructor() {
        this.api = new ConfigAPI();
        this.ui = new ConfigUIBuilder(SettingsPainel, NavBar);
        this.configData = {};
        
        this.initAutoShutdown();
    }

    // Lê a string INI e comanda a UI para construir os elementos
    parseAndBuildINI(iniContent) {
        const lines = iniContent.split(/\r?\n/);
        let currentSection = "";
        let currentPageDiv = null;

        for (let line of lines) {
            line = line.trim();

            if (!line || line.startsWith(";") || line.startsWith("#")) continue;

            if (line.startsWith("[") && line.endsWith("]")) {
                currentSection = line.substring(1, line.length - 1).trim();
                currentPageDiv = this.ui.createPage(currentSection, (id) => this.ui.openTab(id));
                this.configData[currentSection] = {};
            } 
            else if (line.includes("=") && currentSection) {
                const parts = line.split("=");
                const key = parts[0].trim();
                const value = parts.slice(1).join("=").trim();

                this.configData[currentSection][key] = value;

                let type = "text";
                if (value === "true" || value === "false") {
                    type = "checkbox";
                } else if (!isNaN(value) && value !== "") {
                    type = "range";
                }

                if (currentPageDiv) {
                    this.ui.createConfigField(currentPageDiv, currentSection, key, type, value, 0, 100);
                }
            }
        }

        const firstPage = Object.keys(this.configData)[0];
        if (firstPage) this.ui.openTab(firstPage);
    }

    // Carrega dados da API e repassa para o parser
    async loadConfig() {
        try {
            const iniText = await this.api.fetchConfig();
            this.parseAndBuildINI(iniText);
        } catch (err) {
            console.error("Erro ao carregar o arquivo:", err);
        }
    }

    // Coleta dados da UI e envia para a API
    async saveConfig() {
        try {
            const iniOutput = this.ui.generateINIText();
            await this.api.saveConfig(iniOutput);
            console.log("Configurações salvas com sucesso!");
        } catch (err) {
            console.error("Erro ao enviar configurações:", err);
        }
    }

    // Configura eventos de encerramento
    initAutoShutdown() {
        window.addEventListener("pagehide", () => this.api.sendShutdown("18080"));
        window.addEventListener("beforeunload", () => this.api.sendShutdown("17104"));
    }
}

function main(DevMode) {
    const settings = new SettingsManager();

    if (DevMode) {
        
    } else {
        settings.loadConfig();

        const saveBtn = document.getElementById("mySaveButton");
        if (saveBtn) {
            saveBtn.onclick = () => settings.saveConfig();
        }
    }
}

main(true)