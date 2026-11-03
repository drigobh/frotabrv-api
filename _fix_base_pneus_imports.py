import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_BASE_IMPORTS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Base.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Base.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Base.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Garantir que useQueryClient está importado
    if 'useQueryClient' not in c.split('from "@tanstack/react-query"')[0]:
        # Se já existe um import de @tanstack/react-query, adiciona useQueryClient nele
        m = re.search(r'import\s*\{([^}]+)\}\s*from\s*["\']@tanstack/react-query["\']', c)
        if m:
            imports_atuais = m.group(1)
            if 'useQueryClient' not in imports_atuais:
                novos_imports = imports_atuais.strip() + ', useQueryClient'
                c = c[:m.start(1)] + novos_imports + c[m.end(1):]
        else:
            # Se não existe import de react-query, adiciona no topo
            c = 'import { useQueryClient } from "@tanstack/react-query";\n' + c
        print("✅ Import do useQueryClient garantido.")

    # 2. Garantir que apiDelete está importado
    if 'apiDelete' not in c.split('from "@/lib/api"')[0]:
        m = re.search(r'import\s*\{([^}]+)\}\s*from\s*["\']@/lib/api["\']', c)
        if m:
            imports_atuais = m.group(1)
            if 'apiDelete' not in imports_atuais:
                c = c[:m.start(1)] + imports_atuais.strip() + ', apiDelete' + c[m.end(1):]
        else:
            c = 'import { apiDelete } from "@/lib/api";\n' + c
        print("✅ Import do apiDelete garantido.")

    # 3. Garantir que toast está importado
    if 'toast' not in c.split('from "sonner"')[0]:
        c = 'import { toast } from "sonner";\n' + c
        print("✅ Import do toast garantido.")

    # 4. Garantir que Disc está importado
    if 'Disc' not in c.split('from "lucide-react"')[0]:
        m = re.search(r'import\s*\{([^}]+)\}\s*from\s*["\']lucide-react["\']', c)
        if m:
            imports_atuais = m.group(1)
            if 'Disc' not in imports_atuais:
                c = c[:m.start(1)] + imports_atuais.strip() + ', Disc' + c[m.end(1):]
        else:
            c = 'import { Disc, Trash2 } from "lucide-react";\n' + c
        print("✅ Import do Disc garantido.")

    # 5. Garantir que const qc = useQueryClient() está dentro do componente
    if 'const qc = useQueryClient();' not in c:
        # Encontra a assinatura da função do componente e insere o qc depois
        c = re.sub(
            r'(export default function Base\(\)\s*\{)',
            r'\1\n  const qc = useQueryClient();',
            c
        )
        print("✅ const qc = useQueryClient() inserido no componente.")

    # 6. Verificar se o card de pneus já existe
    if 'Limpar Pneus' not in c:
        card_pneus = '''
        {/* Card de Pneus */}
        <div className="glass rounded-xl border border-slate-800 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-sky-500/10">
              <Disc className="size-5 text-sky-400" />
            </div>
            <h3 className="text-lg font-bold text-slate-100">Pneus</h3>
          </div>
          <p className="text-sm text-slate-400 mb-6">Apaga todos os registros da tabela.</p>
          <Button 
            variant="destructive" 
            className="w-full bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30"
            onClick={async () => {
              if (confirm("Tem certeza que deseja apagar TODOS os pneus? Esta ação não pode ser desfeita.")) {
                try {
                  await apiDelete("/pneus/limpar");
                  toast.success("Todos os pneus foram removidos.");
                  qc.invalidateQueries({ queryKey: ["pneus"] });
                  qc.invalidateQueries({ queryKey: ["pneus-dashboard"] });
                } catch (e: any) {
                  toast.error(e.message || "Erro ao limpar pneus.");
                }
              }
            }}
          >
            <Trash2 className="size-4 mr-2" /> Limpar Pneus
          </Button>
        </div>
'''
        # Insere antes do último </div> do grid de cards
        if 'Limpar Fornecedores' in c:
            c = c.replace(
                '</Button>\n        </div>\n      </div>\n    </div>\n  );',
                '</Button>\n        </div>\n' + card_pneus + '\n      </div>\n    </div>\n  );'
            )
        else:
            c = c.replace(
                '      </div>\n    </div>\n  );',
                card_pneus + '\n      </div>\n    </div>\n  );'
            )
        print("✅ Card de Limpeza de Pneus adicionado.")
    else:
        print("ℹ️ Card de Limpeza de Pneus já existe.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Base.tsx atualizado com sucesso.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso! O Vite deve recarregar automaticamente.")