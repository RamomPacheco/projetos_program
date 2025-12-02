# RetFindErro (GUI)

Aplicação GUI para extrair nomes de arquivos .ret/.txt, cruzar com PDFs (para banco JSON) e gerar CSV/TXT com resultados.

## Estrutura

- app.py (ponto de entrada)
- ui/
  - main_window.py (GUI)
- workers/
  - process_worker.py (thread de processamento)
- services/
  - pdf_extraction.py (leitura e extração de PDFs)
  - ret_processing.py (parse de .ret/.txt, busca no banco e agregação de resultados)
  - db.py (persistência do banco JSON)
- utils/
  - formatting.py (formatação de moeda com fallback)
  - fs.py (abrir pasta no SO)
  - ret_file.py (renomeio .ret -> .txt)
- constants/
  - regex.py (regex utilizadas)

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
python app.py
```

Selecione na interface:
- Pasta com PDFs (para gerar banco JSON)
- Pasta com .ret/.txt
- Local de saída (CSV ou TXT)

## Observações
- Formatação de moeda robusta a locale ausente.
- Regex separadas em constants/regex.py
- Saída CSV com cabeçalho e total ao final; saída TXT agrupada por origem.
