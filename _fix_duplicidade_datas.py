import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_DUPLICIDADE_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for p in ["frontend/src/pages/Abastecimentos.tsx", "app/backend/routers/abastecimentos.py"]:
            caminho_abs = os.path.join(raiz, p)
            if os.path.exists(caminho_abs):
                zipf.write(caminho_abs, p)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    alvo = '    await db.abastecimentos.insert_one(doc)'
    if alvo in c:
        if 'codigo_transacao_recebido' not in c:
            bloco_checagem = '''    # Trava de Segurança: Bloqueio de Importação Duplicada
    codigo_transacao_recebido = body.get("codigo_transacao")
    
    if codigo_transacao_recebido:
        existente = await db.abastecimentos.find_one({"codigo_transacao": codigo_transacao_recebido})
        if existente:
            raise HTTPException(409, "Registro duplicado: Código de Transação já importado.")
    
    # Se não tiver código (BSOFT), checa por placa + data + litros
    existente_placa = await db.abastecimentos.find_one({
        "veiculo_id": veiculo["id"],
        "data": data_abast,
        "litros": litros
    })
    if existente_placa:
        raise HTTPException(409, "Registro duplicado: Abastecimento com esta placa, data e litros já existe.")

'''
            c = c.replace(alvo, bloco_checagem + alvo)
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Backend: Trava de Duplicidade ativada com sucesso!")
        else:
            print("ℹ️ Backend: Trava de duplicidade já existe.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Forçar a data a ser exibida no padrão DD/MM/YYYY no Grid
    if 'const formatData = ' not in c:
        c = c.replace(
            'const formatCnpj = (val: string) => {',
            '''const formatData = (d: string) => {
  if (!d) return "—";
  if (d.includes("/")) return d;
  if (d.includes("-")) {
      const parts = d.split("T")[0].split("-");
      if (parts.length === 3) return `${parts[2]}/${parts[1]}/${parts[0]}`;
  }
  return d;
};

const formatCnpj = (val: string) => {'''
        )
    
    c = c.replace('{dataBR(r.data)}', '{formatData(r.data)}')

    # 2. Atualizar BSOFT (Data e Tratamento de Erro)
    padrao_bsoft = re.compile(r'const handleImportXLS = async[\s\S]*?\n  \};', re.DOTALL)
    nova_funcao_bsoft = '''const handleImportXLS = async (e: React.ChangeEvent<HTMLInputElement>) => {
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

      const totalLinhas = rows.length - headerIdx - 1;
      setImportProgress({ total: totalLinhas, current: 0, errors: [] });
      let importados = 0; const erros: any[] = [];

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

      for (let i = headerIdx + 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAIS")) continue;

        let dataStr = String(row[idxData]).trim().split(" ")[0]; 

        let placaRaw = String(row[idxPlaca] || "").trim();
        const placa = placaRaw.replace("-", "").split("/")[0].toUpperCase();

        if (!placa || placa.length < 7 || placa.includes("BSOFT")) continue;

        const litros = parseNum(row[idxLitros]);
        const preco_litro = parseNum(row[idxPreco]);
        const valor_total = parseNum(row[idxValor]);
        const km = parseNum(row[idxKm]);

        const payload = {
          data: dataStr,
          placa: placa,
          km: km,
          fornecedor: String(row[idxPosto] || "").trim(),
          litros: litros,
          preco_litro: preco_litro,
          valor_total: valor_total,
          produto: String(row[idxProduto] || "DIESEL").toUpperCase(),
          origem: "bsoft"
        };

        try { 
          await apiPost("/abastecimentos/importar", payload); 
          importados++; 
          await new Promise(r => setTimeout(r, 150)); 
        } catch (err: any) { 
          if (err.message && err.message.includes("409")) {
            erros.push({ linha: i + 1, placa: placa, erro: "Já importado (duplicado)" });
          } else {
            erros.push({ linha: i + 1, placa: placa, erro: err.message || "Erro" }); 
          }
        }
        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }

      setImportProgress(prev => prev ? { ...prev, current: totalLinhas, errors: erros } : null);
      if (erros.length === 0) {
        toast.success(`${importados} registros BSOFT importados!`);
      } else if (importados > 0) {
        toast.warning(`${importados} importados, mas ${erros.length} já existiam ou deram erro.`);
      } else {
        toast.error("Todos os registros já foram importados ou deram erro.");
      }
      invalidate();
    } catch (error) {
      console.error(error); toast.error("Erro ao ler o arquivo BSOFT."); setImportProgress(null);
    }
  };'''
        
    if padrao_bsoft.search(c):
        c = padrao_bsoft.sub(lambda m: nova_funcao_bsoft, c)
        print("✅ Frontend: BSOFT atualizado e protegido contra duplicidade.")

    # 3. Atualizar EDENRED (Tratamento de Erro)
    padrao_ed = re.compile(r'const handleImportEdenred = async[\s\S]*?\n  \};', re.DOTALL)
    if padrao_ed.search(c):
        ed_func = padrao_ed.search(c).group(0)
        if "err.message && err.message.includes(\"409\")" not in ed_func:
            ed_func_novo = ed_func.replace(
                '''} catch (err: any) { 
          erros.push({ linha: i + 1, placa: payload.placa, erro: err.message || "Erro" }); 
        }''',
                '''} catch (err: any) { 
          if (err.message && err.message.includes("409")) {
            erros.push({ linha: i + 1, placa: payload.placa, erro: "Já importado (duplicado)" });
          } else {
            erros.push({ linha: i + 1, placa: payload.placa, erro: err.message || "Erro" }); 
          }
        }'''
            )
            ed_func_novo = ed_func_novo.replace(
                'if (erros.length === 0) toast.success(`${importados} Edenred importados!`);',
                '''if (erros.length === 0) {
        toast.success(`${importados} Edenred importados!`);
      } else if (importados > 0) {
        toast.warning(`${importados} importados, mas ${erros.length} deram erro ou já existiam.`);
      } else {
        toast.error("Todos os registros já foram importados ou deram erro.");
      }'''
            )
            c = c.replace(ed_func, ed_func_novo)
            print("✅ Frontend: Edenred atualizado e protegido contra duplicidade.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)