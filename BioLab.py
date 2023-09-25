from datetime import datetime
import sys
import time
import os
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency
import warnings


########################################################################################################################
#                                   GERENCIADOR DE AMOSTRAS:    ( Ponto ! )
########################################################################################################################

class Amostra:
     def __init__(self,  paciente, exame, identificacao, data_hora):
        self.paciente = paciente
        self.exame = exame
        self.data_hora = data_hora
        self.identificacao = identificacao
        self.resultado = None


class Database:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def execute(self, query, values=None):
        if values:
            self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)
        self.connection.commit()

    def fetch_all(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()

    def obter_todos_os_dados(self):
        try:
            query = "SELECT * FROM amostras"
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            dados_formatados = [f"{linha[1]}, {linha[2]}, {linha[3]}, {linha[4]}, {linha[5]}" for linha in result]
            return dados_formatados

        except Exception as error:
            print(f"ERRO: Falha ao obter todos os dados -> {error}\n")
            return []

    def amostra_existe(self, paciente, exame, identificacao, resultado=None):
        try:
            query = "SELECT COUNT(*) FROM amostras WHERE paciente = ? AND exame = ? AND identificacao = ? AND resultado = ?"
            values = (paciente, exame, identificacao, resultado)
            self.cursor.execute(query, values)
            count = self.cursor.fetchone()[0]
            return count > 0

        except Exception as error:
            print(f"ERRO: Falha ao verificar amostra -> {error}\n")
            return False

    def adicionar_amostra(self, paciente, exame, identificacao, data_hora, resultado):
        try:
            if not self.verificar_amostra_existente(paciente, identificacao):
                self.cursor.execute("""
                    INSERT INTO amostras (paciente, exame, identificacao, data_hora, resultado)
                    VALUES (?, ?, ?, ?, ?)
                """, (paciente, exame, identificacao, data_hora, resultado))
                self.connection.commit()
                print("\n[ Amostra Adicionada com Sucesso ]\n")
            else:
                print("\nERRO: Amostra já existe no banco de dados.\n")
        except Exception as error:
            print(f"ERRO: Falha ao adicionar amostra -> {error}\n")

    def verificar_amostra_existente(self, paciente, identificacao):
        self.cursor.execute("SELECT paciente AND identificacao FROM amostras WHERE paciente = ? AND identificacao = ?", (paciente, identificacao,))
        return self.cursor.fetchone() is not None

    def deletar_todas_amostras(self):
        try:
            query = "DELETE FROM amostras"
            self.execute(query)
            print("-> Todas as amostras foram deletadas do banco de dados.\n")
            linhareta()

        except Exception as error:
            print(f"ERRO: Falha ao limpar Banco de dados -> {error}\n")
            linhareta()

    def equipamento_existe(self, equipamento, exame, padrao):
        try:
            query = "SELECT COUNT(*) FROM equipamentos WHERE equipamento = ? AND exame = ? AND padrao = ?"
            values = (equipamento, exame, padrao)
            self.cursor.execute(query, values)
            count = self.cursor.fetchone()[0]
            return count > 0

        except Exception as error:
            print(f"ERRO: Falha ao verificar equipamento -> {error}\n")
            return False

    def add_equipamento(self, equipamento, exame, padrao):
        try:
            if not self.equipamento_existe(equipamento, exame, padrao):
                query = "INSERT INTO equipamentos (equipamento, exame, padrao) VALUES (?, ?, ?)"
                values = (equipamento, exame, padrao)
                self.execute(query, values)
                print(f"-> Padrão do equipamento: {equipamento} Cadastrado com Sucesso.\n")

            else:
                print(f"-> Padrão do equipamento: {equipamento} Já existe no banco de dados! Ignorando duplicata.\n")

        except Exception as error:
            print(f"ERRO: Falha ao adicionar equipamento -> {error}\n")

    def deletar_todos_equipamentos(self):
        try:
            query = "DELETE FROM equipamentos"
            self.execute(query)
            print("-> Todos os Equipamentos foram deletados do banco de dados.\n")
            linhareta()

        except Exception as error:
            print(f"ERRO: Falha ao limpar Banco de dados -> {error}\n")
            linhareta()


class GerenciadorAmostras:
    def __init__(self, db):
        self.db = db

    def adicionar_amostra(self, paciente, exame, identificacao, data_hora, resultado=None):
        try:
            verificar = self.db.verificar_amostra_existente(paciente, identificacao)
            if not verificar:
                query = "INSERT INTO amostras (paciente, exame, identificacao, data_hora, resultado) VALUES (?, ?, ?, ?, ?)"
                values = (paciente, exame, identificacao, data_hora, resultado)
                self.db.execute(query, values)
                print(f"-> Amostra de {paciente}/{identificacao} adicionada com Sucesso.\n")
            else:
                print(f"-> Amostra de {paciente}/{identificacao} já existe no banco de dados. Ignorando duplicata.\n")

        except Exception as error:
            print(f"ERRO: Falha ao adicionar amostra -> {error}\n")

    def listar_amostras(self):
        query = "SELECT * FROM amostras"
        amostras = self.db.fetch_all(query)
        for amostra in amostras:
            print("------------------------------------------------------\n")
            print(f"    ¬ ID: {amostra[0]}\n    ¬ NOME DA AMOSTRA: {amostra[1]}\n    ¬ IDENTIFICAÇÃO DA AMOSTRA: {amostra[3]}\n    ¬ LOCAL DE ARMAZENAMENTO: {amostra[2]}\n    ¬ RESULTADO / LEMBRETES: {amostra[5]}\n    ¬ DATA E HORA: {amostra[4]}\n")

    def amostras_por_paciente(self, paciente, identificacao):
        if paciente:
            query = f"SELECT * FROM amostras WHERE paciente = '{paciente}'"
            amostras = self.db.fetch_all(query)
            for amostra in amostras:
                print("------------------------------------------------------\n")
                print(f"    ¬ ID: {amostra[0]}\n    ¬ NOME DA AMOSTRA: {amostra[1]}\n    ¬ IDENTIFICAÇÃO DA AMOSTRA: {amostra[3]}\n    ¬ LOCAL DE ARMAZENAMENTO: {amostra[2]}\n    ¬ RESULTADO / LEMBRETES: {amostra[5]}\n    ¬ DATA E HORA: {amostra[4]}\n")

        elif identificacao:
            query = f"SELECT * FROM amostras WHERE identificacao = '{identificacao}'"
            amostras = self.db.fetch_all(query)
            for amostra in amostras:
                print("------------------------------------------------------\n")
                print(f"    ¬ ID: {amostra[0]}\n    ¬ NOME DA AMOSTRA: {amostra[1]}\n    ¬ IDENTIFICAÇÃO DA AMOSTRA: {amostra[3]}\n    ¬ LOCAL DE ARMAZENAMENTO: {amostra[2]}\n    ¬ RESULTADO / LEMBRETES: {amostra[5]}\n    ¬ DATA E HORA: {amostra[4]}\n")

        else:
            print("Erro: DADOS INFORMADOS INCORRETAMENTE! Tente novamente.\n")

    def atualizar_resultado(self, id_amostra, resultado):
        query = "UPDATE amostras SET resultado = ? WHERE id = ?"
        values = (resultado, id_amostra)
        self.db.execute(query, values)
        print(f"-> Atualização do resultado/lembrete da amostra com ID {id_amostra} feita com Sucesso.\n")

    def deletar_amostras(self, id_amostra):
        query = "DELETE FROM amostras WHERE id = ?"
        self.db.execute(query, (id_amostra,))
        print(f"\n-> Amostra com ID {id_amostra} Deletada com Sucesso.\n")


########################################################################################################################
#                                     ANALIZADOR DE DADOS:      ( Pronto ! )
########################################################################################################################


class AnalizadorDados:
    def __init__(self):
        self.dados = None
        self.resultado = None

    def obter_dados_input(self):
        try:
            entrada = input("INSIRA os dados separados por vírgula: ")
            self.dados = [float(dado) for dado in entrada.split(',')]
            linhareta()

        except ValueError:
            print("ERRO: Insira os dados corretamente (números separados por vírgula).")

    def obter_dados_chi(self):
        try:
            nivel_significancia = float(input("DIGITE o Nível de significância (padrão = 0.05): "))
            linhareta()
            print("\n[*] INSIRA os dados da tabela de contingência:\n(linhas separadas por ';', colunas separadas por ',')\n")
            entrada = input("Dados: ")
            linhas = entrada.strip().split(';')
            self.dados = [list(map(float, linha.split(','))) for linha in linhas]
            linhareta()
            self.calcular_chi_quadrado(nivel_significancia)

        except ValueError:
            print("ERRO: Insira os dados corretamente (números separados por ',' e linhas separadas por ';').")

    def plot_box_plot(self, coluna):
        if self.dados is not None:
            try:
                df = pd.DataFrame({coluna: self.dados})

                plt.figure(figsize=(8, 6))
                sns.boxplot(data=df, y=coluna)
                plt.title(f'Box Plot de {coluna}')
                plt.show()

            except Exception as error:
                print(f"ERRO ao plotar box plot: {error}\n")
        else:
            print("Erro: Nenhum dado para analisar.\n")

    def plot_dot_plot(self, coluna):
        if self.dados is not None:
            try:
                df = pd.DataFrame({coluna: self.dados})

                plt.figure(figsize=(8, 6))
                sns.stripplot(data=df, y=coluna)
                plt.title(f'Dot Plot de {coluna}')
                plt.show()

            except Exception as error:
                print(f"ERRO ao plotar dot plot: {error}\n")
        else:
            print("Erro: Nenhum dado para analisar.\n")

    def calcular_intervalo_confianca(self, coluna, confianca=0.95):
        if self.dados is not None:
            try:
                df = pd.DataFrame(self.dados, columns=['Dados'])
                media = df['Dados'].mean()
                desvio_padrao = df['Dados'].std()
                tamanho_amostra = len(df)
                intervalo = stats.t.interval(confianca, df=tamanho_amostra - 1, loc=media, scale=desvio_padrao / np.sqrt(tamanho_amostra))
                print(f"[*] INTERVALO DE CONFIANÇA: (Nível de confiança {confianca * 100}%)\n")
                print(f"    ¬ Limite Inferior: {intervalo[0]}")
                print(f"    ¬ Limite Superior: {intervalo[1]}\n")
                linhareta()

            except Exception as error:
                print(f"ERRO: {error}\n")
        else:
            print("ERRO: Nenhum dado para analisar.\n")

    def calcular_chi_quadrado(self, nivel_significancia):
        if self.dados is not None:
            try:
                tabela_contingencia = pd.DataFrame(self.dados)
                chi2, p, dof, expected = chi2_contingency(tabela_contingencia)

                print(f"[!] TESTE DE QUI-QUADRADO:\n")
                print(f"    ¬ Qui-Quadrado Estatística: {chi2:.2f}")
                print(f"    ¬ Valor p: {p:.4f}")
                print(f"    ¬ Graus de Liberdade: {dof}")
                print(f"    ¬ Nível de Significância: {nivel_significancia:.2f}%\n\n")

                if p < nivel_significancia / 100:
                    print("[*] RESULTADO de hipóteses:\n    ¬ Aceitar a hipótese alternativa (HA)")
                else:
                    print("[*] RESULTADO de hipóteses:\n    ¬ Aceitar a hipótese nula (H0)")

                unique_values, obs_counts = np.unique(self.dados, return_counts=True)
                total_obs = obs_counts.sum()
                expected_frequencies = (obs_counts / total_obs) * total_obs

                plt.figure(figsize=(8, 6))
                #plt.bar(unique_values, expected_frequencies, label='Esperado', alpha=0.5)
                plt.bar(unique_values, obs_counts, label='Observado', alpha=0.5)
                plt.xlabel('Valores')
                plt.ylabel('Frequência')
                plt.title('Dados sobre a Frequência Observada')
                plt.legend()
                plt.show()

            except Exception as error:
                print(f"ERRO: {error}\n")
        else:
            print("ERRO: Nenhum dado para analisar.\n")

    def analizar_dados(self):
        if self.dados is not None:
            try:
                df = pd.DataFrame(self.dados, columns=['Dados'])

                media = df['Dados'].mean()
                desvio_padrao = df['Dados'].std()
                maximo = df['Dados'].max()
                minimo = df['Dados'].min()
                limite_superior = media + 2 * desvio_padrao
                limite_inferior = media - 2 * desvio_padrao

                print(f"[!] RESULTADOS DA ANÁLISE:\n\n    ¬ Média: {media}\n    ¬ Desvio Padrão: {desvio_padrao}\n    ¬ Máximo: {maximo}\n    ¬ Mínimo: {minimo}")
                print(f"    ¬ Limite Superior: {limite_superior}\n    ¬ Limite Inferior: {limite_inferior}\n")

                self.calcular_intervalo_confianca('Dados')
                self.plot_box_plot('Dados'), self.plot_dot_plot('Dados')
                linhareta()

            except Exception as error:
                print(f"ERRO: {error}\n")
        else:
            print("Erro: Nenhum dado para analisar.\n")


########################################################################################################################
#                                     CONTROLE DE QUALIDADE:   ( Pronto ! )
########################################################################################################################


class PadraoNaoCadastradoError(Exception):
    pass


class LaboratorioBiomedicina:
    def __init__(self, db2):
        self.db2 = db2

    def cadastrar_padrao(self, equipamento: str, exame: str, padrao: float):
        try:
            verificar = self.db2.equipamento_existe(equipamento, exame, padrao)
            if not verificar:
                query = "INSERT INTO equipamentos (equipamento, exame, padrao) VALUES (?, ?, ?)"
                values = (equipamento, exame, padrao)
                self.db2.execute(query, values)
                print(f"-> Padrão do equipamento: {equipamento} cadastrado com Sucesso.\n")

            else:
                print(f"-> Padrão do equipamento: {equipamento} já existe no banco de dados! Ignorando duplicata.\n")
        except Exception as error:
            print(f"ERRO: Falha ao adicionar Padrão de equipamento -> {error}\n")

    def comparar_configuracao(self, configuracao_estagiario):
        erros = []

        for equipamento_estagiario, exames in configuracao_estagiario.items():
            for exame, valor_amostra in exames.items():
                consulta = f"SELECT padrao FROM equipamentos WHERE equipamento = ? AND exame = ?"
                params = (equipamento_estagiario, exame)
                self.db2.execute(consulta, params)
                resultado = self.db2.cursor.fetchall()

                if resultado:
                    valor_padrao = resultado[0][0]
                    if valor_amostra != valor_padrao:
                        erro = {
                            "¬ EQUIPAMENTO": equipamento_estagiario,
                            "¬ EXAME/SUBSTÂNCIA": exame,
                            "¬ VALOR ESPERADO": valor_padrao,
                            "¬ VALOR DE SUA AMOSTRA": valor_amostra
                        }
                        erros.append(erro)
                else:
                    erro = {
                        "¬ EQUIPAMENTO": equipamento_estagiario,
                        "¬ EXAME/SUBSTÂNCIA": exame,
                        "¬ VALOR ESPERADO": "! Não Encontrado ou Não Cadastrado !",
                        "¬ VALOR DE SUA AMOSTRA": valor_amostra
                    }
                    erros.append(erro)

        return erros

    def deletar_equipamento(self, equipamento):
        query = "DELETE FROM equipamentos WHERE equipamento = ?"
        self.db2.execute(query, (equipamento,))
        print(f"\n-> Equipamento: {equipamento} Deletado com Sucesso.\n")
        linhareta()

########################################################################################################################


db = Database("BioLab.db")
db2 = Database("BioLab.db")

ger_amostras = GerenciadorAmostras(db)
anadados = AnalizadorDados()
laboratorio = LaboratorioBiomedicina(db2)


def database():
    db = Database("BioLab.db")
    db.execute("""
        CREATE TABLE IF NOT EXISTS amostras (
            id INTEGER PRIMARY KEY,
            paciente TEXT,
            exame TEXT,
            identificacao TEXT,
            data_hora TEXT,
            resultado TEXT
        )""")


def databaze():
    db2 = Database("BioLab.db")
    db2.execute("""
        CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY,
            equipamento TEXT,
            exame TEXT,
            padrao REAL
        )""")


def exportar_dados(db):
    try:
        data = datetime.now().strftime("%d-%m-%Y_%H-%M")
        nome_arquivo = f"{data}.txt"
        dados = db.obter_todos_os_dados()
        if dados:
            with open(nome_arquivo, "w") as file2:
                for linha in dados:
                    file2.write(linha + "\n")
            print(f"\n[ Dados Exportados com Sucesso para {nome_arquivo} ]")
        else:
            print("\nERRO: Nenhum dado a ser exportado. Apenas feche o programa\n")
            linhareta()
            time.sleep(5)
            opcoes_principal(db, db2)

    except Exception as error:
        print(f"ERRO: Falha ao exportar dados -> {error}\n")
        time.sleep(5)
        opcoes_principal(db, db2)


def limpar_tela():
    try:
        os.system("cls" if os.name == "nt" else "clear")

    except Exception as e:
        print(f"{e}\n")


def linhareta():
    linha_reta = "\u2500" * 95
    print(linha_reta, "\n")


def seabornn():
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=UserWarning)


def opcoes_principal(db, db2):
    try:
        opcao1 = input("[!] Digite o número da Opção [ENTER para confirmar]: ")
        if opcao1 == "1":
            try:

                print("[!] Digite o Nome do Arquivo na pasta (não esqueça de digitar [.txt] no final do nome)")
                print("(Ex: NomeArquivo.txt)\n")
                arquivo = input("Nome do Arquivo: ")
                linhareta()
                if arquivo:
                    with open(arquivo, "r") as file:
                        dados = file.read().splitlines()
                        for linha in dados:
                            campos = linha.split(", ")
                            if len(campos) == 5:
                                paciente, exame, identificacao, data_hora, resultado = campos
                                ger_amostras.adicionar_amostra(paciente, exame, identificacao, data_hora, resultado)
                                linhareta()
                            else:
                                print(f"ERRO: Linha com formato inválido: {linha}")
                    print("                         [ Dados Carregados com Sucesso ]\n")
                    linhareta()
                    time.sleep(5)
                    limpar_tela()
                    menu_principal(db, db2)
                else:
                    print("ERRO: Arquivo Não Encontrado! retornando ao menu principal...\n")
                    linhareta()
                    time.sleep(5)
                    limpar_tela()
                    menu_principal(db, db2)

            except Exception as error:
                print(f"ERRO: falha ao carregar os dados -> {error}\n")
                linhareta()
                time.sleep(3)
                opcoes_principal(db, db2)

        elif opcao1 == "2":
            limpar_tela()
            linhareta()
            menu_amostras()

        elif opcao1 == "3":
            limpar_tela()
            linhareta()
            menu_analizador()

        elif opcao1 == "4":
            limpar_tela()
            linhareta()
            menu_controle(db2)

        elif opcao1 == "5":
            try:
                if db:
                    linhareta()
                    exportar_dados(db)
                    print("\n                             ***  FECHANDO BioLab  ***")
                    time.sleep(5)
                    linhareta()
                    sys.exit()

                else:
                    print("\nERRO: Não foi criado nenhum Biolab.db para salvar os dados! \n")
                    linhareta()
                    time.sleep(5)
                    limpar_tela()
                    menu_principal(db, db2)

            except Exception as error:
                print(f"ERRO: Falha ao criar arquivo! -> {error}.Voltando ao menu principal...")
                linhareta()
                time.sleep(5)
                limpar_tela()
                menu_principal(db, db2)
        else:
            print("\nERRO: Opção Inválida! Tente Novamente.")
            time.sleep(3)
            opcoes_principal(db, db2)

    except Exception as error:
        print(f"ERRO: Erro ao iniciar o Menu Principal -> {error}.Tentando novamente...")
        time.sleep(3)
        menu_principal(db, db2)


def menu_principal(db, db2):
    print("\n             ███████████   ███           █████                 █████    \n            ░░███░░░░░███ ░░░           ░░███                 ░░███     \n             ░███    ░███ ████   ██████  ░███         ██████   ░███████ \n             ░██████████ ░░███  ███░░███ ░███        ░░░░░███  ░███░░███\n             ░███░░░░░███ ░███ ░███ ░███ ░███         ███████  ░███ ░███\n             ░███    ░███ ░███ ░███ ░███ ░███      █ ███░░███  ░███ ░███\n             ███████████  █████░░██████  ███████████░░████████ ████████ \n            ░░░░░░░░░░░  ░░░░░  ░░░░░░  ░░░░░░░░░░░  ░░░░░░░░ ░░░░░░░░  \n\n")
    print("     ------------------------   * [ MENU PRINCIPAL ] *   ------------------------     \n")
    print("[!] OPÇÕES:\n")
    print("° [1]¬ CARREGAR Dados Externos.")
    print("° [2]¬ ABRIR Gerenciador de Amostras.")
    print("° [3]¬ ABRIR Analisador de Dados.")
    print("° [4]¬ ABRIR Controle de Qualidade.")
    print("° [5]¬ SAIR (Gerar Arquivo de Amostras).\n")
    opcoes_principal(db, db2)


def menu_amostras():
    print("\n   █████████                                     █████                               \n  ███░░░░░███                                   ░░███                                \n ░███    ░███  █████████████    ██████   █████  ███████   ████████   ██████    █████ \n ░███████████ ░░███░░███░░███  ███░░███ ███░░  ░░░███░   ░░███░░███ ░░░░░███  ███░░  \n ░███░░░░░███  ░███ ░███ ░███ ░███ ░███░░█████   ░███     ░███ ░░░   ███████ ░░█████ \n ░███    ░███  ░███ ░███ ░███ ░███ ░███ ░░░░███  ░███ ███ ░███      ███░░███  ░░░░███\n █████   █████ █████░███ █████░░██████  ██████   ░░█████  █████    ░░████████ ██████ \n░░░░░   ░░░░░ ░░░░░ ░░░ ░░░░░  ░░░░░░  ░░░░░░     ░░░░░  ░░░░░      ░░░░░░░░ ░░░░░░  \n")
    print("     ------------------------     * [ MENU ] *     ------------------------   \n")
    print("[!] OPÇÕES:\n")
    print("° [1]¬ ADICIONAR amostra.")
    print("° [2]¬ PESQUISAR amostras expecíficas.")
    print("° [3]¬ ATUALIZAR resultado/lembrete de amostra.")
    print("° [4]¬ LISTAR todas as amostras.")
    print("° [5]¬ DELETAR uma amostra.")
    print("° [6]¬ DELETAR todas as amostras. (CUIDADO!)")
    print("° [7]¬ VOLTAR ao menu principal.\n")
    opcoes_amostras()


def opcoes_amostras():
    try:
        opcao2 = input("[!] Digite o número da Opção [ENTER para confirmar]: ")
        if opcao2 == "1":
            try:
                limpar_tela()
                linhareta()
                print("[!] Preencha os dados a seguir para cadastrar amostra:\n")
                paciente = input("° NOME DA AMOSTRA: ")
                exame = input("° LOCAL DE ARMAZENAMENTO: ")
                identificacao = input("° IDENTIFICAÇÃO DA AMOSTRA: ")
                data_hora = input("° DATA E HORA: ")
                linhareta()
                ger_amostras.adicionar_amostra(paciente, exame, identificacao, data_hora, resultado=None)
                time.sleep(5)
                limpar_tela()
                menu_amostras()

            except Exception as error:
                print(f"ERRO: Não foi possível adicionar amostra! -> {error}\n")
                time.sleep(5)
                opcoes_amostras()

            except KeyboardInterrupt:
                print("\n[!] Operação interrompida pelo usuário.\n")
                time.sleep(2)
                limpar_tela()
                menu_amostras()

        elif opcao2 == "2":
            try:
                limpar_tela()
                linhareta()
                modo = input("[!] Utilizar:\n[1]¬ Nome da Amostra ou [2]¬ Identificação?\nDigite [1/2]:")
                linhareta()
                if modo == "1":
                    paciente = input("-> NOME DA AMOSTRA: ")
                    ident = None
                    ger_amostras.amostras_por_paciente(paciente, ident)
                    choic = input("Voltar ao menu?\nDigite [1]¬ sim: ")
                    if choic == "1":
                        limpar_tela()
                        menu_amostras()
                    else:
                        limpar_tela()
                        menu_amostras()

                elif modo == "2":
                    paciente = None
                    ident = input("-> IDENTIFICAÇÃO DA AMOSTRA: ")
                    ger_amostras.amostras_por_paciente(paciente, ident)
                    choic = input("Voltar ao menu principal?\nDigite [1]¬ sim: ")
                    if choic == "1":
                        limpar_tela()
                        menu_amostras()
                    else:
                        limpar_tela()
                        menu_amostras()

                else:
                    print("ERRO: Opção Inválida ! tente novamente...")
                    time.sleep(3)
                    opcoes_amostras()

            except Exception as error:
                print(f"ERRO: não foi possível pesquisar por pacientes! -> {error} tente novamente...\n")
                time.sleep(20)
                opcoes_amostras()

        elif opcao2 == "3":
            try:
                limpar_tela()
                linhareta()
                amost = input("º ID da amostra: ")
                result = input("º RESULTADO / LEMBRETE: ")
                linhareta()
                if result:
                    ger_amostras.atualizar_resultado(amost, result)
                    time.sleep(5)
                    limpar_tela()
                    menu_amostras()

                else:
                    print("ERRO: resultado sem dados, escreva alguma coisa...")
                    time.sleep(5)
                    opcoes_amostras()

            except Exception as error:
                print(f"ERRO: Não foi possivel iniciar a opção! -> {error}\n")
                time.sleep(5)
                opcoes_amostras()

        elif opcao2 == "4":
            try:
                linhareta()
                ger_amostras.listar_amostras()
                linhareta()
                choic = input("Voltar ao menu?\nDigite [1]¬ sim: ")
                if choic == "1":
                    limpar_tela()
                    menu_amostras()
                else:
                    limpar_tela()
                    menu_amostras()

            except Exception as error:
                print(f"ERRO: {error}\n")
                time.sleep(5)
                opcoes_amostras()

        elif opcao2 == "5":
            try:
                limpar_tela()
                linhareta()
                amostr = input("[!] Qual amostra deseja deletar?\n[DIGITE o ID da amostra]: ")
                if amostr:
                    ger_amostras.deletar_amostras(amostr)
                    linhareta()
                    time.sleep(5)
                    limpar_tela()
                    menu_amostras()

                else:
                    print("ERRO: Insira uma amostra para ser deletada!\n")
                    time.sleep(5)
                    limpar_tela()
                    opcoes_amostras()

            except Exception as error:
                print(f"ERRO: Não foi possivel excluir a amostra! -> {error}, tente novamente...\n")
                time.sleep(5)
                limpar_tela()
                opcoes_amostras()

        elif opcao2 == "6":
            try:
                linhareta()
                resposta = input("[!] Tem certeza que deseja apagar todo o banco de dados de amostras?\n[Esta ação não poderá ser desfeita]\n\n[1]¬ Sim\n[2]¬ Não\n\nOPÇÃO: ")
                if resposta == "1":
                    linhareta()
                    print("                         * EXCLUINDO BANCO DE DADOS... *\n")
                    db.deletar_todas_amostras()
                    time.sleep(5)
                    limpar_tela()
                    menu_amostras()

                elif resposta == "2":
                    linhareta()
                    time.sleep(2)
                    limpar_tela()
                    menu_amostras()

                else:
                    print("ERRO: Dados informados incorretamente! tente de novo...\n")
                    time.sleep(3)
                    opcoes_amostras()

            except Exception as error:
                print(f"ERRO: falha ao excluir banco de dados! -> {error}\n")
                time.sleep(5)
                opcoes_amostras()

        elif opcao2 == "7":
            try:
                linhareta()
                limpar_tela()
                menu_principal(db, db2)

            except Exception as error:
                while error:
                    print(f"ERRO: {error}, tentando novamente...\n[ctrl + c -> PARAR]\n")
                    time.sleep(5)
                    limpar_tela()
                    menu_principal(db, db2)
                    if KeyboardInterrupt:
                        menu_amostras()

        else:
            print("\nERRO: opção inválida! tente novamente...\n")
            time.sleep(3)
            opcoes_amostras()

    except Exception as error:
        print(f"ERRO: {error}\n")
        time.sleep(3)
        limpar_tela()
        menu_amostras()

        if KeyboardInterrupt:
            menu_principal(db, db2)


def opcoes_analizador():
    try:
        opcao3 = input("[!] Digite o número da Opção [ENTER para confirmar]: ")
        linhareta()
        if opcao3 == "1":
            anadados.obter_dados_input()
            anadados.analizar_dados()
            choic = input("Voltar ao menu?\nDigite [1]¬ sim: ")
            if choic == "1":
                limpar_tela()
                menu_analizador()
            else:
                limpar_tela()
                menu_analizador()

        elif opcao3 == "2":
            anadados.obter_dados_chi()
            linhareta()
            choic = input("Voltar ao menu?\nDigite [1]¬ sim: ")
            if choic == "1":
                limpar_tela()
                menu_analizador()

        elif opcao3 == "3":
            try:
                linhareta()
                limpar_tela()
                menu_principal(db, db2)

            except Exception as error:
                while error:
                    print(f"ERRO: {error}, tentando novamente...\n[ctrl + c -> PARAR]\n")
                    time.sleep(3)
                    menu_principal(db, db2)

                    if KeyboardInterrupt:
                        menu_analizador()

        else:
            print("ERRO: opção inválida!\n")
            time.sleep(3)
            opcoes_analizador()

    except Exception as error:
        while error:
            print(f"ERRO: Não foi possivel carregar as opções! {error}, tentando novamente...\n")
            time.sleep(3)
            opcoes_analizador()

            if KeyboardInterrupt:
                time.sleep(3)
                limpar_tela()
                menu_analizador()


def menu_analizador():
    print("\n   █████████                        ████   ███                           █████                   \n  ███░░░░░███                      ░░███  ░░░                           ░░███                    \n ░███    ░███  ████████    ██████   ░███  ████   █████████  ██████    ███████   ██████  ████████ \n ░███████████ ░░███░░███  ░░░░░███  ░███ ░░███  ░█░░░░███  ░░░░░███  ███░░███  ███░░███░░███░░███\n ░███░░░░░███  ░███ ░███   ███████  ░███  ░███  ░   ███░    ███████ ░███ ░███ ░███ ░███ ░███ ░░░ \n ░███    ░███  ░███ ░███  ███░░███  ░███  ░███    ███░   █ ███░░███ ░███ ░███ ░███ ░███ ░███     \n █████   █████ ████ █████░░████████ █████ █████  █████████░░████████░░████████░░██████  █████    \n░░░░░   ░░░░░ ░░░░ ░░░░░  ░░░░░░░░ ░░░░░ ░░░░░  ░░░░░░░░░  ░░░░░░░░  ░░░░░░░░  ░░░░░░  ░░░░░     \n")
    print("     ------------------------     * [ MENU ] *     ------------------------   \n")
    print("[!] OPÇÕES:\n")
    print("° [1]¬ ANALISAR conjunto de números.")
    print("º [2]¬ TESTE Chi-Quadrado.")
    print("° [3]¬ VOLTAR ao menu principal.\n")
    opcoes_analizador()


def opcoes_controle(db2):
    try:
        opcao4 = input("[!] Digite o número da Opção [ENTER para confirmar]: ")
        if opcao4 == "1":
            try:
                linhareta()
                print("[!] Preencha os dados a seguir para cadastrar um padrão:\n")
                equip = input("º Nome do Equipamento: ")
                exam = input("º Nome do Exame ou Substância: ")
                padr = float(input("º Valor Padrão para cadastrar: "))
                linhareta()
                laboratorio.cadastrar_padrao(equip, exam, padr)
                time.sleep(5)
                limpar_tela()
                menu_controle(db2)

            except Exception as error:
                print(f"ERRO: Não foi possivel iniciar o cadastro! -> {error}\n")
                time.sleep(3)
                opcoes_controle(db2)

        elif opcao4 == "2":
            try:
                linhareta()
                equipamento = input("º Nome do Equipamento: ")
                exame = input("º Nome do Exame/Substância: ")
                valor_amostra = float(input("º Valor da Amostra: "))
                configuracao_estagiario = {
                    equipamento: {
                        exame: valor_amostra
                    }
                }
                erros = laboratorio.comparar_configuracao(configuracao_estagiario)

                if erros:
                    linhareta()
                    print("ATENÇÃO! Erros encontrados em sua calibração:\n")
                    for erro in erros:
                        print(f"¬ EQUIPAMENTO: {erro['¬ EQUIPAMENTO']}")
                        print(f"¬ EXAME/SUBSTÂNCIA: {erro['¬ EXAME/SUBSTÂNCIA']}")
                        print(f"¬ VALOR ESPERADO: {erro['¬ VALOR ESPERADO']}")
                        print(f"¬ VALOR DE SUA AMOSTRA: {erro['¬ VALOR DE SUA AMOSTRA']}\n")
                    linhareta()

                    choic = input("\nVoltar ao menu?\nDigite [1]¬ sim: ")
                    if choic == "1":
                        limpar_tela()
                        menu_controle(db2)
                    else:
                        limpar_tela()
                        menu_controle(db2)

                else:
                    print("\nOK! Calibração está de acordo com os padrões cadastrados.\n")
                    linhareta()
                    time.sleep(5)
                    limpar_tela()
                    menu_controle(db2)

            except Exception as error:
                print(f"ERRO: Não foi possível iniciar o comparador! -> {error}\n")
                time.sleep(3)
                limpar_tela()
                opcoes_controle(db2)

        elif opcao4 == "3":
            try:
                linhareta()
                equip = input("º Nome do equipamento para deletar: ")
                laboratorio.deletar_equipamento(equip)
                time.sleep(3)
                limpar_tela()
                menu_controle(db2)

            except Exception as error:
                print(f"ERRO: Falha ao iniciar -> {error}\n")
                time.sleep(3)
                limpar_tela()
                opcoes_controle(db2)

        elif opcao4 == "4":
            try:
                linhareta()
                resposta = input("[!] Tem certeza que deseja apagar todos os equipamentos?\n[Esta ação não poderá ser desfeita]\n\n[1]¬ Sim\n[2]¬ Não\n\nOPÇÃO: ")
                if resposta == "1":
                    linhareta()
                    print("                         * EXCLUINDO BANCO DE DADOS... *\n")
                    db2.deletar_todos_equipamentos()
                    time.sleep(3)
                    limpar_tela()
                    menu_controle(db2)

                elif resposta == "2":
                    linhareta()
                    time.sleep(2)
                    limpar_tela()
                    menu_controle(db2)

                else:
                    print("ERRO: Dados informados incorretamente! tente de novo...\n")
                    time.sleep(3)
                    opcoes_controle(db2)

            except Exception as error:
                print(f"ERRO: falha ao excluir banco de dados! -> {error}\n")
                time.sleep(5)
                opcoes_controle(db2)

        elif opcao4 == "5":
            try:
                limpar_tela()
                linhareta()
                menu_principal(db, db2)

            except Exception as error:
                while error:
                    print(f"ERRO: {error}, tentando novamente...\n[ctrl + c -> PARAR]\n")
                    time.sleep(3)
                    menu_principal(db, db2)

                    if KeyboardInterrupt:
                        menu_controle(db2)

        else:
            print("ERRO: opção inválida!\n")
            time.sleep(3)
            opcoes_controle(db2)

    except Exception as error:
        while error:
            print(f"ERRO: Não foi possivel carregar as opções! {error}, tentando novamente...\n")
            time.sleep(2)
            opcoes_controle(db2)

            if KeyboardInterrupt:
                time.sleep(3)
                limpar_tela()
                menu_controle(db2)


def menu_controle(db2):
    print("\n   █████████            ████   ███  █████                             █████                   \n  ███░░░░░███          ░░███  ░░░  ░░███                             ░░███                    \n ███     ░░░   ██████   ░███  ████  ░███████  ████████   ██████    ███████   ██████  ████████ \n░███          ░░░░░███  ░███ ░░███  ░███░░███░░███░░███ ░░░░░███  ███░░███  ███░░███░░███░░███\n░███           ███████  ░███  ░███  ░███ ░███ ░███ ░░░   ███████ ░███ ░███ ░███ ░███ ░███ ░░░ \n░░███     ███ ███░░███  ░███  ░███  ░███ ░███ ░███      ███░░███ ░███ ░███ ░███ ░███ ░███     \n ░░█████████ ░░████████ █████ █████ ████████  █████    ░░████████░░████████░░██████  █████    \n  ░░░░░░░░░   ░░░░░░░░ ░░░░░ ░░░░░ ░░░░░░░░  ░░░░░      ░░░░░░░░  ░░░░░░░░  ░░░░░░  ░░░░░     \n")
    print("     ------------------------     * [ MENU ] *     ------------------------   \n")
    print("[!] OPÇÕES:\n")
    print("° [1]¬ CADASTRAR padrões.")
    print("° [2]¬ ANALISAR calibração.")
    print("° [3]¬ DELETAR um padrão.")
    print("° [4]¬ DELETAR todo o banco de dados. (CUIDADO!)")
    print("° [5]¬ VOLTAR ao menu principal.\n")
    opcoes_controle(db2)


if __name__ == "__main__":
    try:
        database()
        databaze()
        db = Database("BioLab.db")
        db2 = Database("BioLab.db")
        ger_amostras = GerenciadorAmostras(db)
        laboratorio = LaboratorioBiomedicina(db2)
        seabornn()
        linhareta()
        menu_principal(db, db2)

    except sqlite3.Error as sql_error:
        print(f"ERRO no banco de dados: {sql_error}\n")
        time.sleep(5)
        sys.exit()

    except Exception as generic_error:
        print(f"ERRO: Falha ao executar o Programa -> {generic_error}\n")
        time.sleep(5)
        sys.exit()
        

