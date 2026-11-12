#ifndef ARTEXLIB_H
#define ARTEXLIB_H

#pragma once

#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <variant>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <filesystem>
#include <regex>

using fs = std::fstream;
using string = std::string;

namespace ArtexDesktop
{
    void PrintError(int n, string msg)
    {
        std::cerr << "[ERRO] Artex" << n << " | " << msg << " ArtexError" << n << "\n";
    }

    class Ini
    {
    private:
        std::string filecontent;
        std::string filepath;
        std::vector<std::string> comments;
        std::vector<int> comment_lines;
        std::unordered_map<std::string, std::variant<int, float, std::string>> data;
    public:
        Ini(std::string &content, std::string &path)
            : filecontent(std::move(content)), filepath(std::move(path))
        {
            parse();
        }

        int parse()
        {
            if (filecontent.empty())
            {
                return 1;
            }


            const char *file = filecontent.c_str();

            /// Estados do Parser:
            /// 0 = Início / Aguardando chave
            /// 1 = Lendo conjuto
            /// 2 = Lendo chave
            /// 3 = Lendo valor
            /// 4 = Comentário

            std::regex Key_regex("^[a-zA-Z0-9]+$");

            int justwrite = 0;
            string set;
            string key;
            string value;
            int line = 1;

            for (size_t i = 0; i < filecontent.size(); i++)
            {
                char c = file[i];

                if (justwrite == 4)
                {
                    if (c != '\n') { continue; }
                    else { justwrite = 0; }
                }

                switch (c)
                {
                case '#':
                    if (justwrite == 3 && value.empty()){
                        PrintError(135, "Before commenting need to quote at least one value");
                    }
                    if (justwrite == 3 && !value.empty())
                    {

                    }
                    if (justwrite == 0)
                    {
                        justwrite = 4;
                    }
                    else
                    {
                        PrintError(131, "Failed to comment in invalid position");
                        return 1;
                    }
                    break;
                case '=':
                    if (justwrite == 2)
                    {
                        justwrite = 3;
                    }
                    else
                    {
                        PrintError(141, "Unexpected equals sign");
                        return 1;
                    }
                    break;

                case '\n':
                    switch (justwrite)
                    {
                    case 1:
                        PrintError(132, "A set cannot be created while having a line break");
                        break;
                    case 2:
                        PrintError(133, "A key cannot be created because of a line break");
                        break;
                    case 3:
                        if (value[0] == '\0' || value[0] == '\t')
                        {
                            PrintError(121, "the value is null or empty");
                        }
                        else if(std::regex_match(value, Key_regex)) {

                        }
                        break;
                    case 4:
                        comments.push_back(key);
                        comment_lines.push_back(line);
                        justwrite = 0;
                        break;
                    default:
                        break;
                    }
                    if (justwrite == 0){
                        key.clear();
                        value.clear();
                        line++;
                    }
                    break;
                case '[':
                    if (justwrite == 1){
                        PrintError(142, "one set was not created because another was already being created");
                    }
                    if (justwrite == 0){
                        justwrite = 1;
                    } else{
                        PrintError(134, "Another action is being executed while a set was almost created");
                    }
                    break;
                case ']':
                    if (justwrite == 1){
                        set = key;
                        key.erase();
                        justwrite = 0;
                    }
                    break;
                default:
                    if (c != ' ' || c != '\t'){
                        if (justwrite == 0)
                        {
                            justwrite = 2; // Começa a ler a chave
                            key += c;
                        }
                        else if (justwrite == 2)
                        {
                            key += c;
                        }
                        else if (justwrite == 3)
                        {
                            value += c; // Lendo o valor após o '='
                        }
                    }
                    break;
                }
            }

            if (!key.empty())
            {
                switch (justwrite)
                {
                case 1:
                    PrintError(115, "The file ended before it could finish listing a set");
                    break;
                case 2:
                    PrintError(116, "The file ended before a key could be fully defined.");
                case 3:
                    if (value[0] == '\0' || value[0] == '\t')
                    {
                        PrintError(121, "the value is null or empty");
                    }
                    else if (std::regex_match(value, Key_regex))
                    {
                    }
                    break;
                case 4:
                    comments.push_back(key);
                    comment_lines.push_back(line);
                    justwrite = 0;
                    break;
                default:
                    break;
                }
            }

            return 0;
        }

        // Método para recarregar caso o arquivo tenha mudado no disco
        int reload()
        {
        }

        // Escrever ou atualizar um valor na memória
        void set(const std::string &key, const std::variant<int, float, string> &value)
        {
        }

        // Salvar as alterações de volta para o arquivo no disco
        int writeToFile(const std::string &path = "")
        {
        }
    };

    // Função GetConfig separada e mantendo a flexibilidade para múltiplos arquivos
    inline Ini GetConfig(const std::string &ArtexConfigpath)
    {
        std::ifstream file(ArtexConfigpath, std::ios::binary);

        if (!file.is_open())
        {
            std::cerr << "[Erro] Nao foi possivel abrir o arquivo | " << ArtexConfigpath << "\n";
        }

        std::string filecontent = "";
        char buffer[4096];

        while (file.read(buffer, sizeof(buffer)) || file.gcount() > 0)
        {
            filecontent.append(buffer, file.gcount());
        }
    }

    inline string ArtexConfigFolderpath = "/.config/ArtexDesktop";

    inline string GetVersion()
    {
        return "0.0.1";
    }

    inline bool SetConfig()
    {
        return 0;
    }

    inline string GetUserPath()
    {
        const char *homeDir = std::getenv("HOME");
        if (homeDir)
        {
            return string(homeDir);
        }
        return "";
    }

    inline string GetUserName()
    {
        const char *user = std::getenv("USER");
        if (user)
        {
            return string(user);
        }
        return "";
    }

    inline void UpdateSystem(const string &distro)
    {
        if (distro == "arch")
        {
            std::system("sudo pacman -Syu --noconfirm");
        }
        else if (distro == "debian")
        {
            std::system("sudo apt upgrade -y");
        }
        else if (distro == "fedora")
        {
            std::system("sudo dnf upgrade --refresh -y");
        }
    }

    inline void _init()
    {
        ArtexConfigFolderpath = GetUserPath() + ArtexConfigFolderpath;
    }
}

#endif // ARTEXLIB_H