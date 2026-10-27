import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_EDENRED_FORN_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for p in ["frontend/src/pages/Abastecimentos.tsx", "app/backend/routers/fornecedores.py"]:
            caminho_abs = os.path.join(raiz, p)
            if os.path.exists(caminho_abs):
                zipf.write(caminho_abs, p)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "fornecedores.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Adiciona a rota de busca reversa por nome e cidade, usando OpenCNPJ
    if 'consultar-cnpj-por-nome' not in c:
        rota = '''
import httpx
from urllib.parse import quote

@router.get("/consultar-cnpj-por-nome")
async def consultar_cnpj_por_nome(nome: str, cidade: str = None, _u: dict = Depends(require("read"))):
    if not nome:
        raise HTTPException(400, "Nome do estabelecimento é obrigatório.")
    
    # Monta a URL de busca do OpenCNPJ
    # A API aceita filtros por nome e município.
    query = f"https://api.opencnpj.org/search?query={quote(nome)}"
    if cidade:
        query += f"&city={quote(cidade)}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(query)
            if response.status_code == 200:
                data = response.json()
                # A resposta pode vir como lista ou objeto com 'results'
                if isinstance(data, list) and len(data) > 0:
                    return data[0]  # Retorna o primeiro resultado
                elif isinstance(data, dict) and 'results' in data and len(data['results']) > 0:
                    return data['results'][0]
            # Se não encontrar no OpenCNPJ, tenta fallback com BrasilAPI (se tiver CNPJ)
            # Mas como não temos CNPJ, não há fallback direto.
    except Exception as e:
        print(f"Erro na busca reversa: {e}")
    
    raise HTTPException(404, "CNPJ não encontrado para este estabelecimento.")
'''
        c += rota
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota de busca reversa por nome/cidade adicionada.")
    else:
        print("ℹ️ Backend: Rota de busca reversa já existe.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Substitui a função handleImportEdenred inteira para incluir a validação de fornecedor
    padrao = re.compile(r'const handleImportEdenred = async[\s\S]*?\n  \};', re.DOTALL)
    
    nova_funcao = '''const handleImportEdenred = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: "array" });
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const rows = XLSX.utils.sheet_to_json<any[]>(sheet, { header: 1, raw: false });

      if (rows.length < 2) { toast.error("Planilha vazia."); return; }

      const headerRow = rows[0].map((c: any) => String(c).toUpperCase().trim());
      const findIdx = (name: string) => headerRow.findIndex(h => h.replace(/\\s+/g, '').includes(name.replace(/\\s+/g, '')));

      const idxCod = findIdx("CODIGO TRANSACAO");
      const idxData = findIdx("DATA TRANSACAO");
      const idxPlaca = findIdx("PLACA");
      const idxMotorista = findIdx("NOME MOTORISTA");
      const idxProduto = findIdx("TIPO COMBUSTIVEL");
      const idxLitros = findIdx("LITROS");
      const idxPreco = findIdx("VL/LITRO") !== -1 ? findIdx("VL/LITRO") : findIdx("V. LITRO");
      const idxKm = findIdx("HODOMETRO");
      const idxKmRodados = findIdx("KM RODADOS");
      const idxMedia = findIdx("KM/LITRO");
      const idxPosto = findIdx("NOME ESTABELECIMENTO");
      const idxValor = findIdx("VALOR EMISSAO");
      const idxCidade = findIdx("CIDADE");
      const idxEstado = findIdx("UF");

      const totalLinhas = rows.length - 1;
      setImportProgress({ total: totalLinhas, current: 0, errors: [] });
      let importados = 0; const erros: any[] = [];

      const parseNum = (val: any) => {
        if (val === undefined || val === null || val === "") return 0;
        if (typeof val === 'number') return val;
        let str = String(val).replace(/[^0-9.,-]/g, "");
        if (str.includes('.') && str.includes(',')) {
            if (str.lastIndexOf(',') > str.lastIndexOf('.')) str = str.replace(/\\./g, '').replace(',', '.');
            else str = str.replace(/,/g, '');
        } else if (str.includes(',')) {
            str = str.replace(',', '.');
        }
        return Number(str) || 0;
      };

      for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAL")) continue;

        const dataStr = String(row[idxData]).trim();
        const dataFinal = dataStr.split(" ")[0];
        const horaFinal = dataStr.includes(" ") ? dataStr.split(" ")[1].substring(0, 5) : null;

        const kmNum = parseNum(row[idxKm]);
        const litrosNum = parseNum(row[idxLitros]);
        const precoNum = parseNum(row[idxPreco]);
        const valorNum = idxValor !== -1 ? parseNum(row[idxValor]) : (litrosNum * precoNum);
        const kmRodadosNum = idxKmRodados !== -1 ? parseNum(row[idxKmRodados]) : null;
        const mediaNum = idxMedia !== -1 ? parseNum(row[idxMedia]) : null;

        const motoristaNome = idxMotorista !== -1 ? String(row[idxMotorista] || "").trim() : "";
        let motoristaId = NENHUM;
        if (motoristaNome && motoristas.data) {
          const mot = motoristas.data.find((m: any) => m.nome.toUpperCase() === motoristaNome.toUpperCase() || m.nome.toUpperCase().includes(motoristaNome));
          if (mot) motoristaId = mot.id;
        }

        const fornecedorNome = String(row[idxPosto] || "").trim();
        const cidade = idxCidade !== -1 ? String(row[idxCidade] || "").trim() : "";
        const estado = idxEstado !== -1 ? String(row[idxEstado] || "").trim() : "";

        let cnpjFormatado = "";
        let fornecedorExiste = false;

        // 1. Verifica se o fornecedor já existe no banco local
        const existingForn = fornecedores.find((f: any) => f.nome.toLowerCase() === fornecedorNome.toLowerCase());
        if (existingForn) {
          cnpjFormatado = existingForn.documento || "";
          fornecedorExiste = true;
        } else {
          // 2. Se não existe, tenta buscar o CNPJ via API (OpenCNPJ)
          try {
            const data = await apiGet<any>(`/fornecedores/consultar-cnpj-por-nome?nome=${encodeURIComponent(fornecedorNome)}&cidade=${encodeURIComponent(cidade)}`);
            if (data && data.cnpj) {
              cnpjFormatado = formatCnpj(data.cnpj);
              // Se encontrou, pergunta se quer cadastrar
              const confirm = window.confirm(`Fornecedor "${fornecedorNome}" não cadastrado. Deseja cadastrá-lo agora com os dados encontrados?`);
              if (confirm) {
                await apiPost("/fornecedores", {
                  nome: data.razao_social || fornecedorNome,
                  documento: cnpjFormatado,
                  endereco: data.logradouro || "",
                  bairro: data.bairro || "",
                  cidade: data.municipio || cidade,
                  estado: data.uf || estado,
                  ativo: true
                });
                await refetchFornecedores();
                fornecedorExiste = true;
                toast.success(`Fornecedor ${fornecedorNome} cadastrado!`);
              }
            }
          } catch (err) {
            // Se não encontrar, não faz nada (segue o fluxo)
          }
        }

        const payload = {
          data: dataFinal,
          placa: String(row[idxPlaca] || "").toUpperCase().trim(),
          km: kmNum,
          motorista_id: motoristaId,
          fornecedor: fornecedorNome,
          cnpj: cnpjFormatado,
          cidade: cidade,
          estado: estado,
          litros: litrosNum,
          preco_litro: precoNum,
          valor_total: valorNum,
          km_rodados: kmRodadosNum,
          media_km_l: mediaNum,
          produto: String(row[idxProduto] || "DIESEL").toUpperCase(),
          codigo_transacao: String(row[idxCod] || "").trim(),
          hora: horaFinal, numero_nf: null, chave_nfe: null, origem: "excel"
        };

        try { 
          await apiPost("/abastecimentos/importar", payload); 
          importados++; 
          await new Promise(resolve => setTimeout(resolve, 150));
        } catch (err: any) { 
          erros.push({ linha: i + 1, placa: payload.placa, erro: err.message && err.message.includes("409") ? "Já importado" : (err.message || "Erro") }); 
        }
        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }

      setImportProgress(prev => prev ? { ...prev, current: totalLinhas, errors: erros } : null);
      if (erros.length === 0) toast.success(`${importados} Edenred importados!`);
      else if (importados > 0) toast.warning(`${importados} importados, mas ${erros.length} já existiam.`);
      else toast.error("Todos os registros já foram importados.");
      invalidate();
    } catch (error) {
      console.error(error); toast.error("Erro ao ler Edenred."); setImportProgress(null);
    }
  };'''

    if padrao.search(c):
        c = padrao.sub(lambda m: nova_funcao, c)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Frontend: Função do Edenred atualizada com validação de fornecedor.")
    else:
        print("⚠️ Não foi possível encontrar a função handleImportEdenred.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)