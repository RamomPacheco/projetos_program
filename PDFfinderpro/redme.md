# Processador de PDFs (GUI)

Aplicação para extrair, comparar e destacar nomes/valores entre um PDF de pagamentos e uma pasta com PDFs de projetos.

## Estrutura

- app.py (ponto de entrada)
- ui/
  - main_window.py (GUI)
- workers/
  - process_worker.py (orquestração)
- services/
  - pdf_extraction.py (extração de PDFs)
  - compare.py (comparações exata/parcial)
  - annotate.py (destaque/sublinhar PDF)
  - totals.py (totais nos arquivos .txt)
  - artifacts.py (cópia de artefatos)
- utils/
  - formatting.py (formatação de moeda com fallback)
  - fs.py (abrir pasta no SO)
  - names.py (heurísticas de nomes)
- constants/
  - regex.py (padrões)
  - filenames.py (nomes de arquivos)

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
python app.py
```

Selecione na interface:
- PDF de Pagamentos
- Pasta de PDFs de Projetos
- Pasta de Saída

## Observações

- Formatação de moeda é robusta a ambientes sem locale pt_BR.
- A heurística de comparação parcial usa prefixos do nome para achar correspondências únicas.
- O destaque em PDF usa pymupdf (fitz) e pode variar conforme o texto extraível do PDF.
- Ao final, os totais são atualizados em todos os arquivos .txt e os artefatos são copiados para a pasta específica do projeto.
