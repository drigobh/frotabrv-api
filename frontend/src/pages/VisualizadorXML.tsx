import { useState, useRef } from "react";
import { FileText, Upload, X, Printer, Building2, User, Truck, DollarSign, Calendar, CheckCircle2, ShieldAlert, FileSearch } from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { brl } from "@/lib/format";
import { toast } from "sonner";
import { apiGet, apiPost } from "@/lib/api";
import { useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

// ============================================================
// PARSER: NF-e
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
  const transp = xmlDoc.getElementsByTagName("transp")[0];

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
      cfop: get("CFOP", prod),
      unidade: get("uCom", prod),
      quantidade: parseFloat(get("qCom", prod)) || 0,
      valorUnit: parseFloat(get("vUnCom", prod)) || 0,
      valorTotal: parseFloat(get("vProd", prod)) || 0,
      cst: icms00 ? get("CST", icms00) || get("CSOSN", icms00) : "",
      baseIcms: parseFloat(get("vBC", icms00 || prod)) || 0,
      valorIcms: parseFloat(get("vICMS", icms00 || prod)) || 0,
      aliqIcms: parseFloat(get("pICMS", icms00 || prod)) || 0,
    });
  }

  const endEmit = emit?.getElementsByTagName("enderEmit")[0];
  const endDest = dest?.getElementsByTagName("enderDest")[0];

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
      fantasia: get("xFant", emit),
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
      baseIcms: parseFloat(get("vBC", total)) || 0,
      valorIcms: parseFloat(get("vICMS", total)) || 0,
      baseIcmsSt: parseFloat(get("vBCST", total)) || 0,
      valorIcmsSt: parseFloat(get("vICMSST", total)) || 0,
      valorProdutos: parseFloat(get("vProd", total)) || 0,
      valorFrete: parseFloat(get("vFrete", total)) || 0,
      valorSeguro: parseFloat(get("vSeg", total)) || 0,
      valorDesconto: parseFloat(get("vDesc", total)) || 0,
      valorIpi: parseFloat(get("vIPI", total)) || 0,
      valorPis: parseFloat(get("vPIS", total)) || 0,
      valorCofins: parseFloat(get("vCOFINS", total)) || 0,
      valorTotal: (() => {
      const icmsTot = total?.getElementsByTagName("ICMSTot")[0];
      return parseFloat(get("vNF", icmsTot) || get("vNF", total) || get("vProd", total)) || 0;
    })(),
    },
    transporte: {
      modFrete: get("modFrete", transp),
      transportadora: get("xNome", transp?.getElementsByTagName("transporta")[0] || transp),
      placa: get("placa", transp?.getElementsByTagName("veicTransp")[0] || transp),
      ufPlaca: get("UF", transp?.getElementsByTagName("veicTransp")[0] || transp),
      volumes: get("qVol", transp),
      especie: get("esp", transp),
      pesoBruto: get("pesoB", transp),
      pesoLiquido: get("pesoL", transp),
    },
  };
}

// ============================================================
// PARSER: CT-e
// ============================================================
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
      fantasia: "",
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
  };
}

// ============================================================
// COMPONENTE PRINCIPAL
// ============================================================
export default function VisualizadorXML() {
  const navigate = useNavigate();
  const [xmlString, setXmlString] = useState("");
  const [dados, setDados] = useState<any>(null);
  const [tipo, setTipo] = useState<"NF-e" | "CT-e" | null>(null);
  const [erro, setErro] = useState("");
  const [modalImportOpen, setModalImportOpen] = useState(false);
  const [tipoConta, setTipoConta] = useState<"Pagar" | "Receber">("Pagar");
  const [loadingImport, setLoadingImport] = useState(false);
  const [formForn, setFormForn] = useState<any>({});
  const qc = useQueryClient();

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (evt) => {
      const content = evt.target?.result as string;
      setXmlString(content);
      processarXML(content);
    };
    reader.readAsText(file);
  };

  const processarXML = (xml: string) => {
    setErro("");
    setDados(null);
    setTipo(null);
    try {
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(xml, "text/xml");
      const isCTe = xmlDoc.getElementsByTagName("infCte").length > 0;
      const isNFe = xmlDoc.getElementsByTagName("infNFe").length > 0;

      if (isCTe) {
        const d = parseCTe(xmlDoc);
        setDados(d);
        setTipo("CT-e");
        toast.success("CT-e lido com sucesso!");
      } else if (isNFe) {
        const d = parseNFe(xmlDoc);
        setDados(d);
        setTipo("NF-e");
        toast.success("NF-e lida com sucesso!");
      } else {
        throw new Error("XML inválido. Deve ser CT-e ou NF-e (versão 4.00).");
      }
    } catch (e: any) {
      setErro(e.message);
      toast.error(e.message);
    }
  };

  // ============================================================
  // GERAÇÃO DO HTML PARA IMPRESSÃO (DANFE / DACTE)
  // ============================================================
  const imprimir = () => {
    if (!dados || !tipo) return;
    const win = window.open("", "_blank");
    if (!win) {
      toast.error("Permita pop-ups para imprimir.");
      return;
    }

    const isNFe = tipo === "NF-e";
    const d = dados;

    // Código de barras será gerado após abrir a janela
    const html = isNFe ? gerarDanfeHTML(d) : gerarDacteHTML(d);

    win.document.write(html);
    win.document.close();

    // Após renderizar, gera o código de barras
    setTimeout(() => {
      try {
        const svg = win.document.getElementById("barcode");
        if (svg) {
          (window as any).JsBarcode(svg, d.chave, {
            format: "CODE128C",
            width: 1.2,
            height: 50,
            displayValue: false,
            margin: 0,
          });
        }
      } catch (e) {
        console.warn("Erro ao gerar código de barras:", e);
      }
      win.focus();
      setTimeout(() => {
        win.print();
        // win.close(); // descomente se quiser fechar após imprimir
      }, 500);
    }, 300);
  };


  const executarImportacao = async () => {
    if (loadingImport) return;
    setLoadingImport(true);
    try {
      const cnpjEmitente = dados.emitente.cnpj.replace(/\D/g, "");
      const valorReal = Number(dados.valorTotal) || 0;

      // VERIFICA DUPLICIDADE
      const contasExistentes = await apiGet<any[]>("/financeiro/contas");
      const jaImportada = contasExistentes.find(c => c.documento_vinculo === dados.chave);
      if (jaImportada) {
        toast.error("Este XML já foi importado para o Financeiro!");
        setLoadingImport(false);
        return;
      }

      if (tipoConta === "Pagar") {
        const fornecedores = await apiGet<any[]>("/fornecedores");
        const fornecedorExistente = fornecedores.find(f => (f.documento || "").replace(/\D/g, "") === cnpjEmitente);
        
        if (!fornecedorExistente) {
          toast.error("Fornecedor não cadastrado! Cadastre o CNPJ " + dados.emitente.cnpj + " antes de importar.");
          setLoadingImport(false);
          return;
        }

        await apiPost("/financeiro/contas", {
          tipo: "Pagar",
          descricao: `NF-e ${dados.numero} - ${dados.emitente.nome}`,
          categoria: "Peças e componentes",
          valor: valorReal,
          vencimento: new Date().toISOString().split("T")[0],
          status: "Pendente",
          fornecedor_id: fornecedorExistente.id,
          documento_vinculo: dados.chave,
          origem: "Importado XML"
        });
      } else {
        await apiPost("/financeiro/contas", {
          tipo: "Receber",
          descricao: `NF-e ${dados.numero} - ${dados.destinatario.nome}`,
          categoria: "Frete",
          valor: valorReal,
          vencimento: new Date().toISOString().split("T")[0],
          status: "Pendente",
          documento_vinculo: dados.chave,
          origem: "Importado XML"
        });
      }

      toast.success("Importado com sucesso!");
      qc.invalidateQueries({ queryKey: ["contas"] });
      qc.invalidateQueries({ queryKey: ["resumo-financeiro"] });
      navigate("/financeiro");
    } catch (e: any) {
      toast.error("Erro ao importar: " + (e.message || "Verifique os dados"));
    } finally {
      setLoadingImport(false);
    }
  };

  return (
    <div>
      <PageHeader
        eyebrow="Gestão"
        title="Visualizador de XML"
        description="Leia o XML do CT-e ou NF-e, visualize o DANFE/DACTE oficial e imprima."
        actions={
          <Button variant="outline" onClick={() => navigate("/financeiro")} className="border-slate-700 text-slate-300">
            Voltar ao Financeiro
          </Button>
        }
      />

      {/* Upload */}
      <div className="glass p-6 rounded-2xl border border-slate-800 mb-6">
        <h3 className="text-sm font-bold text-slate-100 mb-4 flex items-center gap-2">
          <Upload className="size-4 text-sky-400" /> Importar XML
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            className="border-2 border-dashed border-slate-700 rounded-xl p-8 text-center hover:bg-slate-800/50 transition-colors cursor-pointer"
            onClick={() => document.getElementById("xml-input")?.click()}
          >
            <input id="xml-input" type="file" accept=".xml" onChange={handleFileUpload} className="hidden" />
            <FileText className="size-8 mx-auto text-slate-400 mb-2" />
            <p className="text-sm font-medium text-slate-200">Selecione o arquivo XML</p>
            <p className="text-xs text-slate-500 mt-1">NF-e ou CT-e (versão 4.00)</p>
          </div>
          <div>
            <Label className="text-xs text-slate-400">Ou cole o conteúdo do XML:</Label>
            <textarea
              value={xmlString}
              onChange={(e) => setXmlString(e.target.value)}
              className="w-full h-24 bg-slate-950 border border-slate-700 rounded-md p-2 text-xs text-slate-300 font-mono mt-1"
              placeholder="Cole o XML aqui..."
            />
            <Button onClick={() => processarXML(xmlString)} className="w-full mt-2 bg-sky-600 hover:bg-sky-500">
              Processar XML
            </Button>
          </div>
        </div>
        {erro && (
          <div className="mt-4 p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg flex items-center gap-2 text-rose-400">
            <ShieldAlert className="size-4" /> {erro}
          </div>
        )}
      </div>

      {/* Preview resumido */}
      {dados && (
        <div className="glass p-6 rounded-2xl border border-emerald-500/30">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-bold text-emerald-400 flex items-center gap-2">
              <CheckCircle2 className="size-5" /> {tipo} Lida com Sucesso
            </h3>
            <Button onClick={imprimir} className="bg-sky-600 hover:bg-sky-500">
              <Printer className="size-4 mr-2" /> Imprimir {tipo === "NF-e" ? "DANFE" : "DACTE"}
            </Button>
            <Button onClick={() => setModalImportOpen(true)} className="bg-emerald-600 hover:bg-emerald-500 ml-2">
              <DollarSign className="size-4 mr-2" /> Importar para Financeiro
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
            <div>
              <p className="text-[10px] uppercase text-slate-500 mb-1">Chave de Acesso</p>
              <p className="font-mono text-xs text-slate-200 break-all">{dados.chave}</p>
              <p className="text-[10px] uppercase text-slate-500 mt-3">Número / Série</p>
              <p className="text-slate-200 font-bold">{dados.numero} / {dados.serie}</p>
              <p className="text-[10px] uppercase text-slate-500 mt-2">Emissão</p>
              <p className="text-slate-200">{dados.dataEmissao ? new Date(dados.dataEmissao).toLocaleString("pt-BR") : "—"}</p>
            </div>
            <div>
              <p className="text-[10px] uppercase text-slate-500 flex items-center gap-1"><Building2 className="size-3" /> Emitente</p>
              <p className="text-slate-200 font-bold">{dados.emitente.nome}</p>
              <p className="text-xs text-slate-400">{dados.emitente.cnpj}</p>
              {tipo === "CT-e" && dados.remetente && (
                <>
                  <p className="text-[10px] uppercase text-slate-500 mt-2 flex items-center gap-1"><Truck className="size-3" /> Remetente</p>
                  <p className="text-slate-200 font-bold">{dados.remetente.nome}</p>
                  <p className="text-xs text-slate-400">{dados.remetente.cnpj}</p>
                </>
              )}
              <p className="text-[10px] uppercase text-slate-500 mt-2 flex items-center gap-1"><User className="size-3" /> Destinatário</p>
              <p className="text-slate-200 font-bold">{dados.destinatario.nome}</p>
              <p className="text-xs text-slate-400">{dados.destinatario.cnpj}</p>
            </div>
          </div>

          <div className="mt-4 p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex justify-between items-center">
            <span className="text-sm font-medium text-emerald-400">Valor Total</span>
            <span className="text-2xl font-bold text-emerald-400 font-mono">
              {brl(dados.valorTotal || dados.itens?.reduce((acc: number, it: any) => acc + (it.valorTotal || 0), 0) || 0)}
            </span>
          </div>

          {tipo === "NF-e" && dados.itens?.length > 0 && (
            <div className="mt-4 overflow-x-auto">
              <p className="text-[10px] uppercase text-slate-500 mb-2">Itens ({dados.itens.length})</p>
              <table className="w-full text-xs">
                <thead className="text-slate-500 border-b border-slate-700">
                  <tr>
                    <th className="text-left py-1">Cód</th>
                    <th className="text-left py-1">Descrição</th>
                    <th className="text-right py-1">Qtd</th>
                    <th className="text-right py-1">Unit</th>
                    <th className="text-right py-1">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {dados.itens.map((it: any, i: number) => (
                    <tr key={i} className="border-b border-slate-800/50">
                      <td className="py-1 font-mono text-slate-400">{it.codigo}</td>
                      <td className="py-1 text-slate-200">{it.descricao}</td>
                      <td className="text-right py-1 text-slate-300">{it.quantidade}</td>
                      <td className="text-right py-1 text-slate-300">{brl(it.valorUnit)}</td>
                      <td className="text-right py-1 text-slate-200 font-bold">{brl(it.valorTotal)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* MODAL DE IMPORTAÇÃO PARA O FINANCEIRO */}
      {modalImportOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-lg p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-2">Importar para Financeiro</h2>
            <p className="text-sm text-slate-400 mb-6">Selecione o tipo de conta para lançar este documento.</p>
            
            <div className="flex gap-4 mb-6">
              <Button variant={tipoConta === "Pagar" ? "default" : "outline"} onClick={() => setTipoConta("Pagar")} className="flex-1">Contas a Pagar</Button>
              <Button variant={tipoConta === "Receber" ? "default" : "outline"} onClick={() => setTipoConta("Receber")} className="flex-1">Contas a Receber</Button>
            </div>

            {tipoConta === "Pagar" && (
              <div className="bg-slate-800/50 p-4 rounded-lg mb-4">
                <p className="text-xs text-slate-400 mb-2">Fornecedor (Emitente do XML)</p>
                <p className="text-sm font-bold text-slate-200">{dados.emitente.nome}</p>
                <p className="text-xs text-slate-400 font-mono">{dados.emitente.cnpj}</p>
              </div>
            )}

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setModalImportOpen(false)}>Cancelar</Button>
              <Button onClick={executarImportacao} disabled={loadingImport} className="bg-emerald-600 hover:bg-emerald-500">
                {loadingImport ? "Importando..." : "Confirmar Importação"}
              </Button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

// ============================================================
// HTML DO DANFE (NF-e) — Layout Oficial Simplificado A4 Paisagem
// ============================================================
function gerarDanfeHTML(d: any): string {
  const fmt = (v: number) => v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const chaveFmt = d.chave.replace(/(\d{4})/g, "$1 ").trim();

  const itensRows = (d.itens || []).map((it: any) => `
    <tr>
      <td>${it.codigo}</td>
      <td style="text-align:left">${it.descricao}</td>
      <td>${it.ncm}</td>
      <td>${it.cst}</td>
      <td>${it.cfop}</td>
      <td>${it.unidade}</td>
      <td style="text-align:right">${it.quantidade.toFixed(3)}</td>
      <td style="text-align:right">${fmt(it.valorUnit)}</td>
      <td style="text-align:right">${fmt(it.valorTotal)}</td>
      <td style="text-align:right">${fmt(it.baseIcms)}</td>
      <td style="text-align:right">${fmt(it.valorIcms)}</td>
      <td style="text-align:right">${it.aliqIcms.toFixed(2)}</td>
    </tr>
  `).join("");

  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>DANFE - ${d.numero}</title>
      <style>
        @page { size: A4 landscape; margin: 5mm; }
        body { font-family: Arial, sans-serif; font-size: 7pt; margin: 0; padding: 0; }
        .danfe { border: 1px solid #000; padding: 2mm; }
        .header { display: flex; border-bottom: 1px solid #000; padding-bottom: 1mm; margin-bottom: 1mm; }
        .header-left { width: 30%; border-right: 1px solid #000; padding-right: 2mm; }
        .header-center { width: 40%; text-align: center; border-right: 1px solid #000; padding: 0 2mm; }
        .header-right { width: 30%; padding-left: 2mm; font-size: 6pt; }
        .logo { font-size: 14pt; font-weight: bold; }
        .titulo { font-size: 10pt; font-weight: bold; margin: 1mm 0; }
        .chave { font-family: monospace; font-size: 8pt; letter-spacing: 1px; }
        .barcode-box { text-align: center; margin: 1mm 0; }
        .barcode-box svg { max-width: 100%; height: 40px; }
        .section { border: 1px solid #000; margin-top: 1mm; }
        .section-title { background: #f0f0f0; font-weight: bold; padding: 0.5mm 1mm; font-size: 6.5pt; border-bottom: 1px solid #000; }
        .section-body { padding: 1mm; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1mm; }
        .grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1mm; }
        .field { margin-bottom: 0.5mm; }
        .label { font-size: 5.5pt; color: #666; }
        .value { font-size: 7pt; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; font-size: 6pt; }
        th { background: #f0f0f0; border: 1px solid #000; padding: 0.5mm; text-align: center; font-size: 5.5pt; }
        td { border: 1px solid #000; padding: 0.5mm; text-align: center; }
        .total-box { display: flex; justify-content: flex-end; margin-top: 1mm; }
        .total-item { border: 1px solid #000; padding: 1mm 3mm; font-size: 8pt; font-weight: bold; }
        .footer { text-align: center; font-size: 5pt; margin-top: 1mm; color: #666; }
        @media print { body { -webkit-print-color-adjust: exact; } }
      </style>
    </head>
    <body>
      <div class="danfe">
        <!-- CABEÇALHO -->
        <div class="header">
          <div class="header-left">
            <div class="logo">${d.emitente.nome || "EMITENTE"}</div>
            <div style="font-size:6pt">${d.emitente.endereco || ""}</div>
            <div style="font-size:6pt">CNPJ: ${d.emitente.cnpj || ""} | IE: ${d.emitente.ie || ""}</div>
          </div>
          <div class="header-center">
            <div class="titulo">DANFE</div>
            <div style="font-size:5.5pt">Documento Auxiliar da Nota Fiscal Eletrônica</div>
            <div style="font-size:5.5pt;margin:1mm 0">0 - Entrada &nbsp;&nbsp; 1 - Saída</div>
            <div style="font-size:7pt">Nº ${d.numero} &nbsp; Série ${d.serie}</div>
            <div class="barcode-box"><svg id="barcode"></svg></div>
            <div class="chave">${chaveFmt}</div>
            <div style="font-size:5.5pt">Consulta: www.nfe.fazenda.gov.br/portal</div>
          </div>
          <div class="header-right">
            <div><b>Natureza da Operação:</b> ${d.natOp || "—"}</div>
            <div><b>Protocolo:</b> ${d.protocolo || "—"}</div>
            <div><b>Data Emissão:</b> ${d.dataEmissao ? new Date(d.dataEmissao).toLocaleString("pt-BR") : "—"}</div>
          </div>
        </div>

        <!-- DESTINATÁRIO -->
        <div class="section">
          <div class="section-title">DESTINATÁRIO / REMETENTE</div>
          <div class="section-body">
            <div class="grid">
              <div class="field"><div class="label">Nome / Razão Social</div><div class="value">${d.destinatario.nome || "—"}</div></div>
              <div class="field"><div class="label">CNPJ / CPF</div><div class="value">${d.destinatario.cnpj || "—"}</div></div>
            </div>
            <div class="grid">
              <div class="field"><div class="label">Endereço</div><div class="value">${d.destinatario.endereco || "—"}</div></div>
              <div class="field"><div class="label">IE / CEP / Fone</div><div class="value">${d.destinatario.ie || "—"} | ${d.destinatario.cep || "—"} | ${d.destinatario.fone || "—"}</div></div>
            </div>
          </div>
        </div>

        <!-- PRODUTOS -->
        <div class="section">
          <div class="section-title">DADOS DOS PRODUTOS / SERVIÇOS</div>
          <div class="section-body" style="padding:0">
            <table>
              <thead>
                <tr>
                  <th>Cód</th><th>Descrição</th><th>NCM</th><th>CST</th><th>CFOP</th><th>Un</th>
                  <th>Qtd</th><th>Vl Unit</th><th>Vl Total</th><th>BC ICMS</th><th>Vl ICMS</th><th>Alq</th>
                </tr>
              </thead>
              <tbody>
                ${itensRows || '<tr><td colspan="12">Nenhum item</td></tr>'}
              </tbody>
            </table>
          </div>
        </div>

        <!-- IMPOSTOS -->
        <div class="section">
          <div class="section-title">CÁLCULO DO IMPOSTO</div>
          <div class="section-body">
            <div class="grid3">
              <div class="field"><div class="label">Base ICMS</div><div class="value">R$ ${fmt(d.totais.baseIcms)}</div></div>
              <div class="field"><div class="label">Valor ICMS</div><div class="value">R$ ${fmt(d.totais.valorIcms)}</div></div>
              <div class="field"><div class="label">Base ICMS ST</div><div class="value">R$ ${fmt(d.totais.baseIcmsSt)}</div></div>
              <div class="field"><div class="label">Valor ICMS ST</div><div class="value">R$ ${fmt(d.totais.valorIcmsSt)}</div></div>
              <div class="field"><div class="label">Valor IPI</div><div class="value">R$ ${fmt(d.totais.valorIpi)}</div></div>
              <div class="field"><div class="label">Valor Produtos</div><div class="value">R$ ${fmt(d.totais.valorProdutos)}</div></div>
              <div class="field"><div class="label">Frete</div><div class="value">R$ ${fmt(d.totais.valorFrete)}</div></div>
              <div class="field"><div class="label">Seguro</div><div class="value">R$ ${fmt(d.totais.valorSeguro)}</div></div>
              <div class="field"><div class="label">Desconto</div><div class="value">R$ ${fmt(d.totais.valorDesconto)}</div></div>
              <div class="field"><div class="label">PIS</div><div class="value">R$ ${fmt(d.totais.valorPis)}</div></div>
              <div class="field"><div class="label">COFINS</div><div class="value">R$ ${fmt(d.totais.valorCofins)}</div></div>
              <div class="field"><div class="label">Valor Total NF</div><div class="value">R$ ${fmt(d.totais.valorTotal)}</div></div>
            </div>
          </div>
        </div>

        <!-- TRANSPORTE -->
        <div class="section">
          <div class="section-title">TRANSPORTADOR / VOLUMES TRANSPORTADOS</div>
          <div class="section-body">
            <div class="grid3">
              <div class="field"><div class="label">Transportadora</div><div class="value">${d.transporte?.transportadora || "—"}</div></div>
              <div class="field"><div class="label">Placa</div><div class="value">${d.transporte?.placa || "—"} ${d.transporte?.ufPlaca || ""}</div></div>
              <div class="field"><div class="label">Modalidade Frete</div><div class="value">${d.transporte?.modFrete || "—"}</div></div>
              <div class="field"><div class="label">Volumes</div><div class="value">${d.transporte?.volumes || "—"}</div></div>
              <div class="field"><div class="label">Espécie</div><div class="value">${d.transporte?.especie || "—"}</div></div>
              <div class="field"><div class="label">Peso Bruto / Líquido</div><div class="value">${d.transporte?.pesoBruto || "—"} / ${d.transporte?.pesoLiquido || "—"}</div></div>
            </div>
          </div>
        </div>

        <div class="total-box">
          <div class="total-item">VALOR TOTAL: R$ ${fmt(d.totais.valorTotal)}</div>
        </div>

        <div class="footer">
          Documento gerado pelo Bravus Frota em ${new Date().toLocaleString("pt-BR")} — DANFE simplificado (visualização)
        </div>
      </div>
    </body>
    </html>
  `;
}

// ============================================================
// HTML DO DACTE (CT-e) — Layout Simplificado A4 Paisagem
// ============================================================
function gerarDacteHTML(d: any): string {
  const fmt = (v: number) => v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const chaveFmt = d.chave.replace(/(\d{4})/g, "$1 ").trim();

  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>DACTE - ${d.numero}</title>
      <style>
        @page { size: A4 landscape; margin: 5mm; }
        body { font-family: Arial, sans-serif; font-size: 7pt; margin: 0; padding: 0; }
        .dacte { border: 1px solid #000; padding: 2mm; }
        .header { display: flex; border-bottom: 1px solid #000; padding-bottom: 1mm; margin-bottom: 1mm; }
        .header-left { width: 30%; border-right: 1px solid #000; padding-right: 2mm; }
        .header-center { width: 40%; text-align: center; border-right: 1px solid #000; padding: 0 2mm; }
        .header-right { width: 30%; padding-left: 2mm; font-size: 6pt; }
        .logo { font-size: 14pt; font-weight: bold; }
        .titulo { font-size: 10pt; font-weight: bold; margin: 1mm 0; }
        .chave { font-family: monospace; font-size: 8pt; letter-spacing: 1px; }
        .barcode-box { text-align: center; margin: 1mm 0; }
        .barcode-box svg { max-width: 100%; height: 40px; }
        .section { border: 1px solid #000; margin-top: 1mm; }
        .section-title { background: #f0f0f0; font-weight: bold; padding: 0.5mm 1mm; font-size: 6.5pt; border-bottom: 1px solid #000; }
        .section-body { padding: 1mm; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1mm; }
        .grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1mm; }
        .field { margin-bottom: 0.5mm; }
        .label { font-size: 5.5pt; color: #666; }
        .value { font-size: 7pt; font-weight: bold; }
        .total-box { display: flex; justify-content: flex-end; margin-top: 1mm; }
        .total-item { border: 1px solid #000; padding: 1mm 3mm; font-size: 8pt; font-weight: bold; }
        .footer { text-align: center; font-size: 5pt; margin-top: 1mm; color: #666; }
        @media print { body { -webkit-print-color-adjust: exact; } }
      </style>
    </head>
    <body>
      <div class="dacte">
        <div class="header">
          <div class="header-left">
            <div class="logo">${d.emitente.nome || "TRANSPORTADORA"}</div>
            <div style="font-size:6pt">${d.emitente.endereco || ""}</div>
            <div style="font-size:6pt">CNPJ: ${d.emitente.cnpj || ""} | IE: ${d.emitente.ie || ""}</div>
          </div>
          <div class="header-center">
            <div class="titulo">DACTE</div>
            <div style="font-size:5.5pt">Documento Auxiliar do Conhecimento de Transporte Eletrônico</div>
            <div style="font-size:7pt;margin:1mm 0">Nº ${d.numero} &nbsp; Série ${d.serie}</div>
            <div class="barcode-box"><svg id="barcode"></svg></div>
            <div class="chave">${chaveFmt}</div>
            <div style="font-size:5.5pt">Consulta: www.cte.fazenda.gov.br</div>
          </div>
          <div class="header-right">
            <div><b>Natureza:</b> ${d.natOp || "—"}</div>
            <div><b>CFOP:</b> ${d.cfop || "—"}</div>
            <div><b>Emissão:</b> ${d.dataEmissao ? new Date(d.dataEmissao).toLocaleString("pt-BR") : "—"}</div>
            <div><b>Protocolo:</b> ${d.protocolo || "—"}</div>
          </div>
        </div>

        <!-- REMETENTE -->
        <div class="section">
          <div class="section-title">REMETENTE</div>
          <div class="section-body">
            <div class="grid">
              <div class="field"><div class="label">Nome / Razão Social</div><div class="value">${d.remetente.nome || "—"}</div></div>
              <div class="field"><div class="label">CNPJ / CPF</div><div class="value">${d.remetente.cnpj || "—"}</div></div>
            </div>
            <div class="grid">
              <div class="field"><div class="label">Endereço</div><div class="value">${d.remetente.endereco || "—"}</div></div>
              <div class="field"><div class="label">IE</div><div class="value">${d.remetente.ie || "—"}</div></div>
            </div>
          </div>
        </div>

        <!-- DESTINATÁRIO -->
        <div class="section">
          <div class="section-title">DESTINATÁRIO</div>
          <div class="section-body">
            <div class="grid">
              <div class="field"><div class="label">Nome / Razão Social</div><div class="value">${d.destinatario.nome || "—"}</div></div>
              <div class="field"><div class="label">CNPJ / CPF</div><div class="value">${d.destinatario.cnpj || "—"}</div></div>
            </div>
            <div class="grid">
              <div class="field"><div class="label">Endereço</div><div class="value">${d.destinatario.endereco || "—"}</div></div>
              <div class="field"><div class="label">IE</div><div class="value">${d.destinatario.ie || "—"}</div></div>
            </div>
          </div>
        </div>

        <!-- CARGA -->
        <div class="section">
          <div class="section-title">INFORMAÇÕES DA CARGA</div>
          <div class="section-body">
            <div class="grid3">
              <div class="field"><div class="label">Chave NF-e</div><div class="value" style="font-family:monospace;font-size:6pt">${d.chaveNFe || "—"}</div></div>
              <div class="field"><div class="label">Peso Bruto</div><div class="value">${d.pesoBruto || "—"} kg</div></div>
              <div class="field"><div class="label">Peso Líquido</div><div class="value">${d.pesoLiquido || "—"} kg</div></div>
            </div>
          </div>
        </div>

        <!-- VALORES -->
        <div class="section">
          <div class="section-title">VALORES DA PRESTAÇÃO DE SERVIÇO</div>
          <div class="section-body">
            <div class="grid">
              <div class="field"><div class="label">Valor Total do Serviço</div><div class="value">R$ ${fmt(d.valorTotal)}</div></div>
              <div class="field"><div class="label">Valor a Receber</div><div class="value">R$ ${fmt(d.valorReceber)}</div></div>
            </div>
          </div>
        </div>

        <div class="total-box">
          <div class="total-item">VALOR TOTAL: R$ ${fmt(d.valorTotal)}</div>
        </div>

        <div class="footer">
          Documento gerado pelo Bravus Frota em ${new Date().toLocaleString("pt-BR")} — DACTE simplificado (visualização)
        </div>
      </div>
    </body>
    </html>
  `;
}
