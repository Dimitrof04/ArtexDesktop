#include <iostream>
#include <vector>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <string>
#include <cstdlib>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <sys/stat.h>

const int PORT = 17104;

std::string get_config_path() {
    const char *home = std::getenv("HOME");
    std::string dir_path = std::string(home) + "/.config/ArtexDesktop/";
    mkdir((std::string(home) + "/.config").c_str(), 0755);
    mkdir(dir_path.c_str(), 0755);
    return dir_path + "/Config.ini";
}

std::string get_mime_type(const std::string &path) {
    if (path.rfind(".html") != std::string::npos) return "text/html";
    if (path.rfind(".css") != std::string::npos) return "text/css";
    if (path.rfind(".js") != std::string::npos) return "application/javascript";
    if (path.rfind(".png") != std::string::npos) return "image/png";
    if (path.rfind(".jpg") != std::string::npos || path.rfind(".jpeg") != std::string::npos) return "image/jpeg";
    if (path.rfind(".svg") != std::string::npos) return "image/svg+xml";
    return "text/plain";
}

void serve_file(int client_socket, const std::string &file_path) {
    std::ifstream file(file_path, std::ios::binary);
    if (!file.is_open()) {
        std::string response = "HTTP/1.1 404 Not Found\r\n\r\nArquivo nao encontrado!";
        send(client_socket, response.c_str(), response.length(), 0);
        return;
    }

    std::stringstream buffer;
    buffer << file.rdbuf();
    std::string content = buffer.str();
    std::string mime = get_mime_type(file_path);

    std::string header = "HTTP/1.1 200 OK\r\nContent-Type: " + mime +
                         "\r\nContent-Length: " + std::to_string(content.length()) +
                         "\r\nAccess-Control-Allow-Origin: *\r\n\r\n";

    send(client_socket, header.c_str(), header.length(), 0);
    send(client_socket, content.c_str(), content.length(), 0);
}

int main() {
    bool SeverIsRun = true;
    std::string config_path = get_config_path();

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        std::cerr << "[ERRO] Porta " << PORT << " ocupada!" << std::endl;
        return 1;
    }

    listen(server_fd, 10);
    std::cout << "ArtexDesktop Config rodando na porta " << PORT << "..." << std::endl;

    #ifdef __linux__
        std::string open_cmd = "sleep 0.2 && xdg-open http://localhost:" + std::to_string(PORT) + " &";
        std::system(open_cmd.c_str());
    #endif

    while (SeverIsRun) {
        int addrlen = sizeof(address);
        int new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t *)&addrlen);
        if (new_socket < 0) continue;

        char buffer[8192] = {0};
        int bytes_read = read(new_socket, buffer, sizeof(buffer) - 1);

        if (bytes_read > 0) {
            std::string request(buffer, bytes_read);

            // ROTA DE DESLIGAMENTO
            if (request.find("POST /api/shutdown") != std::string::npos) {
                std::string response = "HTTP/1.1 200 OK\r\nAccess-Control-Allow-Origin: *\r\n\r\nSERVER_CLOSED";
                send(new_socket, response.c_str(), response.length(), 0);
                close(new_socket);
                SeverIsRun = false;
                break;
            }
            // LER CONFIGURAÇÃO INI
            else if (request.find("GET /api/config") != std::string::npos) {
                serve_file(new_socket, config_path);
            }
            // GRAVAR CONFIGURAÇÃO INI
            else if (request.find("POST /api/config") != std::string::npos) {
                size_t body_pos = request.find("\r\n\r\n");
                if (body_pos != std::string::npos) {
                    std::string body = request.substr(body_pos + 4);
                    std::ofstream file(config_path, std::ios::trunc);
                    file << body;
                }
                std::string response = "HTTP/1.1 200 OK\r\nAccess-Control-Allow-Origin: *\r\n\r\nOK";
                send(new_socket, response.c_str(), response.length(), 0);
            }
            // SERVIR INDEX.HTML
            else if (request.find("GET / ") != std::string::npos) {
                serve_file(new_socket, "index.html");
            }
            // SERVIR ARQUIVOS ESTÁTICOS (.js, .css, etc.)
            else if (request.find("GET /") != std::string::npos) {
                size_t start = request.find("GET /") + 5;
                size_t end = request.find(" ", start);
                std::string requested_path = request.substr(start, end - start);
                serve_file(new_socket, requested_path);
            }
        }

        close(new_socket);
    }

    close(server_fd);
    return 0;
}