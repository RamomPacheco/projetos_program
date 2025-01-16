import pymupdf as fitz
import re
from pathlib import Path
from PyPDF2 import PdfReader
from tqdm import tqdm
import os
import subprocess
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit,
                               QPushButton, QFileDialog, QVBoxLayout, QWidget,
                               QProgressBar, QMessageBox, QHBoxLayout)
from PySide6.QtCore import QThread, Signal
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Definir o local para o Brasil


class Worker(QThread):
    progress_update = Signal(int)
    finished = Signal(str)

    def __init__(self, pdf_pagos_path, pdf_projetos_dir, base_output_dir):
        super().__init__()
        self.pdf_pagos_path = pdf_pagos_path
        self.pdf_projetos_dir = pdf_projetos_dir
        self.base_output_dir = base_output_dir

    def run(self):
        pasta_base = self.processar_pdfs(self.pdf_pagos_path, self.pdf_projetos_dir, self.base_output_dir)
        self.finished.emit(pasta_base)

    def extrair_nomes_e_valores_pagos(self, pdf_path, total_pages, current_stage, total_stages):
        """Extrai nomes e valores de um PDF de pagamentos."""
        dados = {}
        try:
            with fitz.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf, start=1):
                    texto = page.get_text("text")
                    pattern = r"([A-Za-zÁ-Úá-úÂ-Ûâ-ûÃ-Õã-õÇç\s]+)\s+(\d{1,3}(?:\.\d{3})*,\d+\s)"
                    matches = re.findall(pattern, texto)
                    for nome, valor in matches:
                        nome = nome.strip()
                        try:
                            valor_float = float(valor.replace('.', '').replace(',', '.'))
                            valor_formatado = locale.format_string('%.2f', valor_float, grouping=True)
                            dados[nome] = valor_formatado
                        except ValueError:
                            print(f"Erro ao converter valor: {valor} (nome: {nome})")

                    progress = ((current_stage - 1) / total_stages) + (1 / total_stages) * (page_num / total_pages)
                    self.progress_update.emit(int(progress * 100))

        except Exception as e:
            print(f"Erro ao abrir/processar PDF (Pagos): {e}")
            return {}
        return dados

    def extract_data(self, pdf_path, total_pages, current_stage, total_stages):
        """Extrai nomes e valores líquidos de um PDF de projeto."""
        extracted_data = {}
        try:
            reader = PdfReader(pdf_path)
            all_text = ""
            for page_num, page in enumerate(reader.pages, start=1):
                all_text += page.extract_text()
                progress = ((current_stage - 1) / total_stages) + (1 / total_stages) * (page_num / total_pages)
                self.progress_update.emit(int(progress * 100))

            pattern = r" - ([A-Z ]+) \d{3}\.\d{3}\.\d{3}-\d{2}.*?(\d{1,3}(?:\.\d{3})*,\d{2})"
            matches = re.findall(pattern, all_text)

            for name, value in matches:
                name = name.strip()
                try:
                    valor_float = float(value.replace('.', '').replace(',', '.'))
                    valor_formatado = locale.format_string('%.2f', valor_float, grouping=True)
                    extracted_data[name] = valor_formatado
                except ValueError:
                    print(f"Aviso: Não foi possível converter valor para float: '{value}' para o nome '{name}'.")
        except Exception as e:
            print(f"Erro ao processar o arquivo PDF (Projeto): {e}")
            return {}
        return extracted_data

    def criar_pasta_saida(self, pdf_path, base_output_dir):
        """Cria uma pasta de saída com base no nome do arquivo PDF."""
        try:
            nome_arquivo = Path(pdf_path).name
            nome_pasta = nome_arquivo.split(' - ')[0].strip()  # Pega o nome antes do " - "
            pasta_saida = Path(base_output_dir, nome_pasta)

            os.makedirs(pasta_saida, exist_ok=True)
            return pasta_saida
        except Exception as e:
            print(f"Erro ao criar pasta de saída: {e}")
            return None

    def comparar_txts_busca_parcial(self, arquivo1_path, arquivo2_path, arquivo_saida_path, total_lines, current_stage, total_stages):
        """Compara nomes e valores com busca parcial."""
        try:
            with open(arquivo1_path, 'r', encoding='utf-8') as arquivo1, \
                 open(arquivo2_path, 'r', encoding='utf-8') as arquivo2, \
                 open(arquivo_saida_path, 'w', encoding='utf-8') as arquivo_saida:

                dados_arquivo1 = {}
                for linha in arquivo1:
                    match = re.match(r"(.+?):\s*([\d,.]+)", linha)
                    if match:
                        nome = match.group(1).strip()
                        valor = match.group(2).strip()
                        dados_arquivo1[nome] = valor

                for line_num, linha in enumerate(arquivo2, start=1):
                    match = re.match(r"(.+?):\s*([\d,.]+)", linha)
                    if match:
                        nome2_completo = match.group(1).strip()
                        valor2 = match.group(2).strip()
                        partes_nome2 = nome2_completo.split()

                        encontrado = False
                        for i in range(len(partes_nome2), 0, -1):
                            nome2_parcial = " ".join(partes_nome2[:i])
                            for nome1, valor1 in dados_arquivo1.items():
                                if nome2_parcial in nome1 and valor1 == valor2:
                                    arquivo_saida.write(linha)
                                    encontrado = True
                                    break
                            if encontrado:
                                break
                    progress = ((current_stage - 1) / total_stages) + (1 / total_stages) * (line_num / total_lines)
                    self.progress_update.emit(int(progress * 100))
        except FileNotFoundError:
            print(f"Erro: Um ou ambos os arquivos de entrada não foram encontrados.")
        except Exception as e:
            print(f"Um erro ocorreu: {e}")

    def comparar_txts_com_busca_parcial(self, arquivo1_path, arquivo2_path, arquivo_saida_exato, arquivo_saida_diferente, arquivo_nomes_nao_encontrados, total_lines, current_stage, total_stages):
        """Compara arquivos de texto com busca exata e parcial e salva nomes não encontrados."""
        try:
            dados_arquivo1 = {}
            with open(arquivo1_path, 'r', encoding='utf-8') as arquivo1:
                for linha in arquivo1:
                    match = re.match(r"(.+?):\s*([\d,.]+)", linha)
                    if match:
                        nome = match.group(1).strip()
                        valor = match.group(2).strip()
                        dados_arquivo1[nome] = valor

            nomes_nao_encontrados = []
            correspondencias_diferentes = []

            with open(arquivo2_path, 'r', encoding='utf-8') as arquivo2, \
                 open(arquivo_saida_exato, 'w', encoding='utf-8') as arquivo_saida_exato:
                for line_num, linha in enumerate(arquivo2, start=1):
                    match = re.match(r"(.+?):\s*([\d,.]+)", linha)
                    if match:
                        nome2_completo = match.group(1).strip()
                        valor2 = match.group(2).strip()

                        if nome2_completo in dados_arquivo1 and dados_arquivo1[nome2_completo] == valor2:
                            arquivo_saida_exato.write(linha)
                        else:
                            nomes_nao_encontrados.append((nome2_completo, valor2))
                    progress = ((current_stage - 1) / total_stages) + (1 / total_stages) * (line_num / total_lines)
                    self.progress_update.emit(int(progress * 100))

            with open(arquivo_nomes_nao_encontrados, 'w', encoding='utf-8') as arquivo_nomes_nao_encontrados_file:
                with open(arquivo_saida_diferente, 'w', encoding='utf-8') as arquivo_saida_diferente:
                    for nome_original, valor_original in tqdm(nomes_nao_encontrados, desc="Comparando arquivos (Parcial)"):
                        partes_nome = nome_original.split()
                        encontrado = False

                        if partes_nome:
                         
                            for i in range(1, len(partes_nome) + 1):
                                nome_parcial = " ".join(partes_nome[:i])
                                if i == 1 and len(partes_nome) > 1:
                                    nome_parcial = partes_nome[0]  # Pega o primeiro nome
                                    nome_parcial += " " + partes_nome[1][0] # Adiciona a primeira letra do segundo nome

                                correspondencias = [
                                    nome for nome, valor in dados_arquivo1.items()
                                    if nome.startswith(nome_parcial) and valor == valor_original
                                ]

                                if len(correspondencias) == 1:
                                    nome_encontrado = correspondencias[0]
                                    arquivo_saida_diferente.write(
                                        f"Original: {nome_original}: {valor_original}\nEncontrado como: {nome_encontrado}: {valor_original}\n"
                                    )
                                    correspondencias_diferentes.append((nome_original, nome_encontrado, valor_original))
                                    encontrado = True
                                    break
                        if not encontrado:
                            arquivo_saida_diferente.write(
                                f"Original: {nome_original}: {valor_original} -> Nenhuma correspondência única encontrada\n"
                            )
                            arquivo_nomes_nao_encontrados_file.write(f"{nome_original}: {valor_original}\n") # Salvando em arquivo separado
    
        except FileNotFoundError as e:
            print(f"Erro: Arquivo não encontrado - {e.filename}")
        except Exception as e:
            print(f"Um erro ocorreu: {e}")

    def adicionar_nomes_encontrados(self, arquivo_entrada_path, arquivo_saida_path, total_lines, current_stage, total_stages):
        """Adiciona nomes encontrados ao arquivo de saída."""
        try:
            with open(arquivo_entrada_path, 'r', encoding='utf-8') as arquivo_entrada:
                with open(arquivo_saida_path, 'a', encoding='utf-8') as arquivo_saida:
                    for line_num, linha in enumerate(arquivo_entrada, start=1):
                        if "Encontrado como" in linha:
                            match = re.match(r"Encontrado como:\s*(.*?):\s*([\d,.]+)", linha.strip())
                            if match:
                                nome = match.group(1).strip()
                                valor = match.group(2).strip()
                                arquivo_saida.write(f"{nome}: {valor}\n")
                        progress = ((current_stage - 1) / total_stages) + (1 / total_stages) * (line_num / total_lines)
                        self.progress_update.emit(int(progress * 100))
        except FileNotFoundError as e:
            print(f"Erro: Arquivo não encontrado - {e.filename}")
        except Exception as e:
            print(f"Um erro ocorreu: {e}")

    def destacar_nomes_no_pdf(self, pdf_path, txt_path, output_pdf_path, nomes_nao_encontrados_path, total_pages, current_stage, total_stages):
        """Destaca nomes em um PDF e salva os não encontrados."""
        nomes = []
        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    nome = line.split(":")[0].strip()
                    nomes.append(nome)

        nomes_nao_destacados = set(nomes)
        try:
            with fitz.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf, start=1):
                    for nome in nomes:
                        areas = page.search_for(nome)
                        if areas:
                            nomes_nao_destacados.discard(nome)
                            for area in areas:
                                page.add_highlight_annot(area)

                    for nome in list(nomes_nao_destacados):
                        areas = page.search_for(nome)
                        if areas:
                            nomes_nao_destacados.discard(nome)
                            for area in areas:
                                page.add_underline_annot(area)
                    progress = ((current_stage - 1) / total_stages) + (1 / total_stages) * (page_num / total_pages)
                    self.progress_update.emit(int(progress * 100))
                pdf.save(output_pdf_path)
        except Exception as e:
            print(f"Erro ao processar PDF para destaque: {e}")
            return

        if nomes_nao_destacados:
            print("Nomes não destacados no PDF:")
            nomes_nao_destacados_lista = sorted(list(nomes_nao_destacados))
            try:
                nomes_nao_encontrados_path = os.path.join(os.path.dirname(output_pdf_path), "nomes_nao_destacados.txt") # Caminho absoluto

                with open(nomes_nao_encontrados_path, "w", encoding="utf-8") as f:
                    total_nomes = len(nomes_nao_destacados_lista)
                    f.write(f"Total de nomes não encontrados: {total_nomes}\n")
                    for nome in nomes_nao_destacados_lista:
                        f.write(f"{nome}\n")
                print(f"Nomes não destacados salvos em: {nomes_nao_encontrados_path}")
            except Exception as e:
                print(f"Erro ao salvar nomes não encontrados: {e}")
                print(f"Nomes não destacados: {nomes_nao_destacados}")  # Imprimir nomes não destacados em caso de erro

        else:
             nomes_nao_encontrados_path = os.path.join(os.path.dirname(output_pdf_path), "nomes_nao_destacados.txt") # Caminho absoluto
             if os.path.exists(nomes_nao_encontrados_path):
                os.remove(nomes_nao_encontrados_path)


    def salvar_arquivos_na_pasta(self, pasta_saida, output_pagos, output_projeto, arquivo_saida_path, arquivo_saida_exato, arquivo_saida_diferente, output_pdf, nomes_nao_encontrados_path, arquivo_nomes_nao_encontrados):
        """Salva todos os arquivos de saída em uma pasta específica."""
        if pasta_saida:
            import shutil
            try:
                # Definindo os novos caminhos de arquivos dentro da pasta de saída
                novo_output_pagos = Path(pasta_saida, Path(output_pagos).name)
                novo_output_projeto = Path(pasta_saida, Path(output_projeto).name)
                novo_arquivo_saida_path = Path(pasta_saida, Path(arquivo_saida_path).name)
                novo_arquivo_saida_exato = Path(pasta_saida, Path(arquivo_saida_exato).name)
                novo_arquivo_saida_diferente = Path(pasta_saida, Path(arquivo_saida_diferente).name)
                novo_output_pdf = Path(pasta_saida, Path(output_pdf).name)
                novo_nomes_nao_encontrados_path = Path(pasta_saida, Path(nomes_nao_encontrados_path).name)
                novo_arquivo_nomes_nao_encontrados = Path(pasta_saida, Path(arquivo_nomes_nao_encontrados).name)

                # Copiar arquivos e renomear
                shutil.copy2(output_pagos, novo_output_pagos)
                shutil.copy2(output_projeto, novo_output_projeto)
                shutil.copy2(arquivo_saida_path, novo_arquivo_saida_path)
                shutil.copy2(arquivo_saida_exato, novo_arquivo_saida_exato)
                shutil.copy2(arquivo_saida_diferente, novo_arquivo_saida_diferente)
                shutil.copy2(output_pdf, novo_output_pdf)
                if os.path.exists(nomes_nao_encontrados_path):
                  shutil.copy2(nomes_nao_encontrados_path, novo_nomes_nao_encontrados_path)
                shutil.copy2(arquivo_nomes_nao_encontrados, novo_arquivo_nomes_nao_encontrados)
                return pasta_saida

            except Exception as e:
                print(f"Erro ao salvar os arquivos na pasta: {e}")
                return None
        else:
            return None

    def atualizar_totais_txt(self, arquivo_path):
      """Adiciona ou substitui o total de nomes e valores na primeira linha do arquivo."""
      try:
        with open(arquivo_path, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            total_valor = 0.0
            total_nomes = 0

              #Contar nomes sem contar a linha de total caso exista
            for line in lines:
                if not line.startswith("Total:"):
                   match = re.match(r".+?:\s*([\d,.]+)", line)
                   if match:
                        try:
                            valor = float(match.group(1).replace('.', '').replace(',', '.'))
                            total_valor += valor
                            total_nomes += 1
                        except ValueError:
                            total_nomes += 1
                  
            new_total_line = f"Total: {total_nomes} nomes, Valor: {locale.format_string('%.2f', total_valor, grouping=True)}\n"

              #Verificar se já existe uma linha de total
            if lines and lines[0].startswith("Total:"):
                lines[0] = new_total_line
            else:
                lines.insert(0, new_total_line)
                
            f.seek(0) # Vai pro inicio do arquivo
            f.writelines(lines)
            f.truncate() # Remove o que está depois do que escrevemos

      except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado '{arquivo_path}'.")
      except Exception as e:
        print(f"Erro ao atualizar totais em '{arquivo_path}': {e}")
    def atualizar_totais_em_todos_txts(self, base_output_dir):
         for item in os.listdir(base_output_dir):
                item_path = Path(base_output_dir, item)
                if item_path.is_dir():
                    for file_name in os.listdir(item_path):
                        if file_name.endswith('.txt'):
                             file_path = Path(item_path, file_name)
                             self.atualizar_totais_txt(file_path)
    def processar_pdfs(self, pdf_pagos_path, pdf_projetos_dir, base_output_dir):
        
        # Obter a lista de arquivos PDF na pasta
        pdf_projetos_files = [
            str(Path(pdf_projetos_dir, f)) for f in os.listdir(pdf_projetos_dir) 
            if f.lower().endswith('.pdf')
        ]

        if not pdf_projetos_files:
            QMessageBox.critical(None, "Erro", "Não foram encontrados arquivos PDF na pasta selecionada.")
            return

        total_stages = len(pdf_projetos_files) * 6  # 6 etapas por PDF
        current_stage = 0
        
        for pdf_todos in pdf_projetos_files:
            # Criar a pasta de saída específica para este PDF
            pasta_saida = self.criar_pasta_saida(pdf_todos, base_output_dir)
            if not pasta_saida:
                QMessageBox.critical(None, "Erro", f"Não foi possível criar a pasta de saída para '{Path(pdf_todos).name}'.")
                continue
            
            # Definindo os caminhos de saída para o PDF atual
            output_pagos = str(Path(pasta_saida, "dados_pdf_pagos.txt"))
            output_projeto = str(Path(pasta_saida, "dados_pdf_projeto.txt"))
            arquivo_saida_path = str(Path(pasta_saida, "Funcionarios_encontrados.txt"))
            arquivo1_path = str(Path(pasta_saida, "dados_pdf_pagos.txt"))
            arquivo2_path = str(Path(pasta_saida, "dados_pdf_projeto.txt"))
            arquivo_saida_exato = str(Path(pasta_saida, "Funcionarios_encontrados.txt"))
            arquivo_saida_diferente = str(Path(pasta_saida, "Funcionarios_nomes_diferente.txt"))
            output_pdf = str(Path(pasta_saida, f"{Path(pdf_todos).stem}_destacado.pdf"))
            nomes_nao_encontrados_path = str(Path(pasta_saida, "nomes_nao_destacados.txt"))
            arquivo_nomes_nao_encontrados = str(Path(pasta_saida, "Nomes não encontrados.txt"))

            # Extrair e salvar dados do PDF (Pagos)
            current_stage += 1
            try:
                with fitz.open(pdf_pagos_path) as pdf:
                     total_pages_pagos = len(pdf)
            except:
                total_pages_pagos = 1
            
            separados = self.extrair_nomes_e_valores_pagos(pdf_pagos_path, total_pages_pagos, current_stage, total_stages)
            
            if separados:
                with open(output_pagos, "w", encoding="utf-8") as f:
                    for nome, valor in sorted(separados.items()):
                        # print(f"{nome}: {valor:.2f}")
                        f.write(f"{nome}: {valor}\n")
                print(f"Arquivo de saída salvo em: {output_pagos}")

            # Extrair e salvar dados do PDF (Projeto)
            current_stage += 1
            try:
                reader = PdfReader(pdf_todos)
                total_pages_projetos = len(reader.pages)
            except:
                total_pages_projetos = 1
                
            dados_projeto = self.extract_data(pdf_todos, total_pages_projetos, current_stage, total_stages)
            
            if dados_projeto:
                with open(output_projeto, "w", encoding="utf-8") as f:
                    for nome, valor in sorted(dados_projeto.items()):
                        # print(f"{nome}: {valor:.2f}")
                        f.write(f"{nome}: {valor}\n")
                print(f"Arquivo de saída salvo em {output_projeto}")
        
        
            # Comparar e salvar nomes iguais
            current_stage += 1
            try:
                with open(output_pagos, 'r', encoding='utf-8') as f:
                  total_lines_pagos = len(f.readlines())

                with open(output_projeto, 'r', encoding='utf-8') as f:
                  total_lines_projetos = len(f.readlines())
            except:
                total_lines_pagos = 1
                total_lines_projetos = 1
                
            self.comparar_txts_busca_parcial(output_projeto, output_pagos, arquivo_saida_path, total_lines_projetos, current_stage, total_stages)
            print(f"Comparação concluída. Resultados em '{arquivo_saida_path}'")

            # Comparar e salvar nomes exatos e diferentes
            current_stage += 1
            self.comparar_txts_com_busca_parcial(arquivo1_path, arquivo2_path, arquivo_saida_exato, arquivo_saida_diferente, arquivo_nomes_nao_encontrados, total_lines_projetos, current_stage, total_stages)

            # Adicionar nomes encontrados ao arquivo de saída
            current_stage += 1
            try:
                with open(arquivo_saida_diferente, 'r', encoding='utf-8') as f:
                    total_lines_diferente = len(f.readlines())
            except:
                total_lines_diferente = 1

            self.adicionar_nomes_encontrados(arquivo_saida_diferente, arquivo_saida_exato, total_lines_diferente, current_stage, total_stages)

            # Destacar nomes no PDF e salvar arquivo de nomes não encontrados
            current_stage += 1
            try:
                with open(arquivo_saida_exato, 'r', encoding='utf-8') as f:
                    total_lines_nomes_iguais = len(f.readlines())
            except:
                total_lines_nomes_iguais = 1
            
            try:
                with fitz.open(pdf_pagos_path) as pdf:
                    total_pages_destacados = len(pdf)
            except:
                total_pages_destacados = 1
            
            self.destacar_nomes_no_pdf(pdf_pagos_path, arquivo_saida_exato, output_pdf, nomes_nao_encontrados_path, total_pages_destacados, current_stage, total_stages)

            #Atualiza Totais
            self.atualizar_totais_txt(output_pagos)
            self.atualizar_totais_txt(output_projeto)
            self.atualizar_totais_txt(arquivo_saida_path)
            self.atualizar_totais_txt(arquivo_saida_exato)
            self.atualizar_totais_txt(nomes_nao_encontrados_path)
            self.atualizar_totais_txt(arquivo_saida_diferente)


            # Salvar arquivos na pasta
            pasta_base = self.salvar_arquivos_na_pasta(pasta_saida, output_pagos, output_projeto, arquivo_saida_path, arquivo_saida_exato, arquivo_saida_diferente, output_pdf, nomes_nao_encontrados_path, arquivo_nomes_nao_encontrados)
           
            print(f"Processamento concluído para: {Path(pdf_todos).name}")
        return base_output_dir
    

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Processador de PDFs")
        self.setGeometry(100, 100, 700, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # PDF de Pagamentos
        self.label_pdf_pagos = QLabel("PDF de Pagamentos:")
        self.entry_pdf_pagos = QLineEdit()
        self.btn_pdf_pagos = QPushButton("Selecionar")
        self.btn_pdf_pagos.clicked.connect(self.selecionar_arquivo_pagos)
        
        self.layout_pagos = QHBoxLayout()
        self.layout_pagos.addWidget(self.label_pdf_pagos)
        self.layout_pagos.addWidget(self.entry_pdf_pagos)
        self.layout_pagos.addWidget(self.btn_pdf_pagos)
        self.layout.addLayout(self.layout_pagos)

        # Pasta de PDFs de Projetos
        self.label_pdf_projetos = QLabel("Pasta de PDFs de Projetos:")
        self.entry_pdf_projetos = QLineEdit()
        self.btn_pdf_projetos = QPushButton("Selecionar")
        self.btn_pdf_projetos.clicked.connect(self.selecionar_pasta_projetos)

        self.layout_projetos = QHBoxLayout()
        self.layout_projetos.addWidget(self.label_pdf_projetos)
        self.layout_projetos.addWidget(self.entry_pdf_projetos)
        self.layout_projetos.addWidget(self.btn_pdf_projetos)
        self.layout.addLayout(self.layout_projetos)

        # Pasta de Saída
        self.label_pasta_saida = QLabel("Pasta de Saída:")
        self.entry_pasta_saida = QLineEdit()
        self.btn_pasta_saida = QPushButton("Selecionar")
        self.btn_pasta_saida.clicked.connect(self.selecionar_pasta_saida)
        
        self.layout_saida = QHBoxLayout()
        self.layout_saida.addWidget(self.label_pasta_saida)
        self.layout_saida.addWidget(self.entry_pasta_saida)
        self.layout_saida.addWidget(self.btn_pasta_saida)
        self.layout.addLayout(self.layout_saida)
        
        # Barra de Progresso
        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)

        # Botão de Iniciar
        self.btn_iniciar = QPushButton("Iniciar Processamento")
        self.btn_iniciar.clicked.connect(self.iniciar_processamento)
        self.layout.addWidget(self.btn_iniciar)

        self.worker_thread = None
    def selecionar_arquivo_pagos(self):
        """Abre um diálogo para selecionar o PDF de pagamentos."""
        filename, _ = QFileDialog.getOpenFileName(self, "Selecione o PDF de Pagamentos", "", "Arquivos PDF (*.pdf)")
        if filename:
            self.entry_pdf_pagos.setText(filename)

    def selecionar_pasta_projetos(self):
        """Abre um diálogo para selecionar a pasta dos PDFs de projetos."""
        foldername = QFileDialog.getExistingDirectory(self, "Selecione a pasta com os PDFs de Projetos")
        if foldername:
            self.entry_pdf_projetos.setText(foldername)

    def selecionar_pasta_saida(self):
        """Abre um diálogo para selecionar a pasta de saída."""
        foldername = QFileDialog.getExistingDirectory(self, "Selecione a pasta de saída")
        if foldername:
            self.entry_pasta_saida.setText(foldername)

    def iniciar_processamento(self):
        """Inicia o processamento dos PDFs."""
        pdf_pagos_path = self.entry_pdf_pagos.text()
        pdf_projetos_dir = self.entry_pdf_projetos.text()
        base_output_dir = self.entry_pasta_saida.text()

        if not pdf_pagos_path or not pdf_projetos_dir or not base_output_dir:
            QMessageBox.critical(self, "Erro", "Por favor, selecione todos os arquivos e pastas.")
            return

        self.iniciar_thread(pdf_pagos_path, pdf_projetos_dir, base_output_dir)
    def iniciar_thread(self, pdf_pagos_path, pdf_projetos_dir, base_output_dir):
        self.progress_bar.setValue(0)
        self.worker_thread = Worker(pdf_pagos_path, pdf_projetos_dir, base_output_dir)
        self.worker_thread.progress_update.connect(self.progress_bar.setValue)
        self.worker_thread.finished.connect(self.processamento_finalizado)
        self.worker_thread.start()

    def processamento_finalizado(self, base_output_dir):
        if QMessageBox.question(self, "Concluído", "Todos os PDFs foram processados! Deseja continuar?") == QMessageBox.Yes:
            self.limpar_campos()
        else:
            if base_output_dir:
                self.worker_thread.atualizar_totais_em_todos_txts(base_output_dir)
                self.abrir_pasta(base_output_dir)
                QApplication.quit() # Encerra o programa após abrir a pasta
        self.worker_thread = None

    def limpar_campos(self):
        self.entry_pdf_pagos.clear()
        self.entry_pdf_projetos.clear()
        self.entry_pasta_saida.clear()
        self.progress_bar.setValue(0)

    def abrir_pasta(self, caminho_pasta):
        if sys.platform == 'win32':  # Para Windows
            try:
                os.startfile(caminho_pasta)
            except FileNotFoundError:
                QMessageBox.critical(self, "Erro", "Pasta não encontrada.")

        elif sys.platform == 'darwin': # Para macOS
            try:
                subprocess.run(['open', caminho_pasta], check=True)
            except subprocess.CalledProcessError:
                QMessageBox.critical(self, "Erro", "Pasta não encontrada.")
        elif sys.platform.startswith('linux'): # Para Linux
            try:
                subprocess.run(['xdg-open', caminho_pasta], check=True)
            except subprocess.CalledProcessError:
                QMessageBox.critical(self, "Erro", "Pasta não encontrada.")
        else:
            QMessageBox.critical(self, "Erro", f"Sistema Operacional não suportado: {sys.platform}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())