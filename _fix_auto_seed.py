import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_AUTO_SEED_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Pneus.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Inserir a lógica de auto-seed assim que o componente monta
    if 'const autoSeedExecutado = React.useRef(false);' not in c:
        c = c.replace(
            'const qc = useQueryClient();',
            '''const qc = useQueryClient();
  const autoSeedExecutado = React.useRef(false);

  // Auto-seed: Popula o banco se estiver vazio (na primeira vez que abre a tela)
  React.useEffect(() => {
    if (!autoSeedExecutado.current && marcasDb.length === 0 && !isLoadingMarcas) {
      autoSeedExecutado.current = true;
      // Dispara o seed em background e força atualizar as queries
      apiPost("/pneus/seed", {}).then(() => {
        qc.invalidateQueries({ queryKey: ["marcas-pneus"] });
        qc.invalidateQueries({ queryKey: ["medidas-pneus"] });
        qc.invalidateQueries({ queryKey: ["modelos-pneus"] });
      }).catch(() => {});
    }
  }, [marcasDb, qc]);'''
        )

    # Adicionar o isLoadingMarcas na query de marcas para não dar loop
    c = c.replace(
        'const { data: marcasDb = [] } = useQuery({ queryKey: ["marcas-pneus"], queryFn: () => apiGet<any[]>("/pneus/marcas") });',
        'const { data: marcasDb = [], isLoading: isLoadingMarcas } = useQuery({ queryKey: ["marcas-pneus"], queryFn: () => apiGet<any[]>("/pneus/marcas") });'
    )

    # Garantir que o React está importado corretamente
    if 'import React' not in c:
        c = 'import React, { useState, useMemo } from "react";\n' + c.replace('import { useState, useMemo } from "react";', '')

    # Garantir que apiPost está importado
    if 'apiPost' not in c.split('from "@/lib/api"')[0]:
        c = c.replace('import { apiGet, apiPut, apiDelete }', 'import { apiGet, apiPost, apiPut, apiDelete }')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Pneus.tsx atualizado com Auto-Seed na inicialização.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")