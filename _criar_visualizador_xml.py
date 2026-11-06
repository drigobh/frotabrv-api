import os

path_visualizador = os.path.join(os.getcwd(), "frontend", "src", "pages", "VisualizadorXML.tsx")

conteudo = r'''import { useState } from "react";
import { FileText, Upload, X, Printer, Building2, User, Truck, DollarSign, Calendar, CheckCircle2, ShieldAlert } from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { brl } from "@/lib/format";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

// Função para extrair dados do XML (CT-e ou NF-e)
function parseXML(xmlString: string) {
  const parser = new DOMParser();
  const xmlDoc = parser.parseFromString(xmlString, "text/xml");

  // Verifica se é CT-e ou NF-e
  const isCTe = xmlDoc.getElementsByTagName("infCte").length > 0;
  const isNFe = xmlDoc.getElementsByTagName("infNFe").length > 0;

  if (!isCTe && !isNFe) {
    throw new Error("XML inválido. Deve ser CT-e ou NF-e.");
  }

  const getText = (tag: string, parent?: Element | Document) => {
    const el = (parent || xmlDoc).getElementsByTagName(tag)[0];
    return el ? el.textContent || "" : "";
  };

  const chave = xmlDoc.getElementsByTagName("infNFe")[0]?.getAttribute("Id")?.replace("NFe", "") || 
                xmlDoc.getElementsByTagName("infCte")[0]?.getAttribute("Id")?.replace("CTe", "") || "";

  if (isCTe) {
    const ide = xmlDoc.getElementsByTagName("ide")[0];
    const emit = xmlDoc.getElementsByTagName("emit")[0];
    const rem = xmlDoc.getElementsByTagName("rem")[0];
    const dest = xmlDoc.getElementsByTagName("dest")[0];
    const vPrest = xmlDoc.getElementsByTagName("vPrest")[0];

    return {
      tipo: "CT-e",
      chave,
      numero: getText("nCT"),
      serie: getText("serie"),
      dataEmissao: getText("dhEmi"),
      emitente: { nome: getText("xNome", emit), cnpj: getText("CNPJ", emit) },
      remetente: { nome: getText("xNome", rem), cnpj: getText("CNPJ", rem) },
      destinatario: { nome: getText("xNome", dest), cnpj: getText("CNPJ", dest) },
      valorTotal: parseFloat(getText("vTPrest", vPrest)) || 0,
      placas: getText("TRANSP_PLACAS").replace(/<\/?[^>]+(>|$)/g, ""),
    };
  } else {
    const ide = xmlDoc.getElementsByTagName("ide")[0];
    const emit = xmlDoc.getElementsByTagName("emit")[0];
    const dest = xmlDoc.getElementsByTagName("dest")[0];
    const total = xmlDoc.getElementsByTagName("total")[0];

    return {
      tipo: "NF-e",
      chave,
      numero: getText("nNF"),
      serie: getText("serie"),
      dataEmissao: getText("dhEmi"),
      emitente: { nome: getText("xNome", emit), cnpj: getText("CNPJ", emit) },
      remetente: null,
      destinatario: { nome: getText("xNome", dest), cnpj: getText("CNPJ", dest) },
      valorTotal: parseFloat(getText("vNF", total)) || 0,
      placas: "",
    };
  }
}

export default function VisualizadorXML() {
  const navigate = useNavigate();
  const [xmlString, setXmlString] = useState("");
  const [dados, setDados] = useState<any>(null);
  const [erro, setErro] = useState("");

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
      const res = parseXML(xml);
      setDados(res);
      toast.success(`${res.tipo} lida com sucesso!`);
    } catch (e: any) {
      setErro(e.message);
      toast.error(e.message);
    }
  };

  const imprimir = () => {
    if (!dados) return;
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      toast.error("Permita pop-ups para imprimir.");
      return;
    }

    const html = `
      <html>
        <head>
          <title>DANFE Simplificado - ${dados.numero}</title>
          <style>
            body { font-family: 'Segoe UI', sans-serif; padding: 20px; color: #333; }
            .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #000; padding-bottom: 10px; }
            .header h1 { margin: 0; font-size: 18px; }
            .header .logo { font-size: 24px; font-weight: bold; }
            .section { margin-top: 20px; }
            .section-title { background: #f1f5f9; padding: 5px 10px; font-weight: bold; font-size: 12px; border: 1px solid #ccc; margin-bottom: 0; }
            .section-content { padding: 10px; border: 1px solid #ccc; border-top: 0; font-size: 12px; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
            .field { margin-bottom: 5px; }
            .field-label { color: #64748b; font-size: 10px; }
            .field-value { font-weight: bold; }
            .total-box { margin-top: 20px; background: #000; color: #fff; padding: 10px; text-align: right; font-size: 18px; }
            .footer { margin-top: 30px; text-align: center; font-size: 10px; color: #94a3b8; }
          </style>
        </head>
        <body>
          <div class="header">
            <div>
              <div class="logo">BRAVUS FROTA</div>
              <div style="font-size:10px">Sistema de Gestão de Frotas</div>
            </div>
            <div style="text-align:right">
              <div style="font-size:12px;font-weight:bold">${dados.tipo}</div>
              <div style="font-size:12px">Nº ${dados.numero} - Série ${dados.serie}</div>
              <div style="font-size:10px">${new Date(dados.dataEmissao).toLocaleString('pt-BR')}</div>
            </div>
          </div>

          <div class="section">
            <div class="section-title">CHAVE DE ACESSO</div>
            <div class="section-content" style="font-family:monospace;font-size:14px;letter-spacing:1px">
              ${dados.chave.replace(/(\d{4})/g, '$1 ').trim()}
            </div>
          </div>

          <div class="section">
            <div class="section-title">EMITENTE</div>
            <div class="section-content">
              <div class="grid">
                <div class="field"><div class="field-label">Nome</div><div class="field-value">${dados.emitente.nome}</div></div>
                <div class="field"><div class="field-label">CNPJ</div><div class="field-value">${dados.emitente.cnpj}</div></div>
              </div>
            </div>
          </div>

          ${dados.remetente ? `
          <div class="section">
            <div class="section-title">REMETENTE</div>
            <div class="section-content">
              <div class="grid">
                <div class="field"><div class="field-label">Nome</div><div class="field-value">${dados.remetente.nome}</div></div>
                <div class="field"><div class="field-label">CNPJ</div><div class="field-value">${dados.remetente.cnpj}</div></div>
              </div>
            </div>
          </div>
          ` : ""}

          <div class="section">
            <div class="section-title">DESTINATÁRIO</div>
            <div class="section-content">
              <div class="grid">
                <div class="field"><div class="field-label">Nome</div><div class="field-value">${dados.destinatario.nome}</div></div>
                <div class="field"><div class="field-label">CNPJ</div><div class="field-value">${dados.destinatario.cnpj}</div></div>
              </div>
            </div>
          </div>

          ${dados.placas ? `
          <div class="section">
            <div class="section-title">VEÍCULOS</div>
            <div class="section-content" style="font-family:monospace;font-size:14px">
              ${dados.placas}
            </div>
          </div>
          ` : ""}

          <div class="total-box">
            VALOR TOTAL: R$ ${dados.valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
          </div>

          <div class="footer">
            Documento gerado pelo sistema Bravus Frota em ${new Date().toLocaleString('pt-BR')}
          </div>
        </body>
      </html>
    `;

    printWindow.document.write(html);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
      printWindow.print();
      printWindow.close();
    }, 500);
  };

  return (
    <div>
      <PageHeader
        eyebrow="Gestão"
        title="Visualizador de XML"
        description="Leia o XML do CT-e ou NF-e, veja os dados e imprima o DANFE simplificado."
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
          <div className="border-2 border-dashed border-slate-700 rounded-xl p-8 text-center hover:bg-slate-800/50 transition-colors cursor-pointer" onClick={() => document.getElementById("xml-input")?.click()}>
            <input id="xml-input" type="file" accept=".xml" onChange={handleFileUpload} className="hidden" />
            <FileText className="size-8 mx-auto text-slate-400 mb-2" />
            <p className="text-sm font-medium text-slate-200">Selecione o arquivo XML</p>
            <p className="text-xs text-slate-500 mt-1">CT-e ou NF-e</p>
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
            <Button onClick={imprimir} className="bg-sky-600 hover:bg-sky-500">
              <Printer className="size-4 mr-2" /> Imprimir DANFE
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <p className="text-[10px] uppercase text-slate-500 mb-1">Chave de Acesso</p>
                <p className="font-mono text-xs text-slate-200 break-all">{dados.chave}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div><p className="text-[10px] uppercase text-slate-500">Número</p><p className="text-sm font-bold text-slate-200">{dados.numero}</p></div>
                <div><p className="text-[10px] uppercase text-slate-500">Série</p><p className="text-sm font-bold text-slate-200">{dados.serie}</p></div>
              </div>
              <div>
                <p className="text-[10px] uppercase text-slate-500">Data de Emissão</p>
                <p className="text-sm text-slate-200">{new Date(dados.dataEmissao).toLocaleString('pt-BR')}</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <p className="text-[10px] uppercase text-slate-500 flex items-center gap-1"><Building2 className="size-3" /> Emitente</p>
                <p className="text-sm font-bold text-slate-200">{dados.emitente.nome}</p>
                <p className="text-xs text-slate-400">{dados.emitente.cnpj}</p>
              </div>
              {dados.remetente && (
                <div>
                  <p className="text-[10px] uppercase text-slate-500 flex items-center gap-1"><Truck className="size-3" /> Remetente</p>
                  <p className="text-sm font-bold text-slate-200">{dados.remetente.nome}</p>
                  <p className="text-xs text-slate-400">{dados.remetente.cnpj}</p>
                </div>
              )}
              <div>
                <p className="text-[10px] uppercase text-slate-500 flex items-center gap-1"><User className="size-3" /> Destinatário</p>
                <p className="text-sm font-bold text-slate-200">{dados.destinatario.nome}</p>
                <p className="text-xs text-slate-400">{dados.destinatario.cnpj}</p>
              </div>
              {dados.placas && (
                <div>
                  <p className="text-[10px] uppercase text-slate-500">Veículos</p>
                  <p className="text-sm font-mono text-sky-300">{dados.placas}</p>
                </div>
              )}
            </div>
          </div>

          <div className="mt-6 p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex justify-between items-center">
            <span className="text-sm font-medium text-emerald-400">Valor Total</span>
            <span className="text-2xl font-bold text-emerald-400 font-mono">{brl(dados.valorTotal)}</span>
          </div>
        </div>
      )}
    </div>
  );
}
'''

with open(path_visualizador, "w", encoding="utf-8") as f:
    f.write(conteudo)
print("✅ Página VisualizadorXML.tsx criada.")

# Adicionar a rota e o botão na tela do Financeiro
path_fin = os.path.join(os.getcwd(), "frontend", "src", "pages", "Financeiro.tsx")
with open(path_fin, "r", encoding="utf-8") as f:
    f_c = f.read()

if "VisualizadorXML" not in f_c:
    f_c = f_c.replace(
        'import { Plus, Search, X, Check, CheckCircle2, Truck, Building2, FileText, Calendar, Filter } from "lucide-react";',
        'import { Plus, Search, X, Check, CheckCircle2, Truck, Building2, FileText, Calendar, Filter, FileSearch } from "lucide-react";'
    )
    f_c = f_c.replace(
        '<Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9">',
        '<Button onClick={() => navigate("/financeiro/xml")} variant="outline" className="border-purple-500/40 text-purple-400 hover:bg-purple-500/10 h-9 mr-2"><FileSearch className="size-4 mr-2" /> Visualizar XML</Button>\n            <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9">'
    )
    if "useNavigate" not in f_c:
        f_c = f_c.replace(
            'import { useState } from "react";',
            'import { useState } from "react";\nimport { useNavigate } from "react-router-dom";'
        )
        f_c = f_c.replace(
            'export default function Financeiro() {',
            'export default function Financeiro() {\n  const navigate = useNavigate();'
        )
    with open(path_fin, "w", encoding="utf-8") as f:
        f.write(f_c)
    print("✅ Botão 'Visualizar XML' (roxo) adicionado ao Financeiro.")

# Adicionar a rota no App.tsx
path_app = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")
with open(path_app, "r", encoding="utf-8") as f:
    a_c = f.read()

if "VisualizadorXML" not in a_c:
    a_c = a_c.replace(
        'import Financeiro from "@/pages/Financeiro";',
        'import Financeiro from "@/pages/Financeiro";\nimport VisualizadorXML from "@/pages/VisualizadorXML";'
    )
    a_c = a_c.replace(
        '<Route path="/financeiro" element={<Financeiro />} />',
        '<Route path="/financeiro" element={<Financeiro />} />\n            <Route path="/financeiro/xml" element={<VisualizadorXML />} />'
    )
    with open(path_app, "w", encoding="utf-8") as f:
        f.write(a_c)
    print("✅ Rota /financeiro/xml adicionada ao App.tsx.")

print("✅ Tudo pronto! Faça o git push.")