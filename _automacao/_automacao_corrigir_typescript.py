import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_fix_ts_{agora}.zip"
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

def corrigir_typescript(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Corrigir o import do XLSX
    if "import * as XLSX from \"xlsx\";" not in conteudo:
        conteudo = conteudo.replace(
            'import { Fuel, Plus, Trash2, ArrowUpRight, ArrowDownRight, DollarSign, Droplets, Target, TrendingUp, List, Pencil, FileText, Upload } from "lucide-react";',
            'import { Fuel, Plus, Trash2, ArrowUpRight, ArrowDownRight, DollarSign, Droplets, Target, TrendingUp, List, Pencil, FileText, Upload } from "lucide-react";\nimport * as XLSX from "xlsx";'
        )

    # 2. Corrigir a tipagem de Abastecimento (se não existir no types)
    caminho_types = os.path.join(raiz, "frontend", "src", "types", "abastecimentos.ts")
    if os.path.exists(caminho_types):
        with open(caminho_types, 'r', encoding='utf-8') as f:
            content_types = f.read()
        
        # Verifica se os novos campos já existem, se não, adiciona
        if "numero_nf" not in content_types:
            # Encontra o final da interface e insere antes do }
            content_types = content_types.replace(
                "  created_at: string;\n}",
                """  created_at: string;
  numero_nf?: string | null;
  chave_nfe?: string | null;
  hora?: string | null;
  cnpj?: string | null;
  fornecedor?: string | null;
  origem?: "manual" | "pdf";
}"""
            )
            with open(caminho_types, 'w', encoding='utf-8') as f:
                f.write(content_types)
            print("⚙️ types/abastecimentos.ts atualizado com os novos campos.")

    # 3. Corrigir a propriedade testId no FieldSelect (Adicionar fallback)
    # O script anterior removeu os testId, o que quebrou o tipo. Vamos colocar de volta.
    if 'testId="abastecimento-filtro-veiculo"' not in conteudo:
        conteudo = conteudo.replace(
            '<FieldSelect value={filtroVeiculo} onChange={setFiltroVeiculo} options={[{ value: TODOS, label: "Todos os veículos" }, ...veicOpts]} />',
            '<FieldSelect value={filtroVeiculo} onChange={setFiltroVeiculo} options={[{ value: TODOS, label: "Todos os veículos" }, ...veicOpts]} testId="abastecimento-filtro-veiculo" />'
        )

    if 'testId="abastecimento-form-veiculo"' not in conteudo:
        conteudo = conteudo.replace(
            '<FieldSelect value={form.veiculo_id} onChange={handleVeiculoChange} options={veicOpts} placeholder="Selecione o veículo" />',
            '<FieldSelect value={form.veiculo_id} onChange={handleVeiculoChange} options={veicOpts} placeholder="Selecione o veículo" testId="abastecimento-form-veiculo" />'
        )

    if 'testId="abastecimento-form-motorista"' not in conteudo:
        conteudo = conteudo.replace(
            '<FieldSelect value={form.motorista_id} onChange={set("motorista_id")} options={[{ value: NENHUM, label: "— Não informado —" }, ...(motoristas.data ?? []).filter(m => m.ativo).map((m) => ({ value: m.id, label: m.nome }))]} />',
            '<FieldSelect value={form.motorista_id} onChange={set("motorista_id")} options={[{ value: NENHUM, label: "— Não informado —" }, ...(motoristas.data ?? []).filter(m => m.ativo).map((m) => ({ value: m.id, label: m.nome }))]} testId="abastecimento-form-motorista" />'
        )

    # 4. Corrigir testId do ConfirmDialog
    if 'testId="abastecimento-excluir"' not in conteudo:
        conteudo = conteudo.replace(
            'onConfirm={() => excluirId && excluir.mutate(excluirId)}\n      />',
            'onConfirm={() => excluirId && excluir.mutate(excluirId)}\n        testId="abastecimento-excluir"\n      />'
        )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ Arquivo Abastecimentos.tsx atualizado com XLSX e testIds.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção do TypeScript...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_typescript(raiz)

    print("\n🚀 Automação concluída! Faça o commit e push para o Render:")
    print("git add .")
    print("git commit -m 'fix: corrigindo imports e tipagens do abastecimento'")
    print("git push")

if __name__ == "__main__":
    executar()