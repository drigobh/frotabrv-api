import os
import re
import ast
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_LIMPEZA_BASE_PNEUS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/routers/pneus.py",
        "frontend/src/pages/BaseLimpeza.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "pneus.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    if 'async def limpar_pneus' not in c:
        # Adiciona a rota de limpeza antes da rota de PUT /{id}
        rota_limpeza = '''
@router.delete("/limpar")
async def limpar_pneus(_u: dict = Depends(require("delete"))):
    await db.pneus.delete_many({})
    return {"ok": True, "message": "Todos os pneus foram removidos."}

'''
        c = c.replace('@router.put("/{id}", response_model=Pneu)', rota_limpeza + '@router.put("/{id}", response_model=Pneu)')
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota /pneus/limpar adicionada.")
    else:
        print("ℹ️ Backend: Rota /pneus/limpar já existe.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "BaseLimpeza.tsx")
    if not os.path.exists(caminho):
        print("⚠️ Arquivo BaseLimpeza.tsx não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar imports se não existirem
    if 'Disc' not in c.split('lucide-react')[0]:
        c = c.replace(
            'import { Trash2,',
            'import { Disc, Trash2,'
        )
    if 'apiDelete' not in c:
        c = c.replace(
            'import { apiGet, apiPost } from "@/lib/api";',
            'import { apiGet, apiPost, apiDelete } from "@/lib/api";'
        )
    if 'toast' not in c:
        c = c.replace(
            'import { useState } from "react";',
            'import { useState } from "react";\nimport { toast } from "sonner";'
        )
    if 'useQueryClient' not in c:
        c = c.replace(
            'import { useQuery } from "@tanstack/react-query";',
            'import { useQuery, useQueryClient } from "@tanstack/react-query";'
        )

    # 2. Garantir que o hook qc está dentro do componente
    if 'const qc = useQueryClient();' not in c:
        # Encontra a linha do export default function e insere o qc na primeira linha do componente
        c = re.sub(
            r'(export default function BaseLimpeza\(\)\s*\{)',
            r'\1\n  const qc = useQueryClient();',
            c
        )

    # 3. Adicionar o card de pneus no grid (antes do fechamento da div dos cards)
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
        # Insere antes do fechamento da div que contém os cards (geralmente o último </div> do grid)
        # Vamos buscar pelo card de Fornecedores para inserir logo depois
        if 'Limpar Fornecedores' in c:
            c = c.replace(
                '</div>\n        </div>\n      </div>',
                card_pneus + '\n        </div>\n      </div>'
            )
        else:
            # Se não achar, insere no final do bloco de cards
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
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado com sucesso!")