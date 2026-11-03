import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_CARD_PNEUS_BASE_{agora}.zip")
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

    # 1. Adicionar imports se não existirem
    if 'Disc' not in c.split('lucide-react')[0]:
        c = c.replace(
            'import { Trash2,',
            'import { Disc, Trash2,'
        )
    if 'toast' not in c:
        c = c.replace(
            'import { useState } from "react";',
            'import { useState } from "react";\nimport { toast } from "sonner";'
        )
    if 'apiDelete' not in c:
        c = c.replace(
            'import { apiGet, apiPost } from "@/lib/api";',
            'import { apiGet, apiPost, apiDelete } from "@/lib/api";'
        )
    if 'useQueryClient' not in c:
        c = c.replace(
            'import { useQuery } from "@tanstack/react-query";',
            'import { useQuery, useQueryClient } from "@tanstack/react-query";'
        )

    # 2. Adicionar o hook qc no componente, se não existir
    if 'const qc = useQueryClient();' not in c:
        c = re.sub(
            r'(export default function Base\(\)\s*\{)',
            r'\1\n  const qc = useQueryClient();',
            c
        )

    # 3. Adicionar o card de pneus
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
        # Insere antes do fechamento do grid (procurando o último </div> do grid de cards)
        # Estratégia: procurar o card de Fornecedores e inserir depois dele
        if 'Limpar Fornecedores' in c:
            # Encontra o fechamento do card de Fornecedores e insere o novo card
            c = c.replace(
                '</Button>\n        </div>\n      </div>\n    </div>\n  );',
                '</Button>\n        </div>\n' + card_pneus + '\n      </div>\n    </div>\n  );'
            )
        else:
            # Fallback: insere antes do último </div>
            c = c.replace(
                '      </div>\n    </div>\n  );',
                card_pneus + '\n      </div>\n    </div>\n  );'
            )

        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Frontend: Card de Limpeza de Pneus adicionado.")
    else:
        print("ℹ️ Frontend: Card de Limpeza de Pneus já existe.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")