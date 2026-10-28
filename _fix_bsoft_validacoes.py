import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_BSOFT_VALIDACOES_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Abastecimentos.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def remover_funcao(c, nome):
    while True:
        inicio = c.find(f'const {nome} = ')
        if inicio == -1: break
        chave = c.find('{', inicio)
        if chave == -1: break
        count = 0
        i = chave
        while i < len(c):
            if c[i] == '{': count += 1
            elif c[i] == '}':
                count -= 1
                if count == 0:
                    fim = i + 1
                    while fim < len(c) and c[fim] not in '\n;': fim += 1
                    if fim < len(c) and c[fim] == ';': fim += 1
                    break
            i += 1
        c = c[:inicio] + c[fim:]
    return c

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Remove a função antiga do BSOFT
    c = remover_funcao(c, "handleImportXLS")
    print("✅ Função antiga do BSOFT removida.")

    # 2. Insere a nova função (que reutiliza os modais e a execução do Edenred)
    idx_return = c.find('  return (')
    if idx_return == -1:
        print("⚠️ Return não encontrado.")
        return

    nova_funcao = '''  const handleImportXLS = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: "array" });
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const rows = XLSX.utils.sheet_to_json<any[]>(sheet, { header: 1, raw: false });

      let headerIdx = -1;
      for (let i = 0; i < rows.length; i++) {
        const rowStr = rows[i].map((c: any) => String(c).toUpperCase()).join(" ");
        if (rowStr.includes("DATA") && rowStr.includes("PLACA") && rowStr.includes("LITROS")) {
          headerIdx = i;
          break;
        }
      }

      if (headerIdx === -1) { toast.error("Cabeçalho do BSOFT não encontrado."); return; }

      const header = rows[headerIdx].map((c: any) => String(c).toUpperCase().trim());
      const findIdx = (name: string) => header.findIndex(h => h.includes(name));

      const idxData = findIdx("DATA");
      const idxPlaca = findIdx("PLACA");
      const idxKm = findIdx("LEITURA");
      const idxPosto = findIdx("POSTO");
      const idxLitros = findIdx("LITROS");
      const idxValor = findIdx("VALOR");
      const idxPreco = findIdx("V. LITRO");
      const idxProduto = findIdx("PRODUTO");

      const parseNum = (val: any) => {
        if (!val) return 0;
        let str = String(val).replace(/[^0-9.,-]/g, "");
        if (str.includes('.') && str.includes(',')) {
            if (str.lastIndexOf(',') > str.lastIndexOf('.')) str = str.replace(/\\./g, '').replace(',', '.');
            else str = str.replace(/,/g, '');
        } else if (str.includes(',')) {
            str = str.replace(',', '.');
        }
        return Number(str) || 0;
      };

      const mapFornecedores = new Set(fornecedores.map((f: any) => f.nome.toUpperCase().trim()));
      const unregistered = new Map<string, any>();
      const payloads: any[] = [];

      for (let i = headerIdx + 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAIS")) continue;

        let dataStr = String(row[idxData]).trim().split(" ")[0];
        if (dataStr.includes("/")) {
            const parts = dataStr.split("/");
            if (parts.length === 3) {
                let month = parts[0].padStart(2, '0');
                let day = parts[1].padStart(2, '0');
                let year = parts[2];
                if (year.length === 2) year = "20" + year;
                dataStr = `${year}-${month}-${day}`;
            }
        }

        let placaRaw = String(row[idxPlaca] || "").trim();
        const placa = placaRaw.replace("-", "").split("/")[0].toUpperCase();

        if (!placa || placa.length < 7 || placa.includes("BSOFT")) continue;

        const litros = parseNum(row[idxLitros]);
        const preco_litro = parseNum(row[idxPreco]);
        const valor_total = parseNum(row[idxValor]);
        const km = parseNum(row[idxKm]);
        const fornecedorNome = String(row[idxPosto] || "").trim();

        if (fornecedorNome && !mapFornecedores.has(fornecedorNome.toUpperCase().trim())) {
          unregistered.set(fornecedorNome, { nome: fornecedorNome, cidade: "", estado: "", endereco: "", bairro: "" });
        }

        payloads.push({
          data: dataStr,
          placa: placa,
          km: km,
          fornecedor: fornecedorNome,
          litros: litros,
          preco_litro: preco_litro,
          valor_total: valor_total,
          produto: String(row[idxProduto] || "DIESEL").toUpperCase(),
          origem: "bsoft",
          motorista_id: NENHUM,
          cnpj: "",
          codigo_transacao: ""
        });
      }

      const pendentes = Array.from(unregistered.values());
      if (pendentes.length > 0) {
        const initialSelected: Record<string, boolean> = {};
        const initialAvaliacoes: Record<string, number> = {};
        pendentes.forEach(f => {
          initialSelected[f.nome] = true;
          initialAvaliacoes[f.nome] = 0;
        });
        setSelectedFornecedores(initialSelected);
        setAvaliacoesPendentes(initialAvaliacoes);
        setFornecedoresPendentes(pendentes);
        setPendingEdenredRows(payloads);
        setOpenFornecedoresModal(true);
      } else {
        setPendingEdenredRows(payloads);
        setOpenConfirmImport(true);
      }

      e.target.value = "";
    } catch (error) {
      console.error(error);
      toast.error("Erro ao ler o arquivo BSOFT.");
    }
  };
'''

    c = c[:idx_return] + nova_funcao + c[idx_return:]

    # 3. Atualiza o botão de importar BSOFT para usar o estado de loading correto
    c = re.sub(
        r'<Button[^>]*onClick=\{[^}]*xlsInputRef\.current\?\.click\(\)[^}]*\}[^>]*>[\s\S]*?Importar BSOFT[\s\S]*?</Button>',
        '<Button variant="outline" disabled={importandoEdenred || openConfirmImport || openFornecedoresModal} onClick={() => xlsInputRef.current?.click()}><Upload className="size-4 mr-2" /> {importandoEdenred ? "Importando..." : "Importar BSOFT"}</Button>',
        c
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ BSOFT atualizado para usar o mesmo fluxo do Edenred.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)