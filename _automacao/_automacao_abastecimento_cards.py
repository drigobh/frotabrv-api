import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_abast_cards_{agora}.zip"
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

def corrigir_calculo_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Corrige o cálculo: busca o último abastecimento com KM menor que o atual
    alvo = '''    # Cálculo do KM Rodados (se houver abastecimento anterior)
    anterior = await db.abastecimentos.find_one(
        {"veiculo_id": body.veiculo_id, "km": {"$lt": body.km}},
        sort=[("km", -1)]
    )
    km_rodados = body.km - anterior["km"] if anterior else None
    media_km_l = km_rodados / body.litros if km_rodados and body.litros > 0 else None'''

    novo = '''    # Cálculo do KM Rodados: busca o último abastecimento com KM menor que o atual
    anterior = await db.abastecimentos.find_one(
        {"veiculo_id": body.veiculo_id, "km": {"$lt": body.km}},
        sort=[("km", -1)]
    )
    
    # Se não houver abastecimento anterior, usa o hodômetro do cadastro do veículo
    km_anterior = anterior["km"] if anterior else veiculo.get("hodometro_km", 0)
    km_rodados = body.km - km_anterior if km_anterior > 0 else None
    media_km_l = km_rodados / body.litros if km_rodados and body.litros > 0 else None'''

    if alvo in conteudo:
        conteudo = conteudo.replace(alvo, novo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ Backend: Cálculo de KM corrigido (prioriza o último abastecimento ou hodômetro do veículo).")
    else:
        print("⚠️ Aviso: Bloco de cálculo não encontrado no backend.")

def melhorar_cards_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Adicionar novos cálculos no resumo
    alvo_resumo = "const resumo = useMemo(() => {"
    # Encontra o final do bloco de resumo atual e adiciona os novos cálculos
    novo_resumo = '''const resumo = useMemo(() => {
    const litros = rows.reduce((s, r) => s + r.litros, 0);
    const valor = rows.reduce((s, r) => s + r.valor_total, 0);
    const comKm = rows.filter((r) => r.km_rodados != null);
    const km = comKm.reduce((s, r) => s + (r.km_rodados ?? 0), 0);
    const litrosKm = comKm.reduce((s, r) => s + r.litros, 0);
    
    // Novos cálculos
    const maior = rows.reduce((max, r) => r.valor_total > (max?.valor_total || 0) ? r : max, null as Abastecimento | null);
    const menor = rows.reduce((min, r) => r.valor_total < (min?.valor_total || Infinity) ? r : min, null as Abastecimento | null);
    const mediaValor = rows.length ? valor / rows.length : 0;
    const mediaKm = comKm.length ? km / comKm.length : 0;

    return { 
      litros, valor, km, media: litrosKm ? km / litrosKm : 0, preco: litros ? valor / litros : 0,
      maior, menor, mediaValor, mediaKm
    };
  }, [rows]);'''

    if alvo_resumo in conteudo:
        # Encontra o bloco de resumo antigo e substitui
        import re
        pattern = re.compile(r"const resumo = useMemo\(\(\) => \{.*?\}, \[rows\]\);", re.DOTALL)
        conteudo = pattern.sub(novo_resumo, conteudo)

    # 2. Substituir os cards antigos por novos cards
    alvo_cards = '''  const cards = [
    { label: "Total abastecido", valor: `${num(resumo.litros, 1)} L`, testId: "resumo-litros" },
    { label: "Valor total", valor: brl(resumo.valor), testId: "resumo-valor" },
    { label: "Média geral", valor: `${num(resumo.media, 2)} km/L`, testId: "resumo-media" },
    { label: "Preço médio", valor: `${brl(resumo.preco)}/L`, testId: "resumo-preco" },
  ];'''

    novo_cards = '''  const cards = [
    { label: "Maior abastecimento", valor: resumo.maior ? brl(resumo.maior.valor_total) : "—", sub: resumo.maior?.veiculo_label.split(" · ")[0], testId: "resumo-maior" },
    { label: "Menor abastecimento", valor: resumo.menor ? brl(resumo.menor.valor_total) : "—", sub: resumo.menor?.motorista_label || resumo.menor?.veiculo_label.split(" · ")[0], testId: "resumo-menor" },
    { label: "Média por abastecimento", valor: brl(resumo.mediaValor), sub: "R$ por registro", testId: "resumo-media-valor" },
    { label: "Média de KM rodados", valor: `${num(resumo.mediaKm, 0)} km`, sub: "por abastecimento", testId: "resumo-media-km" },
  ];'''

    if alvo_cards in conteudo:
        conteudo = conteudo.replace(alvo_cards, novo_cards)

    # 3. Substituir a renderização dos cards (antiga) pela nova
    alvo_render = '''      <div className="mb-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((c) => (
          <div key={c.label} className="glass rounded-xl px-4 py-3">
            <p className="text-xs text-slate-500">{c.label}</p>
            <p className="mt-1 font-heading text-2xl font-semibold tabular-nums" data-testid={c.testId}>{c.valor}</p>
          </div>
        ))}
      </div>'''

    novo_render = '''      <div className="mb-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((c) => (
          <div key={c.label} className="glass rounded-xl" style={{ padding: '12px 16px', height: '90px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }} data-testid={c.testId}>
            <p style={{ fontSize: '12px', color: '#94a3b8', margin: 0, fontWeight: 500 }}>{c.label}</p>
            <div>
              <p style={{ fontSize: '20px', fontWeight: 600, color: '#f8fafc', margin: 0, lineHeight: 1 }}>{c.valor}</p>
              {c.sub && <p style={{ fontSize: '10px', color: '#64748b', marginTop: '4px' }}>{c.sub}</p>}
            </div>
          </div>
        ))}
      </div>'''

    if alvo_render in conteudo:
        conteudo = conteudo.replace(alvo_render, novo_render)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ Frontend: Novos cards de resumo adicionados e estilizados.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Melhorias no Abastecimento (Cards)...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_calculo_backend(raiz)
    melhorar_cards_frontend(raiz)

    print("🚀 Automação concluída! Faça o commit e push para o Render.")

if __name__ == "__main__":
    executar()