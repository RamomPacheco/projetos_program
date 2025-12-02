# Unir PDFs (GUI)

Aplicação para unir múltiplos PDFs em um único arquivo, com suporte a seleção por dialog e drag-and-drop.

## Estrutura
- app.py (ponto de entrada)
- ui/main_window.py (UI)
- services/merge.py (serviço de mesclagem)
- utils/fs.py (abrir pasta no SO)

## Instalação
```bash
pip install -r requirements.txt
```

## Execução
```bash
python app.py
```

## Observações
- A barra de progresso é atualizada por arquivo carregado e define 100% ao concluir a escrita.
- Erros de mesclagem exibem mensagem na UI.
