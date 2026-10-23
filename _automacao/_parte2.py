import os

caminho = os.path.join(os.getcwd(), "frontend", "src", "pages", "Abastecimentos.tsx")

conteudo = '''
  // --- IMPORTAR PDF ---
  const handleImportPDF = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      let text = "";

      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const content = await page.getTextContent();
        text += content.items.map((item: any) => item.str).join(" ") + "\\n";
      }

      const placaMatch = text.match(/PLACA[:\\s]*([A-Z]{3}[0-9][A-Z0-9][0-9]{2})/i) || text.match(/PLACA[:\\s]*([A-Z0-9]{7})/i);
      const kmMatch = text.match(/KM[:\\s]*(\\d+)/i);
      const litrosMatch = text.match(/L\\s+([\\d.,]+)\\s+([\\d.,]+)\\s+([\\d.,]+)/i) || text.match(/L\\s+([\\d.,]+)\\s+([\\d.,]+)/i);
      const nfMatch = text.match(/Nº\\s*(\\d+)/);
      const chaveMatch = text.match(/CHAVE DE ACESSO DA NF-E\\s*([\\d\\s]+)/i);
      const cnpjMatch = text.match(/C\\.N\\.P\\.J\\.\\s*([\\d\\.\\/\\-]+)/i);
      const fornecedorMatch = text.match(/RECEBEMOS DE\\s*(.*?)\\s*OS PRODUTOS/i);

      const parseNum = (val: string) => Number(val.replace(/\\./g, "").replace(",", "."));

      const payload = {
        data: new Date().toISOString().split('T')[0],
        hora: null,
        numero_nf: nfMatch ? nfMatch[1] : null,
        chave_nfe: chaveMatch ? chaveMatch[1].replace(/\\s/g, "") : null,
        cnpj: cnpjMatch ? cnpjMatch[1] : null,
        fornecedor: fornecedorMatch ? fornecedorMatch[1].trim() : null,
        placa: placaMatch ? placaMatch[1].toUpperCase() : null,
        litros: litrosMatch ? parseNum(litrosMatch[1]) : 0,
        preco_litro: litrosMatch ? parseNum(litrosMatch[2]) : 0,
        km: kmMatch ? Number(kmMatch[1]) : 0,
      };

      await apiPost("/abastecimentos/importar", payload);
      toast.success("Nota Fiscal importada com sucesso!");
      invalidate();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao importar o PDF.");
    }
  };

  const handleImportXLS = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(text, "text/html");
      const table = doc.querySelector("table");
      
      if (!table) {
        toast.error("Tabela não encontrada no arquivo HTML.");
        return;
      }

      const rows = Array.from(table.querySelectorAll("tr"));
      let headerRow: string[] = [];
      let startRow = -1;

      for (let i = 0; i < rows.length; i++) {
        const cells = Array.from(rows[i].querySelectorAll("td, th")).map(c => c.textContent?.trim() || "");
        const normalized = cells.map(c => c.toLowerCase());
        if (normalized.includes("data") && normalized.includes("placa") && normalized.includes("litros")) {
          headerRow = normalized;
          startRow = i + 1;
          break;
        }
      }

      if (startRow === -1) {
        toast.error("Cabeçalho da planilha não encontrado. Verifique se a planilha tem as colunas 'Data', 'Placa' e 'Litros'.");
        return;
      }

      const colIndex = (name: string) => headerRow.findIndex(h => h === name.toLowerCase());
      
      const idxData = colIndex("data");
      const idxPlaca = colIndex("placa");
      const idxKm = colIndex("leitura");
      const idxPosto = colIndex("posto");
      const idxLitros = colIndex("litros");
      const idxPreco = colIndex("v. litro");

      if (idxData === -1 || idxPlaca === -1 || idxLitros === -1 || idxPreco === -1) {
        toast.error("Colunas essenciais não encontradas (Data, Placa, Litros, V. Litro).");
        return;
      }

      let importados = 0;

      for (let i = startRow; i < rows.length; i++) {
        const cells = Array.from(rows[i].querySelectorAll("td, th")).map(c => c.textContent?.trim() || "");
        if (cells.length === 0 || !cells[idxData] || cells[idxData].toLowerCase().includes("total") || cells[idxData].includes("Bsoft")) continue;

        let dataStr = cells[idxData];
        if (dataStr.includes("/")) {
           const [d, m, y] = dataStr.split("/");
           dataStr = `${y}-${m}-${d}`;
        }

        const placaRaw = cells[idxPlaca] || "";
        const placa = placaRaw.split("/")[0].replace("-", "").toUpperCase();

        const litrosRaw = Number(cells[idxLitros].replace(".", "").replace(",", ".")) / 1000;
        const valorLitroRaw = Number(cells[idxPreco].replace(".", "").replace(",", ".")) / 100;
        
        const payload = {
          data: dataStr,
          placa: placa,
          km: Number(cells[idxKm] || 0),
          fornecedor: cells[idxPosto] || "",
          litros: litrosRaw,
          preco_litro: valorLitroRaw,
          hora: null,
          numero_nf: null,
          chave_nfe: null,
          cnpj: null
        };

        try {
          await apiPost("/abastecimentos/importar", payload);
          importados++;
        } catch (err) {
          console.error(`Erro na linha ${i + 1}:`, err);
        }
      }

      toast.success(`${importados} abastecimentos importados com sucesso!`);
      invalidate();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao ler o arquivo.");
    }
  };

  const salvar = useMutation({
    mutationFn: () => {
      const payload = {
        data: form.data,
        veiculo_id: form.veiculo_id,
        motorista_id: form.motorista_id === NENHUM ? null : form.motorista_id,
        litros: Number(form.litros.replace(",", ".")),
        preco_litro: Number(form.preco_litro.replace(",", ".")),
        posto: form.posto,
        km: Number(form.km),
        observacoes: form.observacoes,
        numero_nf: form.numero_nf || null,
        chave_nfe: form.chave_nfe || null,
        hora: form.hora || null,
        cnpj: form.cnpj || null,
        fornecedor: form.fornecedor || null,
        origem: form.origem,
      };
      if (editingId) return apiPut<Abastecimento>(`/abastecimentos/${editingId}`, payload);
      return apiPost<Abastecimento>("/abastecimentos", payload);
    },
    onSuccess: () => {
      toast.success(editingId ? "Abastecimento atualizado" : "Abastecimento registrado");
      setOpen(false);
      setEditingId(null);
      invalidate();
    },
    onError: (e) => toast.error(errMsg(e)),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete<void>(`/abastecimentos/${id}`),
    onSuccess: () => { toast.success("Abastecimento excluído"); setExcluirId(null); invalidate(); },
    onError: (e) => toast.error(errMsg(e)),
  });

  const total = Number(form.litros.replace(",", ".")) * Number(form.preco_litro.replace(",", "."));
  const set = (k: keyof ReturnType<typeof vazio>) => (v: string) => setForm((s) => ({ ...s, [k]: v }));
  const veicOpts = (veiculos.data ?? []).filter(v => v.ativo).map((v) => ({ value: v.id, label: `${v.placa} · ${v.modelo}` }));

  const abrirNovo = () => {
    setEditingId(null);
    setForm(vazio(hoje));
    setOpen(true);
  };

  const abrirEdicao = (r: Abastecimento) => {
    setEditingId(r.id);
    setForm({
      data: r.data,
      veiculo_id: r.veiculo_id,
      motorista_id: r.motorista_id || NENHUM,
      litros: String(r.litros),
      preco_litro: String(r.preco_litro),
      posto: r.posto,
      km: String(r.km),
      observacoes: r.observacoes || "",
      numero_nf: r.numero_nf || "",
      chave_nfe: r.chave_nfe || "",
      hora: r.hora || "",
      cnpj: r.cnpj || "",
      fornecedor: r.fornecedor || "",
      origem: r.origem || "manual",
    });
    setOpen(true);
  };

  const handleVeiculoChange = async (veiculoId: string) => {
    set("veiculo_id")(veiculoId);
    if (!veiculoId) return;

    try {
      if (!editingId) {
        const kmData = await apiGet<{ ultimo_km: number }>(`/abastecimentos/ultimo-km/${veiculoId}`);
        setForm(s => ({ ...s, km: String(kmData.ultimo_km) }));
      }

      const acoplamentos = await apiGet<any[]>("/acoplamentos");
      const acoplamentoAtivo = acoplamentos.find(a => a.veiculo_id === veiculoId);
      
      if (acoplamentoAtivo && acoplamentoAtivo.motorista_id && !editingId) {
        setForm(s => ({ ...s, motorista_id: acoplamentoAtivo.motorista_id }));
      }
    } catch (error) {
      console.error("Erro ao buscar dados:", error);
    }
  };

  const cards = [
    { label: "Abastecimentos", valor: resumo.total, icon: List, color: "#38bdf8", sub: "registros no período" },
    { label: "Total Abastecido", valor: `${num(resumo.litros, 1)} L`, icon: Droplets, color: "#2dd4bf", sub: "volume total" },
    { label: "Valor Total", valor: brl(resumo.valor), icon: DollarSign, color: "#fbbf24", sub: "custo total" },
    { label: "Média Geral", valor: `${num(resumo.media, 2)} km/L`, icon: TrendingUp, color: "#a78bfa", sub: "eficiência da frota" },
    { label: "Preço Médio", valor: `${brl(resumo.preco)}/L`, icon: Target, color: "#f87171", sub: "por litro" },
    { label: "Maior Abastecimento", valor: resumo.maior ? brl(resumo.maior.valor_total) : "—", icon: ArrowUpRight, color: "#4ade80", sub: resumo.maior?.veiculo_label.split(" · ")[0] },
    { label: "Menor Abastecimento", valor: resumo.menor ? brl(resumo.menor.valor_total) : "—", icon: ArrowDownRight, color: "#f87171", sub: resumo.menor?.motorista_label || resumo.menor?.veiculo_label.split(" · ")[0] },
    { label: "Média por Abast.", valor: brl(resumo.mediaValor), icon: DollarSign, color: "#fb923c", sub: "R$ por registro" },
    { label: "Média de KM", valor: `${num(resumo.mediaKm, 0)} km`, icon: TrendingUp, color: "#60a5fa", sub: "por abastecimento" },
    { label: "Custo por KM", valor: brl(resumo.custoPorKm), icon: DollarSign, color: "#34d399", sub: "combustível por km" },
  ];
'''

with open(caminho, 'a', encoding='utf-8') as f:
    f.write(conteudo)

print("Parte 2 concluida com sucesso!")