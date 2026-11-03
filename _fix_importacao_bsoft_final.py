import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_IMPORT_BSOFT_FINAL_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/models/pneus.py",
        "app/backend/routers/pneus.py",
        "frontend/src/pages/Pneus.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend_model(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "pneus.py")
    codigo = '''from pydantic import BaseModel
from typing import Optional

class PneuCreate(BaseModel):
    numero_fogo: str
    marca: str
    modelo: Optional[str] = None
    medida: str
    dot: Optional[str] = None
    tipo: str = "Tração"
    status: str = "Estoque"
    custo_aquisicao: float = 0.0
    observacoes: Optional[str] = None
    foto_url: Optional[str] = None
    
    equipamento: Optional[str] = None
    posicao: Optional[str] = None
    banda_rod: Optional[str] = None
    estrutura: Optional[str] = None
    n_serie: Optional[str] = None
    n_recap: Optional[str] = None
    data_compra: Optional[str] = None
    data_descarte: Optional[str] = None
    custo_total_atual: Optional[float] = None
    profundidade_atual: Optional[float] = None
    uso_atual: Optional[str] = None
    custo_por_km: Optional[float] = None
    km_posicao: Optional[float] = None
    
    veiculo_id: Optional[str] = None
    carreta_id: Optional[str] = None

class Pneu(PneuCreate):
    id: str
    created_at: str
    created_by: str
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Backend: Model PneuCreate atualizado com todos os campos.")

def fix_backend_router(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "pneus.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Substituir o bloco de importação para incluir todos os campos
    if '"equipamento": item.get("equipamento"' not in c:
        # Procura o doc = { ... } dentro da função importar_pneus e substitui
        padrao = re.compile(r'doc = \{[\s\S]*?"created_by": user\["nome"\],\s*\}', re.MULTILINE)
        novo_doc = '''doc = {
                "id": str(uuid.uuid4()),
                "numero_fogo": item.get("numero_fogo"),
                "marca": item.get("marca"),
                "modelo": item.get("modelo", ""),
                "medida": item.get("medida", ""),
                "dot": item.get("dot", ""),
                "tipo": item.get("tipo", "Tração"),
                "status": item.get("status", "Estoque"),
                "custo_aquisicao": float(item.get("custo_aquisicao", 0)),
                "observacoes": item.get("observacoes", ""),
                "equipamento": item.get("equipamento", ""),
                "posicao": item.get("posicao", ""),
                "banda_rod": item.get("banda_rod", ""),
                "estrutura": item.get("estrutura", ""),
                "n_serie": item.get("n_serie", ""),
                "n_recap": item.get("n_recap", ""),
                "data_compra": item.get("data_compra", ""),
                "data_descarte": item.get("data_descarte", ""),
                "custo_total_atual": float(item.get("custo_total_atual", 0)),
                "profundidade_atual": float(item.get("profundidade_atual", 0)),
                "uso_atual": item.get("uso_atual", ""),
                "custo_por_km": float(item.get("custo_por_km", 0)),
                "km_posicao": float(item.get("km_posicao", 0)),
                "created_at": now_iso(),
                "created_by": user["nome"],
            }'''
        
        if padrao.search(c):
            c = padrao.sub(novo_doc, c)
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Backend: Rota /importar atualizada para salvar todos os campos.")
        else:
            print("⚠️ Não foi possível encontrar o bloco doc = {} na função importar_pneus.")

def fix_frontend_mapeamento(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Substituir a função handleImportFile
    novo_mapeamento = '''
  const getValor = (row: any, ...chaves: string[]) => {
    for (const chave of chaves) {
      const valor = row[chave];
      if (valor !== undefined && valor !== null && String(valor).trim() !== "") {
        return String(valor).trim();
      }
    }
    return "";
  };

  const handleImportFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (evt) => {
      try {
        const bstr = evt.target?.result;
        const wb = XLSX.read(bstr, { type: 'binary' });
        const wsname = wb.SheetNames[0];
        const ws = wb.Sheets[wsname];
        const data: any[] = XLSX.utils.sheet_to_json(ws, { defval: "" });
        
        if (data.length === 0) {
          toast.error("A planilha está vazia.");
          return;
        }

        console.log("Colunas encontradas na planilha:", Object.keys(data[0]));

        const payload = data.map((row: any) => {
          const numero_fogo = getValor(row, "Marca Fogo", "MarcaFogo", "Nº Fogo", "N.º Fogo", "Fogo");
          const marca = getValor(row, "Marca", "MARCA");
          const modelo = getValor(row, "Modelo", "MODELO");
          const medida = getValor(row, "Tamanho", "Medida", "TAMANHO", "MEDIDA").replace(",", ".").replace(" ", "/");
          
          if (!numero_fogo || !marca) return null;

          const data_descarte = getValor(row, "Data Descarte", "DataDescarte", "Descarte");
          const equipamento = getValor(row, "Equipamento", "EQUIPAMENTO", "Equip.", "Placa");
          
          let status = "Estoque";
          if (data_descarte) status = "Sucateado";
          else if (equipamento) status = "Aplicado";

          const tipo_raw = getValor(row, "Tipo", "TIPO").toUpperCase();
          let tipo = "Misto";
          if (tipo_raw === "LISO" || tipo_raw === "BORRACHUDO") tipo = "Misto";
          else if (tipo_raw === "DIRECIONAL") tipo = "Direcional";
          else if (tipo_raw === "TRACAO" || tipo_raw === "TRAÇÃO") tipo = "Tração";
          else if (tipo_raw === "BANDA") tipo = "Banda";

          return {
            numero_fogo,
            marca,
            modelo,
            medida,
            dot: getValor(row, "DOT", "Dot"),
            tipo,
            status,
            custo_aquisicao: Number(getValor(row, "Custo Total Atual", "CustoTotalAtual", "Custo", "Custo Aquisição").replace(".", "").replace(",", ".")) || 0,
            equipamento,
            posicao: getValor(row, "Posição", "Posicao", "POSIÇÃO", "Posição Pneu"),
            banda_rod: getValor(row, "Banda Rod.", "BandaRod", "Banda", "BANDA ROD."),
            estrutura: getValor(row, "Estrutura", "ESTRUTURA"),
            n_serie: getValor(row, "N.º Série", "NSerie", "N Serie", "Número de Série", "Serie"),
            n_recap: getValor(row, "N.º Recap.", "NRecap", "N Recap", "Recapagem", "Recap"),
            data_compra: getValor(row, "Data Compra", "DataCompra", "Compra"),
            data_descarte,
            custo_total_atual: Number(getValor(row, "Custo Total Atual", "CustoTotalAtual").replace(".", "").replace(",", ".")) || 0,
            profundidade_atual: Number(getValor(row, "Profundidade Atual", "ProfundidadeAtual", "Profundidade").replace(",", ".")) || 0,
            uso_atual: getValor(row, "Uso Atual", "UsoAtual", "Uso", "KM na Posição", "KM"),
            custo_por_km: Number(getValor(row, "Custo por KM", "CustoPorKM", "Custo KM", "CPK").replace(",", ".")) || 0,
            km_posicao: Number(getValor(row, "KM na Posição", "KMnaPosicao", "KM Posição", "KM").replace(".", "").replace(",", ".")) || 0,
          };
        }).filter((p): p is any => p !== null);

        if (payload.length === 0) {
          toast.error("Nenhum pneu válido encontrado. Verifique os nomes das colunas.");
          return;
        }

        console.log("Payload de importação (primeiro item):", payload[0]);

        setImportOpen(true);
        setImportTotal(payload.length);
        setImportProcessados(0);
        setImportProgresso(0);
        setImportErros([]);
        setImportando(true);

        let processados = 0;
        const interval = setInterval(() => {
          processados += Math.ceil(payload.length / 20);
          if (processados >= payload.length) {
            processados = payload.length;
            clearInterval(interval);
          }
          setImportProcessados(processados);
          setImportProgresso(Math.round((processados / payload.length) * 100));
        }, 200);

        const res = await apiPost<any>("/pneus/importar", payload);
        clearInterval(interval);
        
        setImportProcessados(payload.length);
        setImportProgresso(100);
        setImportando(false);
        
        if (res.erros?.length > 0) {
          setImportErros(res.erros);
        }

        qc.invalidateQueries({ queryKey: ["pneus"] });
        qc.invalidateQueries({ queryKey: ["pneus-dashboard"] });
      } catch (err) {
        console.error(err);
        setImportando(false);
        toast.error("Erro ao ler a planilha. Verifique se o arquivo é um Excel válido.");
      }
    };
    reader.readAsBinaryString(file);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };
'''
    
    # Encontra o trecho da função atual e substitui
    padrao = re.compile(r'  // ==========================================\s*\n  // IMPORTAÇÃO DE PLANILHA BSOFT[\s\S]*?if \(fileInputRef\.current\) fileInputRef\.current\.value = "";\s*\n  \};', re.MULTILINE)
    if padrao.search(c):
        c = padrao.sub(novo_mapeamento.strip(), c)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Frontend: Mapeamento da planilha atualizado.")
    else:
        print("⚠️ Não foi possível encontrar a função handleImportFile para substituir.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend_model(raiz)
    fix_backend_router(raiz)
    fix_frontend_mapeamento(raiz)
    print("\n✅ Script aplicado com sucesso! Faça o push para o Render.")