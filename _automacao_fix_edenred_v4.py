import os
import re

def fix_backend(raiz):
    # 1. Garantir que o Código de Transação e Fornecedor/CNPJ sejam salvos no Backend
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

    caminho_router = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho_router, 'r', encoding='utf-8') as f:
        c = f.read()
    if '"codigo_transacao": body.get("codigo_transacao")' not in c:
        c = c.replace(
            '"chave_nfe": body.get("chave_nfe"),',
            '"chave_nfe": body.get("chave_nfe"),\n        "codigo_transacao": body.get("codigo_transacao"),\n        "cnpj": body.get("cnpj"),\n        "fornecedor": body.get("fornecedor"),\n        "cidade": body.get("cidade"),\n        "estado": body.get("estado"),'
        )
        with open(caminho_router, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Router atualizado para salvar campos do fornecedor e código de transação.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Travar o formulário se for importado (PDF ou Excel)
    # Atualiza os readOnly e disabled para incluir 'excel' e 'pdf'
    c = c.replace('readOnly={form.origem === "pdf"}', 'readOnly={form.origem === "pdf" || form.origem === "excel"}')
    c = c.replace('className={form.origem === "pdf" ? "text-purple-400 border-purple-800 bg-purple-950/20" : ""}', 'className={(form.origem === "pdf" || form.origem === "excel") ? "text-purple-400 border-purple-800 bg-purple-950/20" : ""}')
    c = c.replace('disabled={form.origem === "pdf"}', 'disabled={form.origem === "pdf" || form.origem === "excel"}')
    
    # Travar botão de salvar se for edição de importado
    c = c.replace(
        '<Button type="submit" disabled={salvar.isPending || !form.veiculo_id}>',
        '<Button type="submit" disabled={salvar.isPending || !form.veiculo_id || (editingId && (form.origem === "pdf" || form.origem === "excel"))}>'
    )

    # 2. Adicionar o campo Código de Transação no Form
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

    # 3. Corrigir o botão de Visualizar (Olho) para não permitir salvar
    old_eye = '''<Button size="icon-sm" variant="ghost" onClick={() => { 
      setForm({ 
        ...vazio(hoje), 
        ...r, 
        litros: String(r.litros || ""), 
        preco_litro: String(r.preco_litro || ""), 
        km: String(r.km || ""), 
        origem: r.origem 
      }); 
      setOpen(true); 
      setEditingId(r.id); 
    }}><Eye className="size-4 text-emerald-400" /></Button>'''
    new_eye = '''<Button size="icon-sm" variant="ghost" onClick={() => { 
      setForm({ 
        ...vazio(hoje), 
        ...r, 
        litros: String(r.litros || ""), 
        preco_litro: String(r.preco_litro || ""), 
        km: String(r.km || ""), 
        origem: r.origem,
        fornecedor: r.fornecedor || "",
        cnpj: r.cnpj || "",
        cidade: r.cidade || "",
        estado: r.estado || "",
        codigo_transacao: r.codigo_transacao || ""
      }); 
      setOpen(true); 
      setEditingId(r.id); 
    }}><Eye className="size-4 text-emerald-400" /></Button>'''
    c = c.replace(old_eye, new_eye)

    # 4. Atualizar a importação Edenred para VALIDAR FORNECEDOR e salvar tudo
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

      const parseNum = (val: any) => {
        if (!val) return 0;
        let str = String(val).replace(/[^\\d.,-]/g, "");
        if (str.includes('.') && str.includes(',')) str = str.replace(/\\./g, '').replace(',', '.');
        else if (str.includes(',')) str = str.replace(',', '.');
        return Number(str) || 0;
      };

      for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAL")) continue;

        const dataStr = String(row[idxData]).trim();
        const dataFinal = dataStr.split(" ")[0];
        const horaFinal = dataStr.includes(" ") ? dataStr.split(" ")[1].substring(0, 5) : null;

        const kmNum = Number(String(row[idxKm] || "0").replace(/[^\\d]/g, ""));
        
        const litrosNum = parseNum(row[idxLitros]);
        const precoNum = parseNum(row[idxPreco]);
        const valorNum = idxValor !== -1 ? parseNum(row[idxValor]) : (litrosNum * precoNum);
        
        const kmRodadosNum = idxKmRodados !== -1 ? parseNum(row[idxKmRodados]) : null;
        const mediaNum = idxMedia !== -1 ? parseNum(row[idxMedia]) : null;

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
          await new Promise(resolve => setTimeout(resolve, 200));
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

    # 5. Corrigir a soma dos Cards para pegar o valor certo
    # Removemos qualquer replace() que transforme o número em NaN e garantimos que some como Float
    c = c.replace(
        'const valor = rowsOrdenadas.reduce((s, r) => s + r.valor_total, 0);',
        'const valor = rowsOrdenadas.reduce((s, r) => s + (parseFloat(r.valor_total as any) || 0), 0);'
    )
    c = c.replace(
        'const litros = rowsOrdenadas.reduce((s, r) => s + r.litros, 0);',
        'const litros = rowsOrdenadas.reduce((s, r) => s + (parseFloat(r.litros as any) || 0), 0);'
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Importação Edenred blindada, visualização travada e formatação dos cards ajustada.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)