const SettingsPainel = document.getElementsByClassName("window")[0];
const NavBar = document.getElementById("NavCongigBar");
const saveBtn = document.getElementById("mySaveButton");

// ==========================================
// 1. CLASSE RESPONSÁVEL APENAS PELA API
// ==========================================
class ConfigAPI {
    constructor(baseUrl = "http://localhost:17104") {
        this.baseUrl = baseUrl;
    }

    async fetchConfigFilesList() {
        const response = await fetch(`${this.baseUrl}/api/configs`);
        if (!response.ok) throw new Error("Erro ao buscar lista de arquivos");
        const text = await response.text();
        return text.split(/\r?\n/).map(name => name.trim()).filter(Boolean);
    }

    async fetchConfig(fileName) {
        const response = await fetch(`${this.baseUrl}/api/config?file=${fileName}`);
        if (!response.ok) throw new Error(`Erro ao carregar ${fileName}.ini`);
        return await response.text();
    }

    async saveConfig(fileName, iniOutput) {
        const response = await fetch(`${this.baseUrl}/api/config?file=${fileName}`, {
            method: "POST",
            headers: { "Content-Type": "text/plain" },
            body: iniOutput
        });
        if (!response.ok) throw new Error(`Erro ao salvar ${fileName}.ini`);
        return response;
    }

    sendShutdown() {
        navigator.sendBeacon(`${this.baseUrl}/api/shutdown`);
    }
}


// ==========================================
// 2. CLASSE RESPONSÁVEL APENAS PELA INTERFACE (UI)
// ==========================================
class ConfigUIBuilder {
    constructor(panelContainer, navBarContainer) {
        this.panelContainer = panelContainer;
        this.navBarContainer = navBarContainer;
        this.pages = [];
    }

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

    openTab(tab) {
        const targetId = tab + "-config";
        this.pages.forEach(page => {
            page.style.display = (page.id === targetId) ? "block" : "none";
        });
    }

    generateINIText(pageDiv) {
        let iniOutput = "";
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

        return iniOutput;
    }
}


// ==========================================
// 3. CLASSE PRINCIPAL (SETTINGS MANAGER)
// ==========================================
class SettingsManager {
    constructor() {
        this.api = new ConfigAPI();
        this.ui = new ConfigUIBuilder(SettingsPainel, NavBar);
        this.configData = {};
    }

    // Lê linhas com comentários inline (ex: Theme = 0 # 0)
    parseINILine(line) {
        let comment = "";
        let content = line;

        // Separa valor real do comentário (# ou ;)
        const hashIdx = line.indexOf("#");
        const semiIdx = line.indexOf(";");
        let commentIdx = -1;

        if (hashIdx !== -1 && semiIdx !== -1) commentIdx = Math.min(hashIdx, semiIdx);
        else if (hashIdx !== -1) commentIdx = hashIdx;
        else if (semiIdx !== -1) commentIdx = semiIdx;

        if (commentIdx !== -1) {
            comment = line.substring(commentIdx + 1).trim(); // Valor default ou explicação
            content = line.substring(0, commentIdx).trim();
        }

        if (!content.includes("=")) return null;

        const parts = content.split("=");
        const key = parts[0].trim();
        const value = parts.slice(1).join("=").trim();

        return { key, value, defaultValue: comment };
    }

    parseAndBuildINIForFile(fileName, iniContent) {
        const pageDiv = this.ui.createPage(fileName, (id) => this.ui.openTab(id));

        this.configData[fileName] = {
            pageDiv: pageDiv,
            values: {}
        };

        // Guarda os pares chave-valor lidos do arquivo
        if (iniContent) {
            const lines = iniContent.split(/\r?\n/);
            for (let line of lines) {
                line = line.trim();
                if (!line || line.startsWith("#") || line.startsWith(";")) continue;

                const parsed = this.parseINILine(line);
                if (parsed) {
                    this.configData[fileName].values[parsed.key] = parsed;
                }
            }
        }

        // --- CONSTRUÇÃO MANUAL DA INTERFACE DA SUA PREFERÊNCIA ---
        if (fileName === "artex") {
            const fileValues = this.configData[fileName].values;

            const themeVal = fileValues["Theme"] ? fileValues["Theme"].value : "0";
            const hostVal = fileValues["localhost"] ? fileValues["localhost"].value : "127.0.0.17104";

            // Exemplo de criação manual dos campos:
            this.ui.createConfigField(pageDiv, fileName, "Theme", "text", themeVal);
            this.ui.createConfigField(pageDiv, fileName, "localhost", "text", hostVal);
        }
        if (fileName == "Hyprland") {
            const fileValues = this.configData[fileName].values;
        }
    }

    async loadAllConfigs() {
        try {
            const files = await this.api.fetchConfigFilesList();
            for (const fileName of files) {
                const iniText = await this.api.fetchConfig(fileName);
                this.parseAndBuildINIForFile(fileName, iniText);
            }
            if (files.length > 0) this.ui.openTab(files[0]);
        } catch (err) {
            console.error("Erro ao carregar configurações:", err);
        }
    }

    async saveAllConfigs(devMode = false) {
        for (const fileName in this.configData) {
            const pageDiv = this.configData[fileName].pageDiv;
            const iniOutput = this.ui.generateINIText(pageDiv);

            if (devMode) {
                console.log(`[DevMode] Salvando ${fileName}.ini:\n`, iniOutput);
            } else {
                await this.api.saveConfig(fileName, iniOutput);
                console.log(`[Produção] ${fileName}.ini salvo com sucesso!`);
            }
        }
    }
}

// ==========================================
// FUNÇÃO MAIN COM MODO DEV
// ==========================================
function main(DevMode) {
    const settings = new SettingsManager();

    if (DevMode) {
        console.log("--- DEV MODE ---");

        // Simula o conteúdo retornado dos arquivos .ini com comentários e valores default
        const mockArtexINI = `[Geral]
Theme = 0 # 0
localhost = 127.0.0.17104 # 127.0.0.17104`;

        // Carrega e monta a UI normalmente (sem chamar a API real)
        settings.parseAndBuildINIForFile("artex", mockArtexINI);
        settings.ui.openTab("artex");

        // Evento do botão de salvar para o DevMode
        if (saveBtn) {
            saveBtn.onclick = () => {
                settings.saveAllConfigs(true); // Apenas printa no console sem requisições HTTP
            };
        }
    } else {
        // Modo de Produção Normal
        settings.loadAllConfigs();


        if (saveBtn) {
            saveBtn.onclick = () => {
                settings.saveAllConfigs(false);
            };
        }
    }
}

// Executando em modo Dev para testes
main(false);