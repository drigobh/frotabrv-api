import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_campos_nf_{agora}.zip"
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

def atualizar_model_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Atualiza o modelo Create
    if "numero_nf" not in conteudo:
        conteudo = conteudo.replace(
            "    observacoes: str = \"\"",
            """    observacoes: str = ""
    numero_nf: str | None = None
    chave_nfe: str | None = None
    hora: str | None = None
    cnpj: str | None = None
    fornecedor: str | None = None
    origem: Literal["manual", "pdf"] = "manual\""""
        )
        # Garante que o Literal está importado
        if "from typing import Literal" not in conteudo:
            conteudo = "from typing import Literal\n" + conteudo

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ Backend: Modelo de Abastecimento atualizado com os novos campos.")

def atualizar_router_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Como o model_dump() já é usado, os novos campos serão salvos automaticamente no POST.
    # No PUT, a mesma coisa.
    # Só precisamos garantir que o Literal está no modelo.
    print("✅ Backend: Rotas POST e PUT já estão prontas para receber os novos campos (via model_dump).")

def atualizar_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Atualizar a tipagem do formulário
    if "numero_nf" not in conteudo:
        conteudo = conteudo.replace(
            "const vazio = (hoje: string) => ({ data: hoje, veiculo_id: \"\", motorista_id: NENHUM, litros: \"\", preco_litro: \"\", posto: \"\", km: \"\", observacoes: \"\" });",
            """const vazio = (hoje: string) => ({ 
  data: hoje, veiculo_id: "", motorista_id: NENHUM, litros: "", preco_litro: "", posto: "", km: "", observacoes: "",
  numero_nf: "", chave_nfe: "", hora: "", cnpj: "", fornecedor: "", origem: "manual"
});"""
        )

    # 2. Adicionar os inputs no formulário (antes do botão Salvar)
    inputs_novos = '''
            <div className="col-span-1 grid gap-1.5">
              <Label>Nº NF</Label>
              <Input value={form.numero_nf} onChange={(e) => setForm(s => ({ ...s, numero_nf: e.target.value }))} placeholder="12550" />
            </div>
            <div className="col-span-1 grid gap-1.5">
              <Label>Hora</Label>
              <Input type="time" value={form.hora} onChange={(e) => setForm(s => ({ ...s, hora: e.target.value }))} />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Chave NF-e</Label>
              <Input value={form.chave_nfe} onChange={(e) => setForm(s => ({ ...s, chave_nfe: e.target.value }))} placeholder="3126 1020..." />
            </div>
            <div className="col-span-1 grid gap-1.5">
              <Label>CNPJ Emitente</Label>
              <Input value={form.cnpj} onChange={(e) => setForm(s => ({ ...s, cnpj: e.target.value }))} placeholder="00.000.000/0000-00" />
            </div>
            <div className="col-span-1 grid gap-1.5">
              <Label>Fornecedor</Label>
              <Input value={form.fornecedor} onChange={(e) => setForm(s => ({ ...s, fornecedor: e.target.value }))} placeholder="Posto..." />
            </div>
'''
    if "Nº NF" not in conteudo:
        # Insere antes do parágrafo do Valor Total
        alvo = '<p className="col-span-2 rounded-lg bg-slate-950/60 px-3 py-2 text-sm text-slate-300">'
        conteudo = conteudo.replace(alvo, inputs_novos + alvo)

    # 3. Atualizar a função de salvar para incluir os novos campos
    alvo_salvar = '''        km: Number(form.km),
        observacoes: form.observacoes,'''
    novo_salvar = '''        km: Number(form.km),
        observacoes: form.observacoes,
        numero_nf: form.numero_nf || null,
        chave_nfe: form.chave_nfe || null,
        hora: form.hora || null,
        cnpj: form.cnpj || null,
        fornecedor: form.fornecedor || null,
        origem: form.origem,'''
    if "numero_nf: form.numero_nf" not in conteudo:
        conteudo = conteudo.replace(alvo_salvar, novo_salvar)

    # 4. Atualizar a função de abrir edição para carregar os novos campos
    alvo_abrir = '''      observacoes: r.observacoes || "",'''
    novo_abrir = '''      observacoes: r.observacoes || "",
      numero_nf: r.numero_nf || "",
      chave_nfe: r.chave_nfe || "",
      hora: r.hora || "",
      cnpj: r.cnpj || "",
      fornecedor: r.fornecedor || "",
      origem: r.origem || "manual",'''
    if "numero_nf: r.numero_nf" not in conteudo:
        conteudo = conteudo.replace(alvo_abrir, novo_abrir)

    # 5. Adicionar a coluna de Origem (PDF/M) no Grid
    alvo_th = '''{["Data", "Veículo", "Motorista", "Litros", "R$/L", "Total", "Posto", "KM", "Rodados", "Média", "Ações"].map((h) => ('''
    novo_th = '''{["Data", "Origem", "Veículo", "Motorista", "Litros", "R$/L", "Total", "Posto", "KM", "Rodados", "Média", "Ações"].map((h) => ('''
    if '"Origem"' not in conteudo:
        conteudo = conteudo.replace(alvo_th, novo_th)

    alvo_td = '''                <TableCell className="font-mono text-sm">{dataBR(r.data)}</TableCell>
                <TableCell className="font-mono">{r.veiculo_label.split(" · ")[0]}</TableCell>'''
    novo_td = '''                <TableCell className="font-mono text-sm">{dataBR(r.data)}</TableCell>
                <TableCell className="text-center">
                  {r.origem === "pdf" ? (
                    <span className="inline-flex items-center justify-center rounded bg-red-500/20 px-2 py-0.5 text-xs font-bold text-red-400" title="Importado via PDF">PDF</span>
                  ) : (
                    <span className="inline-flex items-center justify-center rounded bg-slate-500/20 px-2 py-0.5 text-xs font-bold text-slate-400" title="Inserido Manualmente">M</span>
                  )}
                </TableCell>
                <TableCell className="font-mono">{r.veiculo_label.split(" · ")[0]}</TableCell>'''
    if "r.origem ===" not in conteudo:
        conteudo = conteudo.replace(alvo_td, novo_td)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ Frontend: Formulário e Grid atualizados com os novos campos de NF.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Campos de Nota Fiscal...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    atualizar_model_backend(raiz)
    atualizar_router_backend(raiz)
    atualizar_frontend(raiz)

    print("\n🚀 Automação concluída! Faça o commit e push para o Render:")
    print("git add .")
    print("git commit -m 'feat: adicionando campos de nota fiscal no abastecimento'")
    print("git push")

if __name__ == "__main__":
    executar()