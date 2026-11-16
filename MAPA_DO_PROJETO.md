# 🗺️ Mapa do Projeto - Bravus Frota

**Última atualização:** 15/11/2026
**Status Geral:** Módulos principais (Frota, Financeiro, Compras) concluídos. Em transição para a API Oficial da Meta (WhatsApp).

---

## ✅ 1. O Que Já Temos (Concluído e Funcional)

### 1.1. Infraestrutura e Arquitetura
- **Frontend:** React (Vite) + TypeScript + Tailwind CSS. Totalmente responsivo (desktop e mobile).
- **Backend:** Python (FastAPI) + MongoDB Atlas.
- **Hospedagem:** Render (Frontend e Backend no ar).
- **Autenticação:** Login com JWT, controle de sessão e Timer de inatividade configurável por perfil.
- **RBAC:** Controle de acesso baseado em perfis, com permissões granulares por módulo.

### 1.2. Módulo de Frota e Operações
- **Veículos:** CRUD completo, Ficha 360º (histórico completo do veículo).
- **Pneus:** Controle de desgaste, movimentações (aplicação/remoção), dashboard de KPIs e importação via Excel/XML.
- **Abastecimentos:** Registro de abastecimentos com cálculo de média de consumo e custo por KM.
- **Manutenção:** Agendamento de planos, gestão de Ordens de Serviço (OS) e alertas de vencimento.
- **Checklist de Viagem:**
  - Tela visual dividida em 5 categorias (Elétrica, Pneus, Documentação, Mecânica, Chassi).
  - Numeração sequencial automática (CHK-00001).
  - Alerta visual (caminhão pulsando) para checklists reprovados.
  - Histórico detalhado de correção (auditoria de itens corrigidos e responsável).
  - Geração de PDF (via navegador) para impressão.
  - Filtros por Veículo, Motorista e Data.

### 1.3. Módulo Financeiro
- **Contas a Pagar/Receber:** Grid completo com filtros por mês/ano (incluindo "Todos os Meses").
- **Histórico de Baixa/Estorno:** Auditoria com data/hora e usuário responsável.
- **Conciliação:** Aba comparativa de receitas e despesas.
- **Importação de XML (NF-e/CT-e):** 
  - Parser inteligente com extração de dados.
  - Geração de DANFE/DACTE (layout A4, código de barras CODE128C).
  - Validação de fornecedor (bloqueia importação se o CNPJ não estiver cadastrado).
  - Criação automática de Contas a Pagar.

### 1.4. Módulo de Compras e Orçamentos
- **Cadastro de Compras:** Gestão de alçadas (Compradores e Aprovadores) com limites de valor e histórico de alterações.
- **Orçamentos Híbridos:** Mistura de fornecedores manuais (cadastrados) e fornecedores encontrados por IA (simulada).
- **Análise de Aprovação:** Tela comparativa com destaque para o "Melhor Preço", classificação de fornecedores, prazos e condições.
- **Rastreabilidade:** Registro de quem criou, quem aprovou/reprovou e data/hora.
- **Transformação:** Orçamento aprovado gera automaticamente um Pedido de Compra (OC).

---

## 🚧 2. Em Andamento (Fase Atual)

### 2.1. Integração WhatsApp (API Oficial da Meta)
- [x] Remoção completa do WAHA (código, rotas, menus e serviços no Render).
- [x] Criação do serviço `meta_whatsapp.py` no backend.
- [x] Criação da rota de teste `POST /api/meta-whatsapp/testar`.
- [ ] **Pendente:** Criar Portfólio Empresarial no `business.facebook.com`.
- [ ] **Pendente:** Obter Token de Acesso e Phone Number ID no Meta for Developers.
- [ ] **Pendente:** Configurar variáveis no Render (`META_WHATSAPP_TOKEN`, `META_PHONE_NUMBER_ID`).
- [ ] **Pendente:** Testar envio de mensagem real.
- [ ] **Pendente:** Integrar notificações automáticas no fluxo de Orçamentos.

---

## 📅 3. Backlog (Próximos Passos)

- [ ] **Recebimento de Mercadoria:** Dar entrada no estoque após a aprovação da compra.
- [ ] **Vincular XML ao Pedido de Compra:** Amarrar a NF-e ao pedido (hoje ela vai direto para o Financeiro).
- [ ] **App do Motorista:** Tela dedicada para o motorista fazer o Checklist pelo celular.
- [ ] **Checklist via QR Code:** Ler o QR Code do caminhão para preencher o Checklist automaticamente.
- [ ] **2FA Real:** Autenticação de dois fatores (Google Authenticator/TOTP).
- [ ] **Automação de Backup:** Enviar backups `.zip` automaticamente para o Google Drive.
- [ ] **Relatórios Avançados:** BI de custos por veículo, fornecedor e período.

---

## 🛠️ 4. Tecnologias

- **Backend:** Python (FastAPI), MongoDB Atlas.
- **Frontend:** React (Vite), TypeScript, Tailwind CSS, React Query.
- **Hospedagem:** Render (Backend e Frontend).
- **Integrações:** Meta Cloud API (WhatsApp), API de CNPJ (Busca de Fornecedores), JsBarcode (DANFE/DACTE).
- **Versionamento:** GitHub (`drigobh/frotabrv-api`).

---

## 🚨 5. Regras de Ouro (Lições Aprendidas)

1. **Nunca commitar `node_modules`:** O `.gitignore` deve sempre bloquear `node_modules/`, `dist/`, `.env`, `_automacao/` e `_fix_*.py`.
2. **Imports no Backend:** Sempre usar imports relativos (ex: `from models.x import y`). Nunca usar `app.` no início.
3. **Cache do Vite:** Se o frontend não atualizar, rodar `Remove-Item -Recurse -Force node_modules\.vite` e reiniciar o Vite.
4. **Datas no HTML:** O `<input type="date">` só aceita `YYYY-MM-DD`. Sempre usar a função `parseDate`.
5. **Deploy no Render:** Aguardar o log `Your service is live 🎉` antes de testar.
6. **IDs únicos:** Sempre usar `uuid` no backend para IDs de documentos, nunca confiar em IDs gerados pelo frontend.