import os
import re

def fix_backend(raiz):
    # 1. Adicionar o campo codigo_transacao no Modelo
    caminho_model = os.path.join(raiz, "app", "backend", "models", "abastecimentos.py")
    with open(caminho_model, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'codigo_transacao' not in c:
        c = c.replace(
            'chave_nfe: str | None = None',
            'chave_nfe: str | None = None\n    codigo_transacao: str | None = None'
        )
        with open(caminho_model, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Modelo atualizado com 'codigo_transacao'.")

    # 2. Adicionar o campo codigo_transacao no Router de Importação e Criação
    caminho_router = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho_router, 'r', encoding='utf-8') as f:
        c = f.read()
    if '"codigo_transacao": body.get("codigo_transacao")' not in c:
        c = c.replace(
            '"chave_nfe": body.get("chave_nfe"),',
            '"chave_nfe": body.get("chave_nfe"),\n        "codigo_transacao": body.get("codigo_transacao"),'
        )
        with open(caminho_router, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Router atualizado para salvar 'codigo_transacao'.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Atualizar o estado vazio para incluir codigo_transacao
    if 'codigo_transacao' not in c:
        c = c.replace(
            'chave_nfe: "", hora: "", cnpj: "",',
            'chave_nfe: "", codigo_transacao: "", hora: "", cnpj: "",'
        )

    # 2. Bloquear edição no Grid (Excel)
    old_action = '''<Button size="icon-sm" variant="ghost" onClick={() => r.origem === "pdf" ? toast.error("Proibido editar arquivo de nota fiscal importada via PDF.") : abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>'''
    new_action = '''<Button size="icon-sm" variant="ghost" onClick={() => {
      if (r.origem === "pdf") toast.error("Proibido editar arquivo de nota fiscal importada via PDF.");
      else if (r.origem === "excel") toast.error("Proibido editar arquivo importado via Excel (Edenred/BSOFT).");
      else abrirEdicao(r);
    }}><Pencil className="size-4 text-sky-400" /></Button>'''
    c = c.replace(old_action, new_action)

    # 3. Adicionar a trava visual (roxo) nos campos quando origem === "excel"
    # Vou substituir os inputs para incluírem a condição (form.origem === "pdf" || form.origem === "excel")
    c = c.replace('readOnly={form.origem === "pdf"}', 'readOnly={form.origem === "pdf" || form.origem === "excel"}')
    c = c.replace('className={form.origem === "pdf" ? "text-purple-400 border-purple-800 bg-purple-950/20" : ""}', 'className={(form.origem === "pdf" || form.origem === "excel") ? "text-purple-400 border-purple-800 bg-purple-950/20" : ""}')
    c = c.replace('disabled={form.origem === "pdf"}', 'disabled={form.origem === "pdf" || form.origem === "excel"}')
    
    # 4. Adicionar o campo Código de Transação no Form
    if 'Código de Transação' not in c:
        c = c.replace(
            '<div className="grid gap-1.5 overflow-hidden">\n              <Label>Nº NF</Label>',
            '''<div className="grid gap-1.5 overflow-hidden">
              <Label>Código de Transação</Label>
              <Input value={form.codigo_transacao || ""} onChange={(e) => setForm(s => ({ ...s, codigo_transacao: e.target.value }))} readOnly={form.origem === "pdf" || form.origem === "excel"} className={(form.origem === "pdf" || form.origem === "excel") ? "text-purple-400 border-purple-800 bg-purple-950/20" : ""} />
            </div>

            <div className="grid gap-1.5 overflow-hidden">
              <Label>Nº NF</Label>'''
        )

    # 5. Atualizar a função handleImportEdenred para checar fornecedor e preencher tudo
    padrao_edenred = re.compile(r'const handleImportEdenred = async[\s\S]*?\n  \};', re.DOTALL)
    
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
      const findIdx = (name: string) => headerRow.findIndex(h => h.includes(name));

      const idxCod = findIdx("CODIGO TRANSACAO");
      const idxData = findIdx("DATA TRANSACAO");
      const idxPlaca = findIdx("PLACA");
      const idxMotorista = findIdx("NOME MOTORISTA");
      const idxProduto = findIdx("TIPO COMBUSTIVEL");
      const idxLitros = findIdx("LITROS");
      const idxPreco = findIdx("VL/LITRO");
      const idxKm = findIdx("HODOMETRO");
      const idxKmRodados = findIdx("KM RODADOS");
      const idxMedia = findIdx("KM/LITRO");
      const idxPosto = findIdx("NOME ESTABELECIMENTO");
      const idxValor = findIdx("VALOR EMISSAO");
      const idxCnpj = findIdx("CNPJ");
      const idxCidade = findIdx("CIDADE");
      const idxEstado = findIdx("UF");

      const totalLinhas = rows.length - 1;
      setImportProgress({ total: totalLinhas, current: 0, errors: [] });
      let importados = 0; const erros: any[] = [];

      for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAL")) continue;

        const dataStr = String(row[idxData]).trim();
        const dataFinal = dataStr.split(" ")[0];
        const horaFinal = dataStr.includes(" ") ? dataStr.split(" ")[1].substring(0, 5) : null;

        const kmNum = Number(String(row[idxKm] || "0").replace(/[^\\d]/g, ""));
        
        const litrosNum = Number(String(row[idxLitros] || "0").replace(",", "."));
        const precoNum = Number(String(row[idxPreco] || "0").replace(",", "."));
        const valorNum = idxValor !== -1 ? Number(String(row[idxValor] || "0").replace(",", ".")) : (litrosNum * precoNum);
        
        const kmRodadosNum = idxKmRodados !== -1 ? Number(String(row[idxKmRodados] || "0").replace(",", ".")) : null;
        const mediaNum = idxMedia !== -1 ? Number(String(row[idxMedia] || "0").replace(",", ".")) : null;

        const motoristaNome = idxMotorista !== -1 ? String(row[idxMotorista] || "").trim() : "";
        let motoristaId = NENHUM;
        if (motoristaNome && motoristas.data) {
          const mot = motoristas.data.find((m: any) => m.nome.toUpperCase() === motoristaNome.toUpperCase());
          if (mot) motoristaId = mot.id;
        }

        let cnpjRaw = idxCnpj !== -1 ? String(row[idxCnpj] || "").replace(/\\D/g, "") : "";
        let cnpjFormatado = cnpjRaw.length === 14 ? formatCnpj(cnpjRaw) : "";

        const fornecedorNome = String(row[idxPosto] || "").trim();
        const cidade = idxCidade !== -1 ? String(row[idxCidade] || "").trim() : "";
        const estado = idxEstado !== -1 ? String(row[idxEstado] || "").trim() : "";

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
        } catch (err: any) { 
          erros.push({ linha: i + 1, placa: payload.placa, erro: err.message || "Erro" }); 
        }
        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }

      setImportProgress(prev => prev ? { ...prev, current: totalLinhas, errors: erros } : null);
      if (erros.length === 0) toast.success(`${importados} Edenred importados!`);
      invalidate();
    } catch (error) {
      console.error(error); toast.error("Erro ao ler Edenred."); setImportProgress(null);
    }
  };'''

    if padrao_edenred.search(c):
        c = padrao_edenred.sub(lambda m: nova_funcao, c)
        print("✅ Frontend: Função handleImportEdenred reescrita.")
    else:
        print("⚠️ Não foi possível encontrar handleImportEdenred.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)