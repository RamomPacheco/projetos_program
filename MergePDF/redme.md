PDF Simple Merger (Unir PDFs)
Este é um aplicativo de desktop simples, construído com PySide6 e PyPDF2, que permite ao usuário selecionar múltiplos arquivos PDF e uni-los em um único documento.

✨ Funcionalidades
Unir múltiplos arquivos PDF: Combine vários documentos PDF em um único arquivo de saída.
Interface Gráfica Simples: Fácil de usar, construído com a biblioteca PySide6 (Qt for Python).
Seleção de Arquivos: Adicione arquivos usando um diálogo de seleção de arquivos.
Arrastar e Soltar (Drag and Drop): Arraste arquivos PDF diretamente da sua pasta para a lista do aplicativo.
Nome de Saída Personalizado: O usuário pode definir o nome do arquivo final (o padrão é pdf_unificado).
Barra de Progresso: Acompanhe visualmente o processo de união dos arquivos.
Ação Pós-Conclusão: Após a união, o aplicativo pergunta se o usuário deseja continuar ou sair (abrindo a pasta de destino).

📦 Requisitos
Este projeto depende das seguintes bibliotecas Python:
Python 3.x
PySide6: Para a interface gráfica.
PyPDF2: Para a manipulação e união dos arquivos PDF.

🚀 Instalação
Salve o código do script em um arquivo (ex: unir_pdf.py).
(Opcional, mas recomendado) Crie e ative um ambiente virtual:

# Criar ambiente
python -m venv venv

# Ativar no Windows
.\venv\Scripts\activate

# Ativar no macOS/Linux
source venv/bin/activate


Instale as dependências necessárias:
pip install PySide6 PyPDF2


▶️ Como Usar
Execute o script Python a partir do seu terminal:
python unir_pdf.py


Na janela do aplicativo:
Clique em "Selecionar PDFs" para adicionar arquivos através do gerenciador de arquivos.
Ou arraste e solte os arquivos PDF diretamente na área da lista.
(Opcional) No campo "Nome do arquivo de saída", digite o nome desejado para o seu arquivo final (sem a extensão .pdf).
Clique em "Juntar PDFs".
Uma janela se abrirá para que você escolha a pasta de destino onde o PDF unificado será salvo.
Aguarde a barra de progresso chegar a 100%.
Ao final, uma caixa de diálogo perguntará "Deseja continuar?":
Clicando em "Yes" (Sim), a aplicação reseta e fica pronta para uma nova união de arquivos.
Clicando em "No" (Não), a aplicação tentará abrir a pasta onde o arquivo foi salvo e, em seguida, será encerrada.

⚠️ Observação Importante
Para que a funcionalidade de "abrir a pasta de destino" (ao clicar em "Não" após a união) funcione corretamente no macOS e Linux, o módulo subprocess é necessário.
O código-fonte utiliza subprocess.Popen, mas a importação não está presente no topo do arquivo fornecido. Certifique-se de adicionar a seguinte linha junto aos outros imports no início do seu script para que essa funcionalidade funcione nessas plataformas:
import subprocess 


