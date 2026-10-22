import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_abast_{agora}.zip"
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

def corrigir_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Adicionar rota para buscar o último KM do veículo
    rota_km = '''
@router.get("/ultimo-km/{veiculo_id}")
async def ultimo_km(veiculo_id: str, _u: dict = Depends(require("read"))):
    veiculo = await db.veiculos.find_one({"id": veiculo_id})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")
    
    # Busca o último abastecimento registrado para este veículo
    ultimo_abast = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo_id}, 
        sort=[("km", -1)]
    )
    
    km_veiculo = veiculo.get("hodometro_km", 0)
    km_abast = ultimo_abast["km"] if ultimo_abast else 0
    
    # Retorna o maior KM entre o cadastro e o último abastecimento
    return {"ultimo_km": max(km_veiculo, km_abast)}
'''
    if 'ultimo-km' not in conteudo:
        # Insere a nova rota antes da rota de criação (POST)
        alvo = '@router.post("", response_model=Abastecimento, status_code=201)'
        conteudo = conteudo.replace(alvo, rota_km + "\n" + alvo)

    # 2. Adicionar validação de KM no POST
    # Procura pela validação após buscar o veículo
    alvo_valida = 'veiculo = await db.veiculos.find_one({"id": body.veiculo_id})\n    if not veiculo:\n        raise HTTPException(404, "Veículo não encontrado")'
    nova_valida = '''veiculo = await db.veiculos.find_one({"id": body.veiculo_id})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    # Validação do Hodômetro: não pode ser menor que o último registrado
    ultimo_abast = await db.abastecimentos.find_one(
        {"veiculo_id": body.veiculo_id}, 
        sort=[("km", -1)]
    )
    km_cadastro = veiculo.get("hodometro_km", 0)
    km_ultimo_abast = ultimo_abast["km"] if ultimo_abast else 0
    km_minimo = max(km_cadastro, km_ultimo_abast)

    if body.km < km_minimo:
        raise HTTPException(400, f"O hodômetro informado ({body.km}) é menor que o último registrado ({km_minimo}).")'''

    if "Validação do Hodômetro" not in conteudo:
        conteudo = conteudo.replace(alvo_valida, nova_valida)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ Backend: Rota de último KM e validação de hodômetro adicionadas.")

def corrigir_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Filtrar apenas ativos nas opções de veículos e motoristas
    conteudo = conteudo.replace(
        "const veicOpts = (veiculos.data ?? []).map((v) => ({ value: v.id, label: `${v.placa} · ${v.modelo}` }));",
        "const veicOpts = (veiculos.data ?? []).filter(v => v.ativo).map((v) => ({ value: v.id, label: `${v.placa} · ${v.modelo}` }));"
    )
    
    conteudo = conteudo.replace(
        "...(motoristas.data ?? []).map((m) => ({ value: m.id, label: m.nome }))",
        "...(motoristas.data ?? []).filter(m => m.ativo).map((m) => ({ value: m.id, label: m.nome }))"
    )

    # 2. Criar a função para buscar KM e Acoplamento ao selecionar o veículo
    nova_funcao = '''
  const handleVeiculoChange = async (veiculoId: string) => {
    set("veiculo_id")(veiculoId);
    if (!veiculoId) return;

    try {
      // Busca o último KM (do cadastro ou último abastecimento)
      const kmData = await apiGet<{ ultimo_km: number }>(`/abastecimentos/ultimo-km/${veiculoId}`);
      setForm(s => ({ ...s, km: String(kmData.ultimo_km) }));

      // Busca o acoplamento ativo para preencher o motorista
      const acoplamentos = await apiGet<any[]>("/acoplamentos");
      const acoplamentoAtivo = acoplamentos.find(a => a.veiculo_id === veiculoId);
      
      if (acoplamentoAtivo) {
        if (acoplamentoAtivo.motorista_id) {
          setForm(s => ({ ...s, motorista_id: acoplamentoAtivo.motorista_id }));
        }
      } else {
        setForm(s => ({ ...s, motorista_id: NENHUM }));
      }
    } catch (error) {
      console.error("Erro ao buscar dados do veículo:", error);
    }
  };
'''
    # Adiciona a função antes do "return ("
    if "handleVeiculoChange" not in conteudo:
        conteudo = conteudo.replace("  return (", nova_funcao + "\n  return (")

    # 3. Alterar o onChange do select de veículo para usar a nova função
    conteudo = conteudo.replace(
        '<FieldSelect value={form.veiculo_id} onChange={set("veiculo_id")} options={veicOpts} placeholder="Selecione o veículo" testId="abastecimento-form-veiculo" />',
        '<FieldSelect value={form.veiculo_id} onChange={handleVeiculoChange} options={veicOpts} placeholder="Selecione o veículo" testId="abastecimento-form-veiculo" />'
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ Frontend: Filtro de ativos, auto-preenchimento e KM inicial adicionados.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Melhorias no Abastecimento...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_backend(raiz)
    corrigir_frontend(raiz)

    print("🚀 Automação concluída! Faça o commit e push para o Render.")

if __name__ == "__main__":
    executar()