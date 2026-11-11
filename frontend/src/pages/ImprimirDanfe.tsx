import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { apiGet } from "@/lib/api";
import { Button } from "@/components/ui/button";

export default function ImprimirDanfe() {
  const [searchParams] = useSearchParams();
  const [xmlData, setXmlData] = useState<any>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    const key = searchParams.get("key");
    if (!key) {
      setErro("Chave de acesso não fornecida.");
      return;
    }

    apiGet<any>(`/financeiro/xml/${key}`)
      .then((res) => {
        if (res && res.xml) {
          const parser = new DOMParser();
          const xmlDoc = parser.parseFromString(res.xml, "text/xml");
          const isCTe = xmlDoc.getElementsByTagName("infCte").length > 0;
          const isNFe = xmlDoc.getElementsByTagName("infNFe").length > 0;

          if (isNFe) {
            setXmlData(parseNFe(xmlDoc));
          } else if (isCTe) {
            setXmlData(parseCTe(xmlDoc));
          } else {
            setErro("XML inválido.");
          }
        }
      })
      .catch((err) => setErro(err.message || "Erro ao carregar XML"));
  }, [searchParams]);

  useEffect(() => {
    if (xmlData) {
      setTimeout(() => { window.print(); }, 800);
    }
  }, [xmlData]);

  if (erro) return <div className="p-8 text-rose-500">{erro}</div>;
  if (!xmlData) return <div className="p-8 text-slate-800">Carregando DANFE...</div>;

  const d = xmlData;
  const chaveFmt = d.chave.match(/.{1,4}/g)?.join(" ") || d.chave;

  return (
    <div className="bg-white text-black min-h-screen">
      <style>{`
        @media print {
          @page { size: A4 landscape; margin: 5mm; }
          body { -webkit-print-color-adjust: exact; }
          .no-print { display: none !important; }
        }
        .danfe { font-family: Arial, sans-serif; font-size: 7pt; line-height: 1.2; }
        .danfe table { width: 100%; border-collapse: collapse; font-size: 6pt; }
        .danfe th, .danfe td { border: 1px solid #000; padding: 0.5mm; text-align: center; }
        .danfe th { background: #f0f0f0; font-weight: bold; font-size: 5.5pt; }
        .danfe .label { font-size: 5.5pt; color: #444; }
        .danfe .value { font-size: 7pt; font-weight: bold; }
        .danfe .section-title { background: #e5e5e5; font-weight: bold; padding: 0.5mm 1mm; font-size: 6.5pt; border-bottom: 1px solid #000; }
        .danfe .section { border: 1px solid #000; margin-top: 1mm; }
        .danfe .section-body { padding: 1mm; }
        .danfe .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1mm; }
        .danfe .grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1mm; }
        .danfe .grid4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1mm; }
      `}</style>

      <div className="no-print p-4 bg-slate-900 flex gap-2 justify-between items-center">
        <Button onClick={() => window.location.href = "/financeiro"} variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-800">
          ← Voltar ao Financeiro
        </Button>
        <div className="flex gap-2">
          <Button onClick={() => window.print()} className="bg-purple-600 hover:bg-purple-500">Imprimir novamente</Button>
          <Button variant="outline" onClick={() => window.close()}>Fechar</Button>
        </div>
      </div>

      <div className="p-4">
        <div className="danfe border border-black p-2">
          
          {/* CABEÇALHO */}
          <div style={{ display: "flex", borderBottom: "1px solid #000", paddingBottom: "1mm", marginBottom: "1mm" }}>
            <div style={{ width: "30%", borderRight: "1px solid #000", paddingRight: "2mm" }}>
              <div style={{ fontSize: "12pt", fontWeight: "bold" }}>{d.emitente.nome}</div>
              <div>{d.emitente.endereco}</div>
              <div>CNPJ: {d.emitente.cnpj} | IE: {d.emitente.ie}</div>
            </div>
            <div style={{ width: "40%", textAlign: "center", borderRight: "1px solid #000", padding: "0 2mm" }}>
              <div style={{ fontSize: "10pt", fontWeight: "bold" }}>DANFE</div>
              <div>Documento Auxiliar da Nota Fiscal Eletrônica</div>
              <div style={{ display: "flex", justifyContent: "center", gap: "4mm", margin: "1mm 0" }}>
                <span>0 - Entrada</span><span>1 - Saída</span>
              </div>
              <div style={{ fontWeight: "bold" }}>Nº {d.numero} &nbsp; Série {d.serie}</div>
              <div style={{ margin: "1mm 0" }}><svg id="barcode"></svg></div>
              <div style={{ fontFamily: "monospace", fontSize: "8pt", letterSpacing: "1px" }}>{chaveFmt}</div>
              <div>Consulta: www.nfe.fazenda.gov.br/portal</div>
            </div>
            <div style={{ width: "30%", paddingLeft: "2mm" }}>
              <div><span className="label">Natureza da Operação:</span> <span className="value">{d.natOp}</span></div>
              <div><span className="label">Protocolo:</span> <span className="value">{d.protocolo || "—"}</span></div>
              <div><span className="label">Data Emissão:</span> <span className="value">{new Date(d.dataEmissao).toLocaleString("pt-BR")}</span></div>
            </div>
          </div>

          {/* DESTINATÁRIO */}
          <div className="section">
            <div className="section-title">DESTINATÁRIO / REMETENTE</div>
            <div className="section-body">
              <div className="grid2">
                <div><div className="label">Nome / Razão Social</div><div className="value">{d.destinatario.nome}</div></div>
                <div><div className="label">CNPJ / CPF</div><div className="value">{d.destinatario.cnpj}</div></div>
              </div>
              <div className="grid2" style={{ marginTop: "1mm" }}>
                <div><div className="label">Endereço</div><div className="value">{d.destinatario.endereco}</div></div>
                <div><div className="label">IE / CEP / Fone</div><div className="value">{d.destinatario.ie || "—"} | {d.destinatario.cep || "—"} | {d.destinatario.fone || "—"}</div></div>
              </div>
            </div>
          </div>

          {/* PRODUTOS */}
          <div className="section">
            <div className="section-title">DADOS DOS PRODUTOS / SERVIÇOS</div>
            <table>
              <thead>
                <tr>
                  <th>Cód</th><th>Descrição</th><th>NCM</th><th>CST</th><th>CFOP</th><th>Un</th>
                  <th>Qtd</th><th>Vl Unit</th><th>Vl Total</th><th>BC ICMS</th><th>Vl ICMS</th><th>Alq</th>
                </tr>
              </thead>
              <tbody>
                {d.itens.map((it: any, i: number) => (
                  <tr key={i}>
                    <td>{it.codigo}</td>
                    <td style={{ textAlign: "left" }}>{it.descricao}</td>
                    <td>{it.ncm}</td>
                    <td>{it.cst}</td>
                    <td>{it.cfop}</td>
                    <td>{it.unidade}</td>
                    <td>{it.quantidade.toFixed(3)}</td>
                    <td>{it.valorUnit.toFixed(2)}</td>
                    <td>{it.valorTotal.toFixed(2)}</td>
                    <td>{it.baseIcms.toFixed(2)}</td>
                    <td>{it.valorIcms.toFixed(2)}</td>
                    <td>{it.aliqIcms.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* IMPOSTOS */}
          <div className="section">
            <div className="section-title">CÁLCULO DO IMPOSTO</div>
            <div className="section-body">
              <div className="grid4">
                <div><div className="label">Base ICMS</div><div className="value">R$ {d.totais.baseIcms.toFixed(2)}</div></div>
                <div><div className="label">Valor ICMS</div><div className="value">R$ {d.totais.valorIcms.toFixed(2)}</div></div>
                <div><div className="label">Base ICMS ST</div><div className="value">R$ {d.totais.baseIcmsSt.toFixed(2)}</div></div>
                <div><div className="label">Valor ICMS ST</div><div className="value">R$ {d.totais.valorIcmsSt.toFixed(2)}</div></div>
                <div><div className="label">Valor IPI</div><div className="value">R$ {d.totais.valorIpi.toFixed(2)}</div></div>
                <div><div className="label">Valor Produtos</div><div className="value">R$ {d.totais.valorProdutos.toFixed(2)}</div></div>
                <div><div className="label">Frete</div><div className="value">R$ {d.totais.valorFrete.toFixed(2)}</div></div>
                <div><div className="label">Seguro</div><div className="value">R$ {d.totais.valorSeguro.toFixed(2)}</div></div>
                <div><div className="label">Desconto</div><div className="value">R$ {d.totais.valorDesconto.toFixed(2)}</div></div>
                <div><div className="label">PIS</div><div className="value">R$ {d.totais.valorPis.toFixed(2)}</div></div>
                <div><div className="label">COFINS</div><div className="value">R$ {d.totais.valorCofins.toFixed(2)}</div></div>
                <div><div className="label">Valor Total NF</div><div className="value">R$ {d.totais.valorTotal.toFixed(2)}</div></div>
              </div>
            </div>
          </div>

          {/* TRANSPORTE */}
          <div className="section">
            <div className="section-title">TRANSPORTADOR / VOLUMES TRANSPORTADOS</div>
            <div className="section-body">
              <div className="grid3">
                <div><div className="label">Transportadora</div><div className="value">{d.transporte?.transportadora || "—"}</div></div>
                <div><div className="label">Placa</div><div className="value">{d.transporte?.placa || "—"} {d.transporte?.ufPlaca || ""}</div></div>
                <div><div className="label">Modalidade Frete</div><div className="value">{d.transporte?.modFrete || "—"}</div></div>
                <div><div className="label">Volumes</div><div className="value">{d.transporte?.volumes || "—"}</div></div>
                <div><div className="label">Espécie</div><div className="value">{d.transporte?.especie || "—"}</div></div>
                <div><div className="label">Peso Bruto / Líquido</div><div className="value">{d.transporte?.pesoBruto || "—"} / {d.transporte?.pesoLiquido || "—"}</div></div>
              </div>
            </div>
          </div>

          {/* FATURA */}
          <div className="section">
            <div className="section-title">FATURA / DUPLICATAS</div>
            <div className="section-body">
              <div className="grid2">
                <div><div className="label">Fatura</div><div className="value">{d.fatura?.numero || "—"}</div></div>
                <div><div className="label">Valor Original / Líquido</div><div className="value">R$ {d.fatura?.valorOriginal?.toFixed(2) || "—"} / R$ {d.fatura?.valorLiquido?.toFixed(2) || "—"}</div></div>
              </div>
              {d.duplicatas && d.duplicatas.length > 0 && (
                <div style={{ marginTop: "1mm" }}>
                  <table>
                    <thead><tr><th>Número</th><th>Vencimento</th><th>Valor</th></tr></thead>
                    <tbody>
                      {d.duplicatas.map((dup: any, i: number) => (
                        <tr key={i}>
                          <td>{dup.numero}</td>
                          <td>{dup.vencimento}</td>
                          <td>R$ {dup.valor.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          {/* TOTAL */}
          <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "1mm" }}>
            <div style={{ border: "1px solid #000", padding: "1mm 3mm", fontSize: "9pt", fontWeight: "bold" }}>
              VALOR TOTAL: R$ {d.totais.valorTotal.toFixed(2)}
            </div>
          </div>

          <div style={{ textAlign: "center", fontSize: "5pt", marginTop: "1mm", color: "#666" }}>
            Documento gerado pelo Bravus Frota em {new Date().toLocaleString("pt-BR")} — DANFE simplificado (visualização)
          </div>
        </div>
      </div>

      {/* Código de barras via CDN */}
      <script src="https://cdn.jsdelivr.net/npm/jsbarcode@3.12.3/dist/JsBarcode.all.min.js"></script>
      <BarcodeGenerator chave={d.chave} />
    </div>
  );
}

// Componente para gerar o código de barras após o render
function BarcodeGenerator({ chave }: { chave: string }) {
  useEffect(() => {
    const tryBarcode = () => {
      const svg = document.getElementById("barcode");
      const JsBarcode = (window as any).JsBarcode;
      if (svg && JsBarcode) {
        JsBarcode(svg, chave, { format: "CODE128C", width: 1.2, height: 50, displayValue: false, margin: 0 });
      } else if (svg && !JsBarcode) {
        setTimeout(tryBarcode, 100);
      }
    };
    setTimeout(tryBarcode, 200);
  }, [chave]);
  return null;
}

// ============================================================
// PARSERS
// ============================================================
function parseNFe(xmlDoc: Document) {
  const get = (tag: string, parent?: Element | Document) => {
    const el = (parent || xmlDoc).getElementsByTagName(tag)[0];
    return el ? el.textContent || "" : "";
  };
  const infNFe = xmlDoc.getElementsByTagName("infNFe")[0];
  const chave = infNFe?.getAttribute("Id")?.replace("NFe", "") || "";
  const ide = xmlDoc.getElementsByTagName("ide")[0];
  const emit = xmlDoc.getElementsByTagName("emit")[0];
  const dest = xmlDoc.getElementsByTagName("dest")[0];
  const total = xmlDoc.getElementsByTagName("total")[0];
  const icmsTot = total?.getElementsByTagName("ICMSTot")[0];
  const transp = xmlDoc.getElementsByTagName("transp")[0];
  const cobr = xmlDoc.getElementsByTagName("cobr")[0];

  const itens: any[] = [];
  const dets = xmlDoc.getElementsByTagName("det");
  for (let i = 0; i < dets.length; i++) {
    const det = dets[i];
    const prod = det.getElementsByTagName("prod")[0];
    const imposto = det.getElementsByTagName("imposto")[0];
    const icms = imposto?.getElementsByTagName("ICMS")[0];
    const icms00 = icms?.getElementsByTagName("ICMS00")[0] || icms?.getElementsByTagName("ICMS10")[0] || icms?.getElementsByTagName("ICMSSN102")[0];
    itens.push({
      codigo: get("cProd", prod),
      descricao: get("xProd", prod),
      ncm: get("NCM", prod),
      cst: icms00 ? get("CST", icms00) || get("CSOSN", icms00) : "",
      cfop: get("CFOP", prod),
      unidade: get("uCom", prod),
      quantidade: parseFloat(get("qCom", prod)) || 0,
      valorUnit: parseFloat(get("vUnCom", prod)) || 0,
      valorTotal: parseFloat(get("vProd", prod)) || 0,
      baseIcms: parseFloat(get("vBC", icms00 || prod)) || 0,
      valorIcms: parseFloat(get("vICMS", icms00 || prod)) || 0,
      aliqIcms: parseFloat(get("pICMS", icms00 || prod)) || 0,
    });
  }

  const endEmit = emit?.getElementsByTagName("enderEmit")[0];
  const endDest = dest?.getElementsByTagName("enderDest")[0];
  const transporta = transp?.getElementsByTagName("transporta")[0];
  const veicTransp = transp?.getElementsByTagName("veicTransp")[0];
  const vol = transp?.getElementsByTagName("vol")[0];
  const fat = cobr?.getElementsByTagName("fat")[0];
  const dups = cobr?.getElementsByTagName("dup") || [];
  const duplicatas: any[] = [];
  for (let i = 0; i < dups.length; i++) {
    const dup = dups[i];
    duplicatas.push({
      numero: get("nDup", dup),
      vencimento: get("dVenc", dup),
      valor: parseFloat(get("vDup", dup)) || 0,
    });
  }

  return {
    tipo: "NF-e",
    chave,
    numero: get("nNF", ide),
    serie: get("serie", ide),
    dataEmissao: get("dhEmi", ide),
    natOp: get("natOp", ide),
    protocolo: "",
    emitente: {
      nome: get("xNome", emit),
      cnpj: get("CNPJ", emit),
      ie: get("IE", emit),
      endereco: `${get("xLgr", endEmit)}, ${get("nro", endEmit)} - ${get("xBairro", endEmit)} - ${get("xMun", endEmit)}/${get("UF", endEmit)}`,
      cep: get("CEP", endEmit),
      fone: get("fone", endEmit),
    },
    destinatario: {
      nome: get("xNome", dest),
      cnpj: get("CNPJ", dest) || get("CPF", dest),
      ie: get("IE", dest),
      endereco: `${get("xLgr", endDest)}, ${get("nro", endDest)} - ${get("xBairro", endDest)} - ${get("xMun", endDest)}/${get("UF", endDest)}`,
      cep: get("CEP", endDest),
      fone: get("fone", endDest),
    },
    itens,
    totais: {
      baseIcms: parseFloat(get("vBC", icmsTot)) || 0,
      valorIcms: parseFloat(get("vICMS", icmsTot)) || 0,
      baseIcmsSt: parseFloat(get("vBCST", icmsTot)) || 0,
      valorIcmsSt: parseFloat(get("vST", icmsTot)) || 0,
      valorProdutos: parseFloat(get("vProd", icmsTot)) || 0,
      valorFrete: parseFloat(get("vFrete", icmsTot)) || 0,
      valorSeguro: parseFloat(get("vSeg", icmsTot)) || 0,
      valorDesconto: parseFloat(get("vDesc", icmsTot)) || 0,
      valorIpi: parseFloat(get("vIPI", icmsTot)) || 0,
      valorPis: parseFloat(get("vPIS", icmsTot)) || 0,
      valorCofins: parseFloat(get("vCOFINS", icmsTot)) || 0,
      valorTotal: parseFloat(get("vNF", icmsTot)) || 0,
    },
    transporte: {
      modFrete: get("modFrete", transp),
      transportadora: get("xNome", transporta),
      placa: get("placa", veicTransp),
      ufPlaca: get("UF", veicTransp),
      volumes: get("qVol", vol),
      especie: get("esp", vol),
      pesoBruto: get("pesoB", vol),
      pesoLiquido: get("pesoL", vol),
    },
    fatura: {
      numero: get("nFat", fat),
      valorOriginal: parseFloat(get("vOrig", fat)) || 0,
      valorLiquido: parseFloat(get("vLiq", fat)) || 0,
    },
    duplicatas,
  };
}

function parseCTe(xmlDoc: Document) {
  const get = (tag: string, parent?: Element | Document) => {
    const el = (parent || xmlDoc).getElementsByTagName(tag)[0];
    return el ? el.textContent || "" : "";
  };
  const infCte = xmlDoc.getElementsByTagName("infCte")[0];
  const chave = infCte?.getAttribute("Id")?.replace("CTe", "") || "";
  const ide = xmlDoc.getElementsByTagName("ide")[0];
  const emit = xmlDoc.getElementsByTagName("emit")[0];
  const rem = xmlDoc.getElementsByTagName("rem")[0];
  const dest = xmlDoc.getElementsByTagName("dest")[0];
  const vPrest = xmlDoc.getElementsByTagName("vPrest")[0];
  const infCTeNorm = xmlDoc.getElementsByTagName("infCTeNorm")[0];
  const infDoc = infCTeNorm?.getElementsByTagName("infDoc")[0];
  const infNFe = infDoc?.getElementsByTagName("infNFe")[0];
  const infQ = infCTeNorm?.getElementsByTagName("infQ")[0];

  return {
    tipo: "CT-e",
    chave,
    numero: get("nCT", ide),
    serie: get("serie", ide),
    dataEmissao: get("dhEmi", ide),
    natOp: get("natOp", ide),
    cfop: get("CFOP", ide),
    protocolo: "",
    emitente: {
      nome: get("xNome", emit),
      cnpj: get("CNPJ", emit),
      ie: get("IE", emit),
      endereco: `${get("xLgr", emit?.getElementsByTagName("enderEmit")[0])}, ${get("nro", emit?.getElementsByTagName("enderEmit")[0])} - ${get("xMun", emit?.getElementsByTagName("enderEmit")[0])}/${get("UF", emit?.getElementsByTagName("enderEmit")[0])}`,
    },
    remetente: {
      nome: get("xNome", rem),
      cnpj: get("CNPJ", rem) || get("CPF", rem),
      ie: get("IE", rem),
      endereco: `${get("xLgr", rem?.getElementsByTagName("enderReme")[0])}, ${get("nro", rem?.getElementsByTagName("enderReme")[0])} - ${get("xMun", rem?.getElementsByTagName("enderReme")[0])}/${get("UF", rem?.getElementsByTagName("enderReme")[0])}`,
    },
    destinatario: {
      nome: get("xNome", dest),
      cnpj: get("CNPJ", dest) || get("CPF", dest),
      ie: get("IE", dest),
      endereco: `${get("xLgr", dest?.getElementsByTagName("enderDest")[0])}, ${get("nro", dest?.getElementsByTagName("enderDest")[0])} - ${get("xMun", dest?.getElementsByTagName("enderDest")[0])}/${get("UF", dest?.getElementsByTagName("enderDest")[0])}`,
    },
    valorTotal: parseFloat(get("vTPrest", vPrest)) || 0,
    valorReceber: parseFloat(get("vRec", vPrest)) || 0,
    chaveNFe: get("chave", infNFe),
    pesoBruto: get("pesoBC", infQ) || get("pesoB", infQ),
    pesoLiquido: get("pesoL", infQ),
    volumes: get("qCarga", infQ),
    itens: [],
    totais: { valorTotal: parseFloat(get("vTPrest", vPrest)) || 0 },
    transporte: {},
    fatura: {},
    duplicatas: [],
  };
}
