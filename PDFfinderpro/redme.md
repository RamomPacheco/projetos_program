Processador e Comparador de PDFs de Pagamento
Esta é uma ferramenta de desktop (GUI) construída em PySide6 para automatizar um processo complexo de extração de dados, comparação e auditoria entre um PDF mestre de "Pagamentos" e múltiplos PDFs de "Projetos".
O objetivo principal é encontrar quais nomes/valores de uma pasta de projetos correspondem aos nomes/valores de um PDF de pagamento, gerando relatórios detalhados e um PDF de auditoria com destaques.

🎯 O que este programa faz?
O aplicativo automatiza o seguinte fluxo de trabalho:
Entrada:
PDF de Pagamentos: Um único arquivo PDF que contém a lista mestre de nomes e valores (ex: uma folha de pagamento).
Pasta de PDFs de Projetos: Uma pasta contendo um ou mais arquivos PDF de projetos (ex: listas de alocação de equipe).
Pasta de Saída: O local onde todos os relatórios serão salvos.
Processamento (em Loop):
Para cada arquivo PDF encontrado na pasta Projetos, o programa cria uma nova subpasta com o nome daquele projeto dentro da Pasta de Saída.
Ele extrai nomes e valores monetários de ambos os PDFs (o de Pagamento e o de Projeto atual).
Ele realiza uma comparação complexa para encontrar correspondências entre os dois conjuntos de dados.
A lógica de comparação inclui correspondências exatas e parciais (ex: "JOAO SILVA" pode corresponder a "JOAO S").
Saída (por Projeto):
Dentro de cada subpasta de projeto, ele gera múltiplos arquivos .txt detalhando quais nomes foram encontrados, quais foram encontrados com nomes parciais e quais não foram encontrados.
Ele também gera um novo arquivo *_destacado.pdf, que é uma cópia do PDF de Pagamentos original, mas com os nomes encontrados destacados em amarelo.
Todos os arquivos de texto são atualizados com um cabeçalho de "Total" (contagem de nomes e soma de valores).

✨ Funcionalidades
Interface Gráfica (GUI): Construída com PySide6 para fácil seleção de arquivos e pastas.
Extração de Dados de PDF: Utiliza PyMuPDF (fitz) e PyPDF2 para extrair texto de diferentes layouts de PDF.
Correspondência com Regex: Usa expressões regulares (re) para isolar nomes e valores monetários em formato pt_BR.
Lógica de Comparação Avançada: Encontra correspondências exatas e parciais entre os nomes.
Geração de Relatórios: Cria múltiplos arquivos .txt com os resultados da comparação.
Auditoria Visual em PDF: Gera uma cópia do PDF de pagamentos com os nomes correspondentes destacados (.add_highlight_annot).
Processamento Assíncrono: Usa QThread (Worker) para executar a análise complexa em segundo plano, mantendo a interface responsiva e exibindo o progresso em tempo real.

📦 Requisitos
Este projeto depende das seguintes bibliotecas Python:
Python 3.x
PySide6: Para a interface gráfica.
PyMuPDF: Para extração de texto e destaque em PDF (biblioteca fitz).
PyPDF2: Para extração de texto.
tqdm: Para barras de progresso (usado no backend).

🚀 Instalação
Salve o código do script em um arquivo (ex: processador.py).
(Opcional, mas recomendado) Crie e ative um ambiente virtual:

# Criar ambiente
python -m venv venv

# Ativar no Windows
.\venv\Scripts\activate

# Ativar no macOS/Linux
source venv/bin/activate


Instale as dependências necessárias:
pip install PySide6 PyMuPDF PyPDF2 tqdm


▶️ Como Usar
Execute o script Python a partir do seu terminal:
python processador.py


Na janela do aplicativo:
PDF de Pagamentos: Clique em "Selecionar" e escolha o arquivo PDF mestre que contém os pagamentos.
Pasta de PDFs de Projetos: Clique em "Selecionar" e escolha a pasta que contém todos os PDFs de projetos que você deseja comparar.
Pasta de Saída: Clique em "Selecionar" e escolha uma pasta (geralmente vazia) onde os resultados serão salvos.
Clique em "Iniciar Processamento".
Aguarde a barra de progresso chegar a 100%. O processo pode demorar dependendo da quantidade de arquivos de projeto.
Ao final, uma caixa de diálogo perguntará "Deseja continuar?":
Clicando em "Yes" (Sim), a aplicação reseta os campos, pronta para um novo processamento.
Clicando em "No" (Não), a aplicação tentará abrir a Pasta de Saída principal e será encerrada.
📂 Entendendo os Arquivos de Saída
Após a execução, a sua Pasta de Saída terá a seguinte estrutura:
Pasta de Saída/
│
├── [Nome_do_Projeto_1]/
│   ├── dados_pdf_pagos.txt
│   ├── dados_pdf_projeto.txt
│   ├── Funcionarios_encontrados.txt
│   ├── Funcionarios_nomes_diferente.txt
│   ├── Nomes não encontrados.txt
│   └── [Nome_do_Projeto_1]_destacado.pdf
│
└── [Nome_do_Projeto_2]/
    ├── dados_pdf_pagos.txt
    ├── ... (etc.)


Descrição de cada arquivo (dentro de cada pasta de projeto):
dados_pdf_pagos.txt: Os dados brutos (Nome: Valor) extraídos do PDF de Pagamentos.
dados_pdf_projeto.txt: Os dados brutos (Nome: Valor) extraídos do PDF de Projeto correspondente.
Funcionarios_encontrados.txt: A lista principal de auditoria. Contém todos os nomes do PDF de Projeto que tiveram correspondência (exata ou parcial) encontrada no PDF de Pagamentos.
Funcionarios_nomes_diferente.txt: Um relatório de log detalhando como as correspondências parciais foram encontradas (ex: Original: JOAO P SILVA -> Encontrado como: JOAO P).
Nomes não encontrados.txt: Uma lista de nomes que estavam no PDF do Projeto, mas que não foram encontrados no PDF de Pagamentos por nenhuma lógica.
*_destacado.pdf: O resultado visual. É uma cópia do PDF de Pagamentos com os nomes de Funcionarios_encontrados.txt destacados em amarelo para fácil conferência.
