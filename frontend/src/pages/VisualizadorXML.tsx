import { useState, useRef } from "react";
import { FileText, Upload, Printer, Building2, User, Truck, CheckCircle2, ShieldAlert, DollarSign } from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { brl } from "@/lib/format";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPost } from "@/lib/api";

// === PARSERS ===
function parseXML(xmlString: string) {
  const parser = new DOMParser();
  const xmlDoc = parser.parseFromString(xmlString, "text/xml");

  const isCTe = xmlDoc.getElementsByTagName("infCte").length > 0;
  const isNFe = xmlDoc.getElementsByTagName("infNFe").length > 0;

  if (!isCTe && !isNFe) throw new Error("XML inválido. Deve ser CT-e ou NF-e.");

  const get = (tag: string, parent?: Element | Document) => {
    const el = (parent || xmlDoc).getElementsByTagName(tag)[0];
    return el ? el.textContent || "" : "";
  };

  if (isCTe) {
    const infCte = xmlDoc.getElementsByTagName("infCte")[0];
    const chave = infCte?.getAttribute("Id")?.replace("CTe", "") || "";
    const ide = xmlDoc.getElementsByTagName("ide")[0];
    const emit = xmlDoc.getElementsByTagName("emit")[0];
    const rem = xmlDoc.getElementsByTagName("rem")[0];
    const dest = xmlDoc.getElementsByTagName("dest")[0];
    const vPrest = xmlDoc.getElementsByTagName("vPrest")[0];

    return {
      tipo: "CT-e",
      chave,
      numero: get("nCT", ide),
      serie: get("serie", ide),
      dataEmissao: get("dhEmi", ide),
      emitente: { nome: get("xNome", emit), cnpj: get("CNPJ", emit) },
      remetente: { nome: get("xNome", rem), cnpj: get("CNPJ", rem) },
      destinatario: { nome: get("xNome", dest), cnpj: get("CNPJ", dest) },
      valorTotal: parseFloat(get("vTPrest", vPrest)) || 0,
      valorReceber: parseFloat(get("vRec", vPrest)) || 0,
      itens: []
    };
  } else {
    const infNFe = xmlDoc.getElementsByTagName("infNFe")[0];
    const chave = infNFe?.getAttribute("Id")?.replace("NFe", "") || "";
    const ide = xmlDoc.getElementsByTagName("ide")[0];
    const emit = xmlDoc.getElementsByTagName("emit")[0];
    const dest = xmlDoc.getElementsByTagName("dest")[0];
    const total = xmlDoc.getElementsByTagName("total")[0];
    const icmsTot = total?.getElementsByTagName("ICMSTot")[0];

    const itens: any[] = [];
    const dets = xmlDoc.getElementsByTagName("det");
    for (let i = 0; i < dets.length; i++) {
      const det = dets[i];
      const prod = det.getElementsByTagName("prod")[0];
      itens.push({
        codigo: get("cProd", prod),
        descricao: get("xProd", prod),
        ncm: get("NCM", prod),
        cfop: get("CFOP", prod),
        unidade: get("uCom", prod),
        quantidade: parseFloat(get("qCom", prod)) || 0,
        valorUnit: parseFloat(get("vUnCom", prod)) || 0,
        valorTotal: parseFloat(get("vProd", prod)) || 0,
      });
    }

    return {
      tipo: "NF-e",
      chave,
      numero: get("nNF", ide),
      serie: get("serie", ide),
      dataEmissao: get("dhEmi", ide),
      natOp: get("natOp", ide),
      emitente: { 
        nome: get("xNome", emit), 
        cnpj: get("CNPJ", emit),
        endereco: `${get("xLgr", emit?.getElementsByTagName("enderEmit")[0])}, ${get("nro", emit?.getElementsByTagName("enderEmit")[0])} - ${get("xBairro", emit?.getElementsByTagName("enderEmit")[0])} - ${get("xMun", emit?.getElementsByTagName("enderEmit")[0])}/${get("UF", emit?.getElementsByTagName("enderEmit")[0])}`
      },
      destinatario: { 
        nome: get("xNome", dest), 
        cnpj: get("CNPJ", dest) || get("CPF", dest),
        endereco: `${get("xLgr", dest?.getElementsByTagName("enderDest")[0])}, ${get("nro", dest?.getElementsByTagName("enderDest")[0])} - ${get("xBairro", dest?.getElementsByTagName("enderDest")[0])} - ${get("xMun", dest?.getElementsByTagName("enderDest")[0])}/${get("UF", dest?.getElementsByTagName("enderDest")[0])}`
      },
      // Pega o vNF, se não tiver, tenta vProd
      valorTotal: parseFloat(get("vNF", icmsTot || total)) || parseFloat(get("vProd", icmsTot || total)) || 0,
      itens
    };
  }
}

export default function VisualizadorXML() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [xmlString, setXmlString] = useState("");
  const [dados, setDados] = useState<any>(null);
  const [erro, setErro] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [tipoConta, setTipoConta] = useState<"Pagar" | "Receber">("Pagar");
  const [loadingImport, setLoadingImport] = useState(false);

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
    try {
      const d = parseXML(xml);
      setDados(d);
      toast.success(`${d.tipo} lida com sucesso!`);
    } catch (e: any) {
      setErro(e.message);
      toast.error(e.message);
    }
  };

  const executarImportacao = async () => {
    if (loadingImport) return;
    setLoadingImport(true);
    try {
      const cnpjEmitente = dados.emitente.cnpj.replace(/\D/g, "");
      const valorReal = Number(dados.valorTotal) || 0;

      // Verifica duplicidade
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
      setModalOpen(false);
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

      {dados && (
        <div className="glass p-6 rounded-2xl border border-emerald-500/30">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-bold text-emerald-400 flex items-center gap-2">
              <CheckCircle2 className="size-5" /> {dados.tipo} Lida com Sucesso
            </h3>
            <div className="flex gap-2">
              <Button onClick={() => setModalOpen(true)} className="bg-emerald-600 hover:bg-emerald-500">
                <DollarSign className="size-4 mr-2" /> Importar para Financeiro
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
            <div>
              <p className="text-[10px] uppercase text-slate-500 mb-1">Chave de Acesso</p>
              <p className="font-mono text-xs text-slate-200 break-all">{dados.chave}</p>
              <p className="text-[10px] uppercase text-slate-500 mt-3">Número / Série</p>
              <p className="text-slate-200 font-bold">{dados.numero} / {dados.serie}</p>
            </div>
            <div>
              <p className="text-[10px] uppercase text-slate-500 flex items-center gap-1"><Building2 className="size-3" /> Emitente</p>
              <p className="text-slate-200 font-bold">{dados.emitente.nome}</p>
              <p className="text-xs text-slate-400">{dados.emitente.cnpj}</p>
            </div>
          </div>

          <div className="mt-4 p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex justify-between items-center">
            <span className="text-sm font-medium text-emerald-400">Valor Total</span>
            <span className="text-2xl font-bold text-emerald-400 font-mono">{brl(dados.valorTotal)}</span>
          </div>

          {dados.itens?.length > 0 && (
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

      {modalOpen && dados && (
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
              <Button variant="outline" onClick={() => setModalOpen(false)}>Cancelar</Button>
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
