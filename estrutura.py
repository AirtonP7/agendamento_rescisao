import os

def gerar_estrutura_em_txt(caminho_pasta, nome_arquivo_saida="estrutura.txt"):
    with open(nome_arquivo_saida, "w", encoding="utf-8") as f:
        for raiz, dirs, arquivos in os.walk(caminho_pasta):
            nivel = raiz.replace(caminho_pasta, "").count(os.sep)
            indentacao = " " * 4 * nivel
            f.write(f"{indentacao}{os.path.basename(raiz)}/\n")
            for arquivo in arquivos:
                f.write(f"{indentacao}    {arquivo}\n")

# Exemplo de uso
pasta_alvo = r"C:\Users\TI-001555\Desktop\AIRTON CONTROLE\PROJETOS\agendamento_rescisao"
gerar_estrutura_em_txt(pasta_alvo)