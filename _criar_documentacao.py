import os

def criar_documentacao():
    conteudo = """# 📑 Documentação do Módulo de Abastecimentos (Status: 100% Funcional)

Este documento registra o estado atual e as regras de negócio do módulo de Abastecimentos, garantindo que futuras alterações não quebrem o que já foi conquistado.

## 1. Fontes de Importação Suportadas
O sistema está preparado para receber dados de 4 formas distintas, sem que uma interfira na outra:
- **Manual**: Preenchimento no formulário.
- **PDF**: Leitura de Nota Fiscal eletrônica.
- **Edenred**: Leitura de planilha Excel (.xlsx) do sistema Edenred.
- **BSOFT**: Leitura de planilha exportada do sistema BSOFT TMS.

## 2. Regras de Duplicidade (Segurança)
O sistema agora bloqueia a importação de registros repetidos de forma inteligente:
- **PDF**: Bloqueia pela Chave NF-e ou Número da NF + CNPJ.
- **Edenred**: Bloqueia pelo Código de Transação (Coluna A).
- **BSOFT**: Bloqueia pela combinação de Placa + Data + Litros.
- **Manual**: Pode ser criado, mas sempre com um aviso prévio de validação se já existir algo parecido.

## 3. Mapeamento de Importação (Edenred & BSOFT)
- **Edenred**: Lê as colunas fixas (A = Código, E = Data, F = Placa, L = Motorista, N = Produto, O = Litros, P = Preço, Q = KM, T = Valor Total, V = Posto, Z = Cidade, AA = UF). Valores decimais lidos corretamente (aceita vírgula ou ponto).
- **BSOFT**: Faz varredura dinâmica do cabeçalho. A placa é limpa (ex: QPN-5250/MG vira QPN5250). A data é convertida de americano (M/D/YY) para o padrão brasileiro (DD/MM/YYYY) antes de salvar.
- **Data no Grid**: Sempre exibida no padrão `DD/MM/YYYY`, independentemente da origem.

## 4. Regras de Cálculo (KM, Média e Valor)
- **Cálculo de Média (KM/L)**: Usa o Hodômetro Inicial do Veículo se for o primeiro abastecimento. Para os seguintes, usa o KM do último abastecimento. A média ignora abastecimentos de ARLA.
- **Valor Total**: Calculado como `Litros * Preço/L`, com proteção contra erros de formatação de float.
- **Cards do Topo (KPIs)**: O cálculo dos cards lê diretamente os valores numéricos do banco (com `parseFloat`), refletindo os valores exatos da planilha.

## 5. Visual e Usabilidade (Frontend)
- **Colunas do Grid**: Data, Origem (Bsoft em laranja, Excel em verde, PDF em vermelho), NF, Cód.Trans, Veículo, Motorista, Produto, Litros, R$/L, Total, Posto (com estrelas de avaliação), KM, Rodados, Média, Ações.
- **Formulário**:
  - O campo **Veículo** é o primeiro, para puxar o hodômetro correto.
  - Importações (PDF, Edenred, BSOFT) deixam todos os campos bloqueados (readOnly/disabled) e com cor roxa. O botão de salvar também é desativado na edição.
  - O campo **CNPJ** tem busca online via BrasilAPI (evitando erro de CORS no Backend). Se o fornecedor não existir, é possível cadastrá-lo na hora, com direito a dar a nota de avaliação por estrelas.
  - O valor total tem um destaque visual (fundo escuro, texto verde grande).

## 6. Arquivos Modificados Principais
- `frontend/src/pages/Abastecimentos.tsx`
- `app/backend/routers/abastecimentos.py`
- `app/backend/models/abastecimentos.py`
"""
    caminho = os.path.join(os.getcwd(), "DOCUMENTACAO_ABASTECIMENTOS.md")
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print(f"✅ Documentação criada em: {caminho}")

if __name__ == "__main__":
    criar_documentacao()