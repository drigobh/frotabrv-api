import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { apiGet } from "@/lib/api";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";

export default function ImprimirDanfe() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
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
          // Parse do XML (reutilizando lógica)
          const parser = new DOMParser();
          const xmlDoc = parser.parseFromString(res.xml, "text/xml");
          const isNFe = xmlDoc.getElementsByTagName("infNFe").length > 0;
          
          if (isNFe) {
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

            const itens: any[] = [];
            const dets = xmlDoc.getElementsByTagName("det");
            for (let i = 0; i < dets.length; i++) {
              const det = dets[i];
              const prod = det.getElementsByTagName("prod")[0];
              itens.push({
                codigo: get("cProd", prod),
                descricao: get("xProd", prod),
                unidade: get("uCom", prod),
                quantidade: parseFloat(get("qCom", prod)) || 0,
                valorUnit: parseFloat(get("vUnCom", prod)) || 0,
                valorTotal: parseFloat(get("vProd", prod)) || 0,
              });
            }

            setXmlData({
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
              valorTotal: parseFloat(get("vNF", icmsTot || total)) || parseFloat(get("vProd", icmsTot || total)) || 0,
              itens
            });
          }
        }
      })
      .catch((err) => {
        setErro(err.message || "Erro ao carregar XML");
      });
  }, [searchParams]);

  useEffect(() => {
    if (xmlData) {
      setTimeout(() => { window.print(); }, 800);
    }
  }, [xmlData]);

  if (erro) {
    return <div className="p-8 text-rose-500">{erro}</div>;
  }

  if (!xmlData) {
    return <div className="p-8 text-white">Carregando DANFE...</div>;
  }

  const d = xmlData;
  const chaveFormatada = d.chave.match(/.{1,4}/g)?.join(" ") || d.chave;

  return (
    <div className="bg-white text-black min-h-screen print:m-0">
      <style>{`
        @media print {
          @page { size: A4 landscape; margin: 5mm; }
          body { -webkit-print-color-adjust: exact; }
          .no-print { display: none !important; }
        }
      `}</style>

      <div className="no-print p-4 bg-slate-900 flex gap-2">
        <Button onClick={() => window.print()} className="bg-purple-600">Imprimir novamente</Button>
        <Button variant="outline" onClick={() => window.close()}>Fechar</Button>
      </div>

      <div className="p-4">
        <div className="danfe border border-black p-2" style={{ fontFamily: "Arial, sans-serif", fontSize: "7pt" }}>
          {/* Cabeçalho */}
          <div style={{ display: "flex", borderBottom: "1px solid #000", paddingBottom: "1mm", marginBottom: "1mm" }}>
            <div style={{ width: "30%", borderRight: "1px solid #000", paddingRight: "2mm" }}>
              <div style={{ fontSize: "14pt", fontWeight: "bold" }}>{d.emitente.nome}</div>
              <div style={{ fontSize: "6pt" }}>{d.emitente.endereco}</div>
              <div style={{ fontSize: "6pt" }}>CNPJ: {d.emitente.cnpj}</div>
            </div>
            <div style={{ width: "40%", textAlign: "center", borderRight: "1px solid #000", padding: "0 2mm" }}>
              <div style={{ fontSize: "10pt", fontWeight: "bold", margin: "1mm 0" }}>DANFE</div>
              <div style={{ fontSize: "5.5pt" }}>Documento Auxiliar da Nota Fiscal Eletrônica</div>
              <div style={{ fontSize: "7pt" }}>Nº {d.numero} &nbsp; Série {d.serie}</div>
              <div style={{ textAlign: "center", margin: "1mm 0" }}><svg id="barcode"></svg></div>
              <div style={{ fontFamily: "monospace", fontSize: "8pt", letterSpacing: "1px" }}>{chaveFormatada}</div>
            </div>
            <div style={{ width: "30%", paddingLeft: "2mm", fontSize: "6pt" }}>
              <div><b>Natureza:</b> {d.natOp || "—"}</div>
              <div><b>Data Emissão:</b> {new Date(d.dataEmissao).toLocaleString("pt-BR")}</div>
            </div>
          </div>

          {/* Destinatário */}
          <div style={{ border: "1px solid #000", marginTop: "1mm" }}>
            <div style={{ background: "#f0f0f0", fontWeight: "bold", padding: "0.5mm 1mm", fontSize: "6.5pt", borderBottom: "1px solid #000" }}>DESTINATÁRIO / REMETENTE</div>
            <div style={{ padding: "1mm" }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1mm" }}>
                <div><div style={{ fontSize: "5.5pt", color: "#666" }}>Nome / Razão Social</div><div style={{ fontSize: "7pt", fontWeight: "bold" }}>{d.destinatario.nome}</div></div>
                <div><div style={{ fontSize: "5.5pt", color: "#666" }}>CNPJ / CPF</div><div style={{ fontSize: "7pt", fontWeight: "bold" }}>{d.destinatario.cnpj}</div></div>
              </div>
            </div>
          </div>

          {/* Produtos */}
          <div style={{ border: "1px solid #000", marginTop: "1mm" }}>
            <div style={{ background: "#f0f0f0", fontWeight: "bold", padding: "0.5mm 1mm", fontSize: "6.5pt", borderBottom: "1px solid #000" }}>DADOS DOS PRODUTOS / SERVIÇOS</div>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "6pt" }}>
              <thead><tr>{["Cód", "Descrição", "Un", "Qtd", "Vl Unit", "Vl Total"].map(h => <th key={h} style={{ background: "#f0f0f0", border: "1px solid #000", padding: "0.5mm" }}>{h}</th>)}</tr></thead>
              <tbody>
                {d.itens.map((it: any, i: number) => (
                  <tr key={i}>
                    <td style={{ border: "1px solid #000", padding: "0.5mm", textAlign: "center" }}>{it.codigo}</td>
                    <td style={{ border: "1px solid #000", padding: "0.5mm" }}>{it.descricao}</td>
                    <td style={{ border: "1px solid #000", padding: "0.5mm", textAlign: "center" }}>{it.unidade}</td>
                    <td style={{ border: "1px solid #000", padding: "0.5mm", textAlign: "center" }}>{it.quantidade}</td>
                    <td style={{ border: "1px solid #000", padding: "0.5mm", textAlign: "center" }}>{it.valorUnit.toFixed(2)}</td>
                    <td style={{ border: "1px solid #000", padding: "0.5mm", textAlign: "center" }}>{it.valorTotal.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Total */}
          <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "1mm" }}>
            <div style={{ border: "1px solid #000", padding: "1mm 3mm", fontSize: "8pt", fontWeight: "bold" }}>VALOR TOTAL: R$ {d.valorTotal.toFixed(2)}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
