import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_EMERGENCIA_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    arquivos = ["app/backend/models/fornecedores.py", "frontend/src/pages/Fornecedores.tsx"]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "fornecedores.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Volta a ser opcional para leitura (None), assim o grid não quebra
    c = c.replace('tipo_fornecedor_id: str  # Obrigatório', 'tipo_fornecedor_id: str | None = None')
    c = c.replace('tipo_fornecedor_id: str', 'tipo_fornecedor_id: str | None = None')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Backend: Model ajustado para não quebrar com fornecedores antigos.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Vamos reescrever a função de Bulk Update para injetar no Backend via API
    if 'const bulkUpdateTipos' in c:
        # Se já existe, substitui a lógica para ser mais robusta
        novo_bulk = '''  const bulkUpdateTipos = useMutation({
    mutationFn: async () => {
      const tipoAlvo = tiposQ.data?.find((t: any) => t.nome.toLowerCase().includes("combustíveis e lubrificantes"));
      if (!tipoAlvo) throw new Error("Tipo 'Combustíveis e lubrificantes' não encontrado.");

      const semTipo = rowsFiltradas.filter(r => !r.tipo_fornecedor_id);
      
      // Faz as requisições PUT para atualizar um por um
      for (const f of semTipo) {
        await apiPut(`/fornecedores/${f.id}`, { ...f, tipo_fornecedor_id: tipoAlvo.id });
      }
      return semTipo.length;
    },
    onSuccess: (qtd) => {
      toast.success(`${qtd} fornecedores atualizados com o tipo "Combustíveis e lubrificantes".`);
      qc.invalidateQueries({ queryKey: ["fornecedores"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro ao preencher em massa.")
  });'''
        c = re.sub(r'const bulkUpdateTipos = useMutation\(\{[\s\S]*?\}\);', novo_bulk, c, count=1)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Lógica de injeção em massa preparada.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("✅ Emergência resolvida!")