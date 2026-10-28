import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_FECHAR_MODAIS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Abastecimentos.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Corrigir a função executarImportacaoEdenred para fechar TODOS os modais
    padrao_exec = re.compile(r'const executarImportacaoEdenred = async \(rowsData: any\[\]\) => \{[\s\S]*?\n  \};', re.DOTALL)
    
    nova_exec = '''const executarImportacaoEdenred = async (rowsData: any[]) => {
    if (isImportingEdenredRef.current) return;
    isImportingEdenredRef.current = true;
    
    // Fecha TODOS os modais ANTES de iniciar
    setOpenConfirmImport(false);
    setOpenFornecedoresModal(false);
    setOpenEdenredConfirm(false); // <--- FECHA O MODAL DE "IMPORTAR PLANILHA EDENRED?"
    setOpen(false); // Fecha qualquer outro modal que possa estar aberto
    
    setImportandoEdenred(true);
    setImportProgress({ total: rowsData.length, current: 0, errors: [] });
    
    let importados = 0; const erros: any[] = [];
    
    try {
      for (let i = 0; i < rowsData.length; i++) {
        const payload = rowsData[i];
        try { 
          await apiPost("/abastecimentos/importar", payload); 
          importados++; 
          await new Promise(resolve => setTimeout(resolve, 150));
        } catch (err: any) { 
          erros.push({ linha: i + 1, placa: payload.placa, erro: err.message && err.message.includes("409") ? "Já importado" : (err.message || "Erro") }); 
        }
        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }
      
      setImportProgress(prev => prev ? { ...prev, current: rowsData.length, errors: erros } : null);
      
      if (erros.length === 0) toast.success(`${importados} Edenred importados!`);
      else if (importados > 0) toast.warning(`${importados} importados, mas ${erros.length} deram erro ou já existiam.`);
      else toast.error("Todos os registros já foram importados ou deram erro.");
      
      invalidate();
    } finally {
      // DESLIGA O OVERLAY E LIMPA TUDO
      setImportandoEdenred(false);
      isImportingEdenredRef.current = false;
      setPendingEdenredRows([]);
      setImportProgress(null);
      
      // Garante que todos os modais estejam fechados no final
      setOpenConfirmImport(false);
      setOpenFornecedoresModal(false);
      setOpenEdenredConfirm(false);
      setOpen(false);
    }
  };'''

    if padrao_exec.search(c):
        c = padrao_exec.sub(lambda m: nova_exec, c)
        print("✅ executarImportacaoEdenred corrigida para fechar todos os modais.")
    else:
        print("⚠️ executarImportacaoEdenred não encontrada.")

    # 2. Garantir que o modal de confirmação (openEdenredConfirm) seja fechado ao clicar em "Sim, Importar"
    # Vamos procurar o botão "Sim, Importar" no modal de confirmação
    padrao_botao_confirmar = re.compile(
        r'(<Button[^>]*onClick=\{\(\) => \{[\s\S]*?executarImportacaoEdenred\([\s\S]*?\}\})',
        re.DOTALL
    )
    if padrao_botao_confirmar.search(c):
        # Adiciona o fechamento dos modais no clique do botão
        c = c.replace(
            'executarImportacaoEdenred(pendingEdenredRows);',
            'setOpenConfirmImport(false); setOpenEdenredConfirm(false); executarImportacaoEdenred(pendingEdenredRows);'
        )
        print("✅ Fechamento de modais adicionado no clique de 'Sim, Importar'.")

    # 3. Garantir que o modal de confirmação (openEdenredConfirm) seja fechado no onOpenChange
    c = c.replace(
        '<Dialog open={openEdenredConfirm} onOpenChange={(o) => { if (!importandoEdenred) setOpenEdenredConfirm(o); }}>',
        '<Dialog open={openEdenredConfirm} onOpenChange={(o) => { if (!importandoEdenred) { setOpenEdenredConfirm(o); } }}>'
    )

    # 4. Garantir que o botão "Selecionar Arquivo" feche o modal antes de abrir o seletor
    c = c.replace(
        'onClick={() => edenredInputRef.current?.click()}',
        'onClick={() => { setOpenEdenredConfirm(false); edenredInputRef.current?.click(); }}'
    )
    print("✅ Botão 'Selecionar Arquivo' agora fecha o modal antes de abrir o seletor.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)