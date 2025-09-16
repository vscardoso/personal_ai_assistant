# Copilot Instructions for AI Coding Agents

## Visão Geral da Arquitetura
- O projeto está dividido em três principais componentes:
  - `app/`: Backend principal, incluindo configuração, API e modelos.
  - `frontend/`: Interface web estática, scripts JS e servidor Python para integração frontend-backend.
  - `models/` e `services/`: Lógica de dados e serviços de IA.
- O banco de dados local é `personal_assistant.db`, manipulado via código Python (veja `models/database.py`).

## Fluxos de Trabalho Essenciais
- **Execução do Backend:**
  - O ponto de entrada é `app/main.py`.
  - Use `python app/main.py` para iniciar o backend.
- **Frontend:**
  - Arquivos HTML e JS em `frontend/`.
  - O servidor Python (`frontend/server.py`) pode ser usado para servir a interface: `python frontend/server.py`.
- **Testes:**
  - Testes estão em `tests/`. Use `pytest tests/` para rodar todos os testes.
- **Dependências:**
  - Instale dependências via `requirements.txt` ou variantes (`requirements_core.txt`, `requirements_simple.txt`).
  - Recomenda-se usar um ambiente virtual Python.

## Padrões e Convenções Específicas
- **Configuração:**
  - Variáveis de ambiente podem ser definidas em `.env`.
  - Configurações do backend estão em `app/config.py`.
- **Modelos e Serviços:**
  - Modelos de dados em `app/models/` e `models/database.py`.
  - Serviços de IA em `services/ai_service.py`.
- **Scripts Frontend:**
  - JS principal: `frontend/script.js` e `frontend/sales-script.js`.
  - CSS: `frontend/styles.css`.
- **Integração:**
  - Comunicação entre frontend e backend via chamadas HTTP (verifique `frontend/server.py` e rotas em `app/api/`).

## Exemplos de Padrões
- Para adicionar um novo endpoint, crie o handler em `app/api/` e registre em `main.py`.
- Para expandir o modelo de dados, edite `models/database.py` e atualize os serviços conforme necessário.
- Para novos testes, adicione arquivos em `tests/` seguindo o padrão do `pytest`.

## Observações Importantes
- Não há instruções de build automatizadas; use comandos Python diretamente.
- O projeto não utiliza frameworks web robustos (ex: Flask, Django) no backend, mas pode ter APIs simples.
- O banco de dados é SQLite local, sem migrações automáticas.

## Referências de Arquivos-Chave
- Backend: `app/main.py`, `app/config.py`, `app/api/`
- Banco de dados: `models/database.py`
- Serviços IA: `services/ai_service.py`
- Frontend: `frontend/index.html`, `frontend/script.js`, `frontend/server.py`
- Testes: `tests/`

---
Essas instruções são específicas para este projeto. Se algum padrão ou fluxo não estiver claro, peça exemplos ou esclarecimentos ao usuário.
