# Runbook (Work in progress)

## Goal
This project will provide:
1) A minimal RAG pipeline (ingest → retrieve → answer with citations)
2) An evaluation harness to measure quality and faithfulness

## Planned local setup
- Python 3.10+
- Create a virtual environment
- Install dependencies (to be added in `requirements.txt`)

## Planned commands
These commands will be implemented in future steps:

- `python -m src.ingest --config config.yaml`
- `python -m src.query --config config.yaml --question "..." --show-citations`
- `python -m eval.run --config config.yaml`
- `python eval/run_eval.py` 
- `python src/ingest.py` 
<<<<<<< HEAD
=======
- `python src/index.py` 
>>>>>>> f46b2f377555e1f3661b86de1349a7b6dc523b0f

## Evaluation notes
The evaluation harness will score:
- Retrieval effectiveness (did we fetch the right chunks?)
- Faithfulness (are answers supported by cited text?)
- Quality (basic rubric / LLM-judge, documented)
