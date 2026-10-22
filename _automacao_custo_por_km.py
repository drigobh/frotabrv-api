import os
import shutil
import datetime
import zipfile
import re

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_custo_km_{agora}.zip"
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print(f"📦 Criando Backup Full do Sistema...")
    ignorar = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build']
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta_alvo in ['app', 'frontend']:
            caminho_pasta = os.path.join(raiz, pasta_alvo)
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in ignorar]
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try:
                        zipf.write(caminho_completo, caminho_relativo)
                    except Exception:
                        pass
    print(f"✅ Backup Full salvo em: _automacao/backups/{nome_backup}")

def adicionar_card_custo_km(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Adicionar o cálculo do custo por km no resumo
    # Precisamos calcular o total de custo (abastecimentos) e dividir pelos km rodados
    # (O custo de manutenção não está nesta tela, então usamos apenas o custo dos abastecimentos)
    
    # Encontra o bloco de retorno do useMemo e adiciona o cálculo
    alvo = "return { \n      litros, \n      valor, \n      km, \n      media: litrosKm ? km / litrosKm : 0, \n      preco: litros ? valor / litros : 0,\n      total: rows.length,\n      maior, menor, mediaValor, mediaKm\n    };"
    
    novo = """const custoPorKm = km > 0 ? valor / km : 0;

    return { 
      litros, 
      valor, 
      km, 
      media: litrosKm ? km / litrosKm : 0, 
      preco: litros ? valor / litros : 0,
      total: rows.length,
      maior, menor, mediaValor, mediaKm, custoPorKm
    };"""
    
    if alvo in conteudo:
        conteudo = conteudo.replace(alvo, novo)
    else:
        # Se o script anterior não adicionou os cálculos do maior/menor, fazemos agora
        alvo_antigo = "return { \n      litros, \n      valor, \n      km, \n      media: litrosKm ? km / litrosKm : 0, \n      preco: litros ? valor / litros : 0,\n      total: rows.length\n    };"
        novo_antigo = """const maior = rows.reduce((max, r) => r.valor_total > (max?.valor_total || 0) ? r : max, null as Abastecimento | null);
    const menor = rows.reduce((min, r) => r.valor_total < (min?.valor_total || Infinity) ? r : min, null as Abastecimento | null);
    const mediaValor = rows.length ? valor / rows.length : 0;
    const mediaKm = comKm.length ? km / comKm.length : 0;
    const custoPorKm = km > 0 ? valor / km : 0;

    return { 
      litros, 
      valor, 
      km, 
      media: litrosKm ? km / litrosKm : 0, 
      preco: litros ? valor / litros : 0,
      total: rows.length,
      maior, menor, mediaValor, mediaKm, custoPorKm
    };"""
        if alvo_antigo in conteudo:
            conteudo = conteudo.replace(alvo_antigo, novo_antigo)
        else:
            print("⚠️ Aviso: O bloco de retorno do resumo não foi encontrado. Verifique se o arquivo foi alterado.")

    # 2. Adicionar o novo card na lista de cards
    # Encontra a lista de cards e adiciona o novo card no final
    alvo_cards = "  ];"
    novo_card = """    { label: "Custo por KM", valor: brl(resumo.custoPorKm), icon: DollarSign, color: "#34d399", sub: "combustível por km" },
  ];"""
    
    if alvo_cards in conteudo:
        # Verifica se o card já existe para não duplicar
        if "Custo por KM" not in conteudo:
            conteudo = conteudo.replace(alvo_cards, novo_card)
            print("⚙️ Card 'Custo por KM' adicionado com sucesso.")
        else:
            print("ℹ️ O card 'Custo por KM' já existe.")
    else:
        print("⚠️ Aviso: A lista de cards não foi encontrada.")

    # 3. Ajustar a grade para suportar 10 cards (2 linhas de 5)
    # Muda a classe da div que contém os cards
    if "xl:grid-cols-5" not in conteudo:
        conteudo = conteudo.replace(
            "lg:grid-cols-4",
            "lg:grid-cols-5"
        )
        conteudo = conteudo.replace(
            "xl:grid-cols-5",
            "xl:grid-cols-5" # Já está, só garante que não duplique
        )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ Arquivo Abastecimentos.tsx atualizado com o novo card.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Custo por KM...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    adicionar_card_custo_km(raiz)

    print("\n🚀 Automação concluída! Siga os passos:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()