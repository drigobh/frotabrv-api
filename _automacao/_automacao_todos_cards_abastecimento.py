import os
import shutil
import datetime
import zipfile
import re

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_todos_cards_{agora}.zip"
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

def adicionar_todos_cards(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Adicionar os novos cálculos no resumo (se já não existirem)
    if "mediaValor" not in conteudo:
        # Se o script anterior não adicionou, adicionamos agora
        alvo = "return { \n      litros, \n      valor, \n      km, \n      media: litrosKm ? km / litrosKm : 0, \n      preco: litros ? valor / litros : 0,\n      total: rows.length\n    };"
        novo = """const maior = rows.reduce((max, r) => r.valor_total > (max?.valor_total || 0) ? r : max, null as Abastecimento | null);
    const menor = rows.reduce((min, r) => r.valor_total < (min?.valor_total || Infinity) ? r : min, null as Abastecimento | null);
    const mediaValor = rows.length ? valor / rows.length : 0;
    const mediaKm = comKm.length ? km / comKm.length : 0;

    return { 
      litros, 
      valor, 
      km, 
      media: litrosKm ? km / litrosKm : 0, 
      preco: litros ? valor / litros : 0,
      total: rows.length,
      maior, menor, mediaValor, mediaKm
    };"""
        conteudo = conteudo.replace(alvo, novo)

    # 2. Substituir a lista de cards atual pela lista completa
    # Vamos usar regex para achar o bloco de definição de cards
    padrao_cards = r"const cards = \[.*?\];"
    
    novos_cards = '''const cards = [
    { label: "Abastecimentos", valor: resumo.total, icon: List, color: "#38bdf8", sub: "registros no período" },
    { label: "Total Abastecido", valor: `${num(resumo.litros, 1)} L`, icon: Droplets, color: "#2dd4bf", sub: "volume total" },
    { label: "Valor Total", valor: brl(resumo.valor), icon: DollarSign, color: "#fbbf24", sub: "custo total" },
    { label: "Média Geral", valor: `${num(resumo.media, 2)} km/L`, icon: TrendingUp, color: "#a78bfa", sub: "eficiência da frota" },
    { label: "Preço Médio", valor: `${brl(resumo.preco)}/L`, icon: Target, color: "#f87171", sub: "por litro" },
    { label: "Maior Abastecimento", valor: resumo.maior ? brl(resumo.maior.valor_total) : "—", icon: ArrowUpRight, color: "#4ade80", sub: resumo.maior?.veiculo_label.split(" · ")[0] },
    { label: "Menor Abastecimento", valor: resumo.menor ? brl(resumo.menor.valor_total) : "—", icon: ArrowDownRight, color: "#f87171", sub: resumo.menor?.motorista_label || resumo.menor?.veiculo_label.split(" · ")[0] },
    { label: "Média por Abast.", valor: brl(resumo.mediaValor), icon: DollarSign, color: "#fb923c", sub: "R$ por registro" },
    { label: "Média de KM", valor: `${num(resumo.mediaKm, 0)} km`, icon: TrendingUp, color: "#60a5fa", sub: "por abastecimento" },
  ];'''

    conteudo = re.sub(padrao_cards, novos_cards, conteudo, flags=re.DOTALL)

    # 3. Ajustar a grade para suportar 9 cards (talvez 3 colunas em telas médias)
    # O Tailwind já lida com isso se usarmos grid-cols-3 ou grid-cols-4, mas vamos forçar
    conteudo = conteudo.replace(
        '<div className="mb-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">',
        '<div className="mb-5 grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">'
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ Abastecimentos.tsx atualizado com os 9 cards.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação para Trazer Todos os Cards...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    adicionar_todos_cards(raiz)

    print("\n🚀 Automação concluída! Siga os passos:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()
    