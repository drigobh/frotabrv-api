import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PDF_DATA_{agora}.zip")
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

    # Substitui a função importar_pdf inteira por uma versão à prova de falhas
    padrao = re.compile(r'@router\.post\("/importar"[\s\S]*?(?=@router\.|$)', re.DOTALL)
    
    nova_funcao = '''@router.post("/importar", response_model=None, status_code=201)
async def importar_pdf(body: dict, request: Request, user: dict = Depends(require("write"))):
    def safe_float(val):
        if val is None: return 0.0
        if isinstance(val, (int, float)): return float(val)
        try: return float(str(val).replace(',', '.'))
        except: return 0.0

    try:
        placa_limpa = body.get("placa", "").strip().upper()
        veiculo = await db.veiculos.find_one({"placa": placa_limpa}, {"_id": 0})
        if not veiculo:
            raise HTTPException(status_code=404, detail=f"Veículo com placa {placa_limpa} não encontrado.")

        litros = safe_float(body.get("litros"))
        preco_litro = safe_float(body.get("preco_litro"))
        km_atual = safe_float(body.get("km"))
        valor_total = safe_float(body.get("valor_total"))
        data_recebida = body.get("data")

        try:
            if data_recebida and "/" in data_recebida:
                data_abast = datetime.strptime(data_recebida, "%d/%m/%Y").strftime("%Y-%m-%d")
            else:
                data_abast = data_recebida
        except:
            data_abast = data_recebida

        # TRAVA DE DUPLICIDADE
        codigo_transacao_recebido = body.get("codigo_transacao")
        chave_nfe_recebida = body.get("chave_nfe")
        numero_nf_recebido = body.get("numero_nf")
        cnpj_recebido = body.get("cnpj")

        if codigo_transacao_recebido:
            if await db.abastecimentos.find_one({"codigo_transacao": codigo_transacao_recebido}):
                raise HTTPException(409, "Registro duplicado: Código de Transação já importado.")
        elif chave_nfe_recebida:
            if await db.abastecimentos.find_one({"chave_nfe": chave_nfe_recebida}):
                raise HTTPException(409, "Registro duplicado: Chave NF-e já importada.")
        elif numero_nf_recebido and cnpj_recebido:
            if await db.abastecimentos.find_one({"numero_nf": numero_nf_recebido, "cnpj": cnpj_recebido}):
                raise HTTPException(409, "Registro duplicado: Nota Fiscal já importada.")
        else:
            existente_placa = await db.abastecimentos.find_one({
                "veiculo_id": veiculo["id"],
                "data": data_abast,
                "litros": litros
            })
            if existente_placa:
                raise HTTPException(409, "Registro duplicado: Abastecimento com esta placa, data e litros já existe.")

        if valor_total == 0:
            valor_total = litros * preco_litro
        valor_total = round(valor_total, 2)

        ultimo = await db.abastecimentos.find_one(
            {"veiculo_id": veiculo["id"], "data": {"$lt": data_abast}},
            {"_id": 0},
            sort=[("data", -1)]
        )

        if body.get("origem") == "excel" and body.get("km_rodados") is not None:
            km_rodados = safe_float(body.get("km_rodados"))
            media_km_l = safe_float(body.get("media_km_l"))
        else:
            km_rodados, media_km_l = calcular_km(km_atual, litros, body.get("produto", "DIESEL").upper(), ultimo, veiculo)

        acoplamento = await db.acoplamentos.find_one(
            {"veiculo_id": veiculo["id"]},
            {"_id": 0},
            sort=[("created_at", -1)]
        )
            
        motorista_id = acoplamento.get("motorista_id") if acoplamento else None
        motorista_label = None
        if motorista_id:
            mot = await db.motoristas.find_one({"id": motorista_id}, {"_id": 0})
            motorista_label = mot["nome"] if mot else None

        doc = {
            "id": str(uuid.uuid4()),
            "data": data_abast,
            "veiculo_id": veiculo["id"],
            "veiculo_label": f"{veiculo['placa']} · {veiculo['modelo']}",
            "motorista_id": motorista_id,
            "motorista_label": motorista_label,
            "litros": litros,
            "preco_litro": preco_litro,
            "valor_total": valor_total,
            "posto": body.get("fornecedor") or "Importado",
            "km": km_atual,
            "km_rodados": km_rodados,
            "media_km_l": media_km_l,
            "origem": body.get("origem", "excel"),
            "produto": body.get("produto", "DIESEL").upper(),
            "numero_nf": body.get("numero_nf"),
            "chave_nfe": body.get("chave_nfe"),
            "codigo_transacao": body.get("codigo_transacao"),
            "hora": body.get("hora"),
            "cnpj": body.get("cnpj"),
            "cidade": body.get("cidade"),
            "estado": body.get("estado"),
            "fornecedor": body.get("fornecedor"),
            "created_by": user.get("id", "sistema"),
            "created_by_name": user.get("nome", user.get("email", "Sistema")),
            "created_at": now_iso()
        }

        await db.abastecimentos.insert_one(doc)
        if km_atual > 0:
            await db.veiculos.update_one({"id": veiculo["id"]}, {"$set": {"hodometro_km": km_atual}})
        doc.pop("_id", None)
        return doc
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERRO NA IMPORTACAO: {e}")
        raise HTTPException(500, f"Erro interno ao importar: {str(e)}")
'''
    
    if padrao.search(c):
        c = padrao.sub(lambda m: nova_funcao, c)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Função /importar restaurada e blindada contra falhas.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Substitui a função handleImportXLS inteira para garantir a conversão correta de data
    padrao_bsoft = re.compile(r'const handleImportXLS = async[\s\S]*?\n  \};', re.DOTALL)
    
    nova_funcao = '''const handleImportXLS = async (e: React.ChangeEvent<HTMLInputElement>) => {
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
        
        // CONVERSÃO INTELIGENTE DE DATA (M/D/YY -> YYYY-MM-DD)
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
          erros.push({ linha: i + 1, placa: placa, erro: err.message && err.message.includes("409") ? "Já importado" : (err.message || "Erro") }); 
        }
        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }

      setImportProgress(prev => prev ? { ...prev, current: totalLinhas, errors: erros } : null);
      if (erros.length === 0) {
        toast.success(`${importados} registros BSOFT importados!`);
      } else if (importados > 0) {
        toast.warning(`${importados} importados, mas ${erros.length} já existiam.`);
      } else {
        toast.error("Todos os registros já foram importados.");
      }
      invalidate();
    } catch (error) {
      console.error(error); toast.error("Erro ao ler o arquivo BSOFT."); setImportProgress(null);
    }
  };'''

    if padrao_bsoft.search(c):
        c = padrao_bsoft.sub(lambda m: nova_funcao, c)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Frontend: BSOFT atualizado com conversão correta de data e bloqueio.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)