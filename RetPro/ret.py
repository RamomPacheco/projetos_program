"""
Este arquivo foi migrado para uma estrutura modular.

Novo ponto de entrada: app.py
Componentes principais agora estão em:
- ui/main_window.py
- workers/process_worker.py
- services/*
- utils/*
- constants/*

Execute a aplicação com:
    python app.py
"""




def process_pdfs_from_folder(folder_path, progress_callback):
    """
    Processa todos os PDFs em uma pasta e retorna os dados extraídos.
    """
    all_data = {}
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
    total_files = len(pdf_files)
    for i, filename in enumerate(pdf_files):
        pdf_path = os.path.join(folder_path, filename)
        print(f"Processando: {filename}")
        extracted_data = extract_data(pdf_path)
        if extracted_data:
            all_data[filename] = extracted_data
        progress_callback.emit(int((i + 1) / total_files * 100))
    return all_data


def save_data_to_json(data, output_path):
    """
    Salva os dados em um arquivo JSON.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_data_from_json(output_path):
    """
    Carrega os dados de um arquivo JSON.
    """
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# Função para alterar a extensão de um arquivo .ret para .txt
def alterar_extensao_para_txt(arquivo_ret):
    if arquivo_ret.endswith(".ret"):
        arquivo_txt = arquivo_ret[:-4] + ".txt"
        os.rename(arquivo_ret, arquivo_txt)
        return arquivo_txt
    return None



    def run(self):
        palavra_excluida = "0BD"
        regex_excluir = re.compile(r"\d+[A-Za-z]$")
        regex_nome = re.compile(r"\b[A-ZÁ-Ú][A-ZÁ-Ú\s]+[A-ZÁ-Ú]\b")
        total_nomes_encontrados_global = 0
        total_valores_encontrados = 0
        resultados_por_arquivo = {}  # Organizar os dados por arquivo
        nomes_encontrados_arquivos_total = (
            {}
        )  # organizar a quantidade de nomes por arquivo
        all_results = []  # Lista para armazenar todos os resultados sem duplicatas
        arquivos_txt = []
        # Encontra todos os .txt e os convertidos de .ret
        for arquivo in glob.glob(os.path.join(self.pasta, "*.ret")):
            arquivo_txt = alterar_extensao_para_txt(arquivo)
            if arquivo_txt:
                arquivos_txt.append(arquivo_txt)

        arquivos_txt.extend(glob.glob(os.path.join(self.pasta, "*.txt")))

        total_arquivos = len(arquivos_txt)

        # Gera o banco de dados JSON
        extracted_data_all_pdfs = process_pdfs_from_folder(
            self.pasta_pdf, self.progresso
        )
        save_data_to_json(extracted_data_all_pdfs, self.banco_dados_json)
        print(f"\nDados salvos em {self.banco_dados_json}")

        # Carrega o banco de dados JSON
        dados_banco = load_data_from_json(self.banco_dados_json)

        for index, file_path in enumerate(arquivos_txt, start=1):
            nome_arquivo = os.path.basename(file_path)
            nomes_encontrados = []
            nomes_encontrados_arquivo = 0
            resultados_por_chave = {}

            try:
                with open(file_path, "r", encoding="latin-1") as file:
                    linhas = file.readlines()
                    linhas = linhas[
                        2:-2
                    ]  # Remove as duas primeiras e duas últimas linhas

                    for i, line in enumerate(linhas, start=3):
                        if (
                            i % 2 != 0
                            and palavra_excluida not in line
                            and not regex_excluir.search(line)
                        ):
                            nomes = regex_nome.findall(line)
                            nomes_encontrados.extend(nomes)
                            nomes_encontrados_arquivo += len(nomes)
            except Exception as e:
                print(f"Erro ao processar o arquivo {nome_arquivo}: {e}\n")
                continue

            # Busca no banco de dados pelos nomes encontrados
            if nomes_encontrados:
                nomes_encontrados_arquivos_total[nome_arquivo] = (
                    nomes_encontrados_arquivo
                )

                for nome_original in nomes_encontrados:
                    pdf_origem = None
                    nome_encontrado = None
                    valor_encontrado = None
                    cpf_encontrado = None

                    # Tenta buscar o nome original diretamente
                    if nome_original in dados_banco.get(
                        list(dados_banco.keys())[0], {}
                    ):
                        for nome_arquivo_db, dados in dados_banco.items():
                            if nome_original in dados:
                                pdf_origem = nome_arquivo_db
                                nome_encontrado = nome_original
                                raw = dados[nome_original]
                                if isinstance(raw, dict):
                                    valor_encontrado = raw.get("valor")
                                    cpf_encontrado = raw.get("cpf")
                                else:
                                    valor_encontrado = raw
                                    cpf_encontrado = None
                                break

                        if nome_encontrado:
                            nome_saida = pdf_origem.split(" - ")[0].replace("  ", " ")
                            if nome_saida not in resultados_por_chave:
                                resultados_por_chave[nome_saida] = []
                            if self.incluir_valores:
                                formatted_valor = (
                                    locale.currency(
                                        valor_encontrado, grouping=True, symbol=False
                                    )
                                    if isinstance(valor_encontrado, (int, float))
                                    else None
                                )
                                resultados_por_chave[nome_saida].append(
                                    (
                                        nome_original,
                                        cpf_encontrado,
                                        formatted_valor,
                                        "Completo",
                                    )
                                )
                                if isinstance(valor_encontrado, (int, float)):
                                    total_valores_encontrados += valor_encontrado
                            else:
                                resultados_por_chave[nome_saida].append(
                                    (nome_original, cpf_encontrado, None, "Completo")
                                )
                    else:  # Busca parcial
                        partes_nome = nome_original.split()
                        encontrado = False
                        for i in range(1, len(partes_nome) + 1):
                            nome_parcial = " ".join(partes_nome[:i])
                            correspondencias = [
                                (nome, nome_arquivo_db, dados[nome])
                                for nome_arquivo_db, dados in dados_banco.items()
                                for nome in dados
                                if nome.startswith(nome_parcial)
                            ]
                            if len(correspondencias) == 1:
                                nome_encontrado = correspondencias[0][0]
                                pdf_origem = correspondencias[0][1]

                                # Correção: Busca o valor usando o nome_encontrado
                                for nome_arquivo_db, dados in dados_banco.items():
                                    if nome_encontrado in dados:
                                        raw = dados[nome_encontrado]
                                        if isinstance(raw, dict):
                                            valor_encontrado = raw.get("valor")
                                            cpf_encontrado = raw.get("cpf")
                                        else:
                                            valor_encontrado = raw
                                            cpf_encontrado = None
                                        break
                                    else:
                                        valor_encontrado = None  # caso não encontre o valor na busca parcial, valor_encontrado é None
                                        cpf_encontrado = None

                                nome_saida = pdf_origem.split(" - ")[0].replace(
                                    "  ", " "
                                )
                                if nome_saida not in resultados_por_chave:
                                    resultados_por_chave[nome_saida] = []

                                if (
                                    self.incluir_valores
                                    and valor_encontrado is not None
                                ):
                                    formatted_valor = (
                                        locale.currency(
                                            valor_encontrado,
                                            grouping=True,
                                            symbol=False,
                                        )
                                        if isinstance(valor_encontrado, (int, float))
                                        else None
                                    )
                                    resultados_por_chave[nome_saida].append(
                                        (
                                            nome_original,
                                            cpf_encontrado,
                                            formatted_valor,
                                            f"Parcial - Encontrado como: {nome_encontrado}",
                                        )
                                    )
                                    if isinstance(valor_encontrado, (int, float)):
                                        total_valores_encontrados += valor_encontrado
                                else:
                                    resultados_por_chave[nome_saida].append(
                                        (
                                            nome_original,
                                            cpf_encontrado,
                                            None,
                                            f"Parcial - Encontrado como: {nome_encontrado}",
                                        )
                                    )
                                encontrado = True
                                break
                        if not encontrado:
                            if "Não Encontrado" not in resultados_por_chave:
                                resultados_por_chave["Não Encontrado"] = []
                            # Tentativa automática de buscar CPF/valor para nomes não encontrados
                            tokens = [
                                t.lower() for t in nome_original.split() if len(t) > 2
                            ]
                            candidates = []
                            for nome_db_file, dados in dados_banco.items():
                                for nome_db in dados:
                                    nome_db_low = nome_db.lower()
                                    if tokens and all(
                                        tok in nome_db_low for tok in tokens
                                    ):
                                        candidates.append(
                                            (nome_db, nome_db_file, dados[nome_db])
                                        )

                            if len(candidates) == 1:
                                cand_nome, cand_file, raw = candidates[0]
                                if isinstance(raw, dict):
                                    cpf_cand = raw.get("cpf")
                                    val_cand = raw.get("valor")
                                else:
                                    cpf_cand = None
                                    val_cand = raw
                                status_text = (
                                    f"Tentativa - Encontrado como: {cand_nome}"
                                )
                                formatted_val = (
                                    locale.currency(
                                        val_cand, grouping=True, symbol=False
                                    )
                                    if isinstance(val_cand, (int, float))
                                    else None
                                )
                                resultados_por_chave["Não Encontrado"].append(
                                    (
                                        nome_original,
                                        cpf_cand,
                                        formatted_val,
                                        status_text,
                                    )
                                )
                                if isinstance(val_cand, (int, float)):
                                    total_valores_encontrados += val_cand
                            else:
                                # Sem correspondência (ou múltiplas) — registra sem cpf/valor
                                resultados_por_chave["Não Encontrado"].append(
                                    (nome_original, None, None, "Não encontrado")
                                )

                if resultados_por_chave:
                    resultados_por_arquivo[nome_arquivo] = resultados_por_chave
        # Processamento para evitar duplicatas e preparar para a saída
        processed_results = (
            set()
        )  # Usado para verificar se um resultado já foi adicionado
        for nome_arquivo, resultados_por_chave in resultados_por_arquivo.items():
            for chave, resultados in resultados_por_chave.items():
                for nome, cpf, valor, status in resultados:
                    result_tuple = (nome_arquivo, chave, nome, cpf, valor, status)
                    if result_tuple not in processed_results:
                        all_results.append(
                            {
                                "Arquivo": nome_arquivo,
                                "Origem": chave,
                                "Nome": nome,
                                "CPF": cpf,
                                "Valor": valor,
                                "Status": status,
                            }
                        )
                        processed_results.add(result_tuple)

        total_nomes_encontrados_global = sum(nomes_encontrados_arquivos_total.values())

        if self.saida_csv:
            # Escreve os resultados no CSV
            with open(self.arquivo_saida, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["Arquivo", "Origem", "Nome", "CPF", "Valor", "Status"]
                writer = csv.DictWriter(
                    csvfile, fieldnames=fieldnames, delimiter=";", quoting=csv.QUOTE_ALL
                )
                writer.writeheader()
                writer.writerows(all_results)

            if self.incluir_valores:
                formatted_total = locale.currency(
                    total_valores_encontrados, grouping=True, symbol=False
                )
                total_texto = f"Total de nomes encontrados em todos os arquivos: {total_nomes_encontrados_global}\nValor total : {formatted_total}"
            else:
                total_texto = f"Total de nomes encontrados em todos os arquivos: {total_nomes_encontrados_global}\nOBS:Opção sem valor total"

            with open(self.arquivo_saida, "a", encoding="utf-8") as file:
                file.write(f"\n{total_texto}")
        else:
            with open(
                self.arquivo_saida, "w", encoding="latin-1"
            ) as saida:  # Abre o arquivo de saída com encoding
                for (
                    nome_arquivo,
                    resultados_por_chave,
                ) in resultados_por_arquivo.items():
                    saida.write(f"Nomes encontrados no arquivo {nome_arquivo}:\n")
                    for chave, nomes in resultados_por_chave.items():
                        saida.write(f"{chave}:\n")
                        for nome, cpf, valor, status in nomes:
                            if self.incluir_valores:
                                saida.write(
                                    f"- {nome} - CPF: {cpf if cpf else 'N/A'} - {valor}\n    - {status}\n"
                                )
                            else:
                                saida.write(f"- {nome}\n    - {status}\n")
                    saida.write("\n")

                total_nomes_encontrados_global = sum(
                    nomes_encontrados_arquivos_total.values()
                )
                saida.write(
                    f"\nTotal de nomes encontrados em todos os arquivos: {total_nomes_encontrados_global}\n"
                )
                if self.incluir_valores:
                    formatted_total = locale.currency(
                        total_valores_encontrados, grouping=True, symbol=False
                    )
                    saida.write(f"Valor total : {formatted_total}")
                else:
                    saida.write(f"OBS:Opção sem valor total")
        self.concluido.emit()


# ... (Restante do código da interface gráfica - sem mudanças)



    def open_folder(self, path):
        """Abre a pasta especificada."""
        if os.path.exists(path):
            if os.name == "nt":  # Windows
                os.startfile(path)
            elif os.name == "posix":  # macOS e Linux
                subprocess.Popen(["open", path])
            else:
                print(
                    "Sistema operacional não suportado para abrir pastas automaticamente."
                )
        else:
            print(f"Erro: A pasta '{path}' não existe.")

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Layout para selecionar a pasta de origem PDF (para gerar o banco)
        pasta_pdf_layout = QHBoxLayout()
        self.pasta_pdf_label = QLabel("Pasta com arquivos .pdf para (BANCO DE DADOS):")
        self.pasta_pdf_input = QLineEdit(self)
        self.pasta_pdf_button = QPushButton("Selecionar Pasta", self)
        self.pasta_pdf_button.clicked.connect(self.selecionar_pasta_pdf)

        pasta_pdf_layout.addWidget(self.pasta_pdf_label)
        pasta_pdf_layout.addWidget(self.pasta_pdf_input)
        pasta_pdf_layout.addWidget(self.pasta_pdf_button)
        layout.addLayout(pasta_pdf_layout)

        # Layout para selecionar a pasta de origem .txt
        pasta_layout = QHBoxLayout()
        self.pasta_label = QLabel("Pasta com arquivos .ret:")
        self.pasta_input = QLineEdit(self)
        self.pasta_button = QPushButton("Selecionar Pasta", self)
        self.pasta_button.clicked.connect(self.selecionar_pasta_origem)

        pasta_layout.addWidget(self.pasta_label)
        pasta_layout.addWidget(self.pasta_input)
        pasta_layout.addWidget(self.pasta_button)
        layout.addLayout(pasta_layout)

        # Radio buttons para selecionar o formato de saída
        self.formato_layout = QHBoxLayout()
        self.formato_label = QLabel("Formato de Saída:")
        self.radio_txt = QRadioButton("TXT")
        self.radio_csv = QRadioButton("CSV")
        self.radio_csv.setChecked(True)  # Set CSV as default
        self.formato_layout.addWidget(self.formato_label)
        self.formato_layout.addWidget(self.radio_txt)
        self.formato_layout.addWidget(self.radio_csv)

        self.button_group_formato = QButtonGroup(self)
        self.button_group_formato.addButton(self.radio_txt)
        self.button_group_formato.addButton(self.radio_csv)

        layout.addLayout(self.formato_layout)
        # Layout para selecionar o arquivo de saída

        arquivo_layout = QHBoxLayout()
        self.arquivo_label = QLabel("salvar como:")
        self.arquivo_input = QLineEdit(self)
        self.arquivo_button = QPushButton("Selecionar Local", self)
        self.arquivo_button.clicked.connect(self.selecionar_arquivo_saida)

        arquivo_layout.addWidget(self.arquivo_label)
        arquivo_layout.addWidget(self.arquivo_input)
        arquivo_layout.addWidget(self.arquivo_button)
        layout.addLayout(arquivo_layout)

        # Checkbox para escolher entre incluir ou não os valores
        self.checkbox_valores = QCheckBox("Incluir valores na saída", self)
        self.checkbox_valores.setChecked(True)  # Defina o padrão para "com valores"
        layout.addWidget(self.checkbox_valores)

        # Barra de progresso
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Botão de iniciar
        self.iniciar_button = QPushButton("Iniciar Extração", self)
        self.iniciar_button.clicked.connect(self.iniciar_processamento)
        layout.addWidget(self.iniciar_button)

        # Rodapé com a mensagem de autoria
        rodape_layout = QHBoxLayout()
        self.rodape_label = QLabel("Criado por Max Ramom.F", self)
        self.rodape_label.setAlignment(Qt.AlignCenter)
        rodape_layout.addWidget(self.rodape_label)

        layout.addLayout(rodape_layout)

    def selecionar_pasta_pdf(self):
        pasta_pdf = QFileDialog.getExistingDirectory(
            self, "Selecione a pasta com os arquivos .pdf"
        )
        if pasta_pdf:
            self.pasta_pdf_input.setText(pasta_pdf)

    def selecionar_pasta_origem(self):
        pasta_origem = QFileDialog.getExistingDirectory(
            self, "Selecione a pasta com os arquivos .txt"
        )
        if pasta_origem:
            self.pasta_input.setText(pasta_origem)

    def selecionar_arquivo_saida(self):
        if self.radio_csv.isChecked():
            arquivo_saida, _ = QFileDialog.getSaveFileName(
                self, "Escolha o local para salvar o arquivo", "", "CSV files (*.csv)"
            )
        else:
            arquivo_saida, _ = QFileDialog.getSaveFileName(
                self, "Escolha o local para salvar o arquivo", "", "Text files (*.txt)"
            )

        if arquivo_saida:
            self.arquivo_input.setText(arquivo_saida)

    def iniciar_processamento(self):
        pasta_txt = self.pasta_input.text()
        arquivo_saida = self.arquivo_input.text()
        pasta_pdf = self.pasta_pdf_input.text()
        incluir_valores = self.checkbox_valores.isChecked()
        saida_csv = self.radio_csv.isChecked()

        if not pasta_txt or not arquivo_saida or not pasta_pdf:
            QMessageBox.critical(
                self,
                "Erro",
                "Por favor, selecione a pasta de origem, arquivo de saída e pasta PDF",
            )
            return

        # Alterar a extensão de um arquivo .ret para .txt
        try:
            arquivos_ret = glob.glob(os.path.join(pasta_txt, "*.ret"))
            for arquivo_ret in arquivos_ret:
                arquivo_txt = alterar_extensao_para_txt(arquivo_ret)
                print(f"Arquivo renomeado: {arquivo_txt}")
        except ValueError as e:
            QMessageBox.critical(self, "Erro", str(e))
            return

        # Iniciar o processamento em segundo plano
        self.thread = ProcessadorThread(
            pasta_txt, arquivo_saida, pasta_pdf, incluir_valores, saida_csv
        )
        self.thread.progresso.connect(self.atualizar_barra_progresso)
        self.thread.concluido.connect(self.finalizar_processamento)
        self.thread.start()
        self.iniciar_button.setEnabled(False)

    def atualizar_barra_progresso(self, progresso):
        self.progress_bar.setValue(progresso)

    def finalizar_processamento(self):
        # Exibir mensagem de conclusão e perguntar sobre nova execução
        resposta = QMessageBox.question(
            self,
            "Processamento Concluído",
            "Processamento concluído! Deseja fazer outra execução?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if resposta == QMessageBox.No:
            output_file_path = self.arquivo_input.text()
            self.open_folder(os.path.dirname(output_file_path))
            QApplication.quit()
        else:
            self.resetar_campos()

    def resetar_campos(self):
        self.pasta_pdf_input.clear()
        self.pasta_input.clear()
        self.arquivo_input.clear()
        self.progress_bar.setValue(0)
        self.checkbox_valores.setChecked(True)
        self.iniciar_button.setEnabled(True)


