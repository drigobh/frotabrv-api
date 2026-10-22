import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_carretas_v2_{agora}.zip"
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

def atualizar_tela_carretas(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Carretas.tsx")
    if not os.path.exists(caminho):
        print("❌ Erro: Carretas.tsx não encontrado.")
        return

    # Código novo que utiliza a arquitetura do CadastroTable
    codigo_novo = '''import { CadastroTable } from "@/components/cadastros/CadastroTable";
import type { Carreta } from "@/types/cadastros";

const TIPOS_CARRETA = [
  { value: "Bau", label: "Bau" },
  { value: "Sider", label: "Sider" },
  { value: "Graneleiro", label: "Graneleiro" },
  { value: "Frigorifico", label: "Frigorífico" },
  { value: "Tanque", label: "Tanque" },
  { value: "Prancha", label: "Prancha" },
  { value: "Cacamba", label: "Caçamba" },
  { value: "Porta-conteiner", label: "Porta-contêiner" },
];

const columns = [
  { key: "codigo", label: "Código" },
  { key: "placa", label: "Placa" },
  { key: "modelo", label: "Modelo" },
  { key: "ano", label: "Ano" },
  { key: "hodometro_km", label: "KM" },
  { key: "tipo", label: "Tipo" },
  { key: "observacoes", label: "Observações" },
];

const fields = [
  { key: "codigo", label: "Código", type: "text", placeholder: "CR-001", required: true },
  { key: "placa", label: "Placa", type: "text", placeholder: "ABC-1234" },
  { key: "modelo", label: "Modelo", type: "text", placeholder: "Ex: Graneleiro" },
  { key: "ano", label: "Ano", type: "number", placeholder: "2024" },
  { key: "hodometro_km", label: "Hodômetro (KM)", type: "number", placeholder: "0" },
  { key: "tipo", label: "Tipo", type: "select", options: TIPOS_CARRETA, required: true },
  { key: "observacoes", label: "Observações", type: "textarea", placeholder: "Opcional" },
];

export default function Carretas() {
  return (
    <CadastroTable<Carreta>
      title="Carretas"
      description="Semirreboques da frota. Inative em vez de excluir."
      endpoint="/carretas"
      entityLabel="carreta"
      testPrefix="carreta"
      columns={columns}
      fields={fields}
      searchKeys={["codigo", "tipo", "placa", "modelo"]}
    />
  );
}
'''

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo_novo)
    print("⚙️ Frontend: Arquivo Carretas.tsx reescrito com os novos campos e a arquitetura correta.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação Visual de Carretas (v2 - Arquitetura)...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    atualizar_tela_carretas(raiz)

    print("🚀 Automação concluída! Faça o commit e push para o Render.")

if __name__ == "__main__":
    executar()