import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { MessageCircle, CheckCircle2, XCircle, Send, RefreshCw } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

export default function WhatsAppConfig() {
  const [telefoneTeste, setTelefoneTeste] = useState("");

  const { data: status, refetch: refetchStatus } = useQuery({
    queryKey: ["whatsapp-status"],
    queryFn: () => apiGet<any>("/whatsapp/status"),
    refetchInterval: 30000
  });

  const { data: logs = [] } = useQuery({
    queryKey: ["whatsapp-logs"],
    queryFn: () => apiGet<any[]>("/whatsapp/logs")
  });

  const testar = useMutation({
    mutationFn: (payload: any) => apiPost<any>("/whatsapp/testar", payload),
    onSuccess: (data) => {
      if (data.sucesso) toast.success("Mensagem enviada!");
      else toast.error("Erro: " + (data.erro || "Verifique as credenciais."));
    },
    onError: (e: any) => toast.error("Erro: " + e.message)
  });

  const handleTestar = () => {
    if (!telefoneTeste) return toast.error("Digite um telefone.");
    testar.mutate({ telefone: telefoneTeste });
  };

  const conectado = status?.conectado;

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Administração"
        title="WhatsApp Automático"
        description="Gerencie a integração de envio automático via WAHA (open-source)."
        actions={<Button onClick={() => refetchStatus()} variant="outline" className="border-slate-700 text-slate-300"><RefreshCw className="size-4 mr-2"/> Atualizar</Button>}
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className={`glass p-4 rounded-xl border ${conectado ? 'border-emerald-500/30' : 'border-rose-500/30'}`}>
          <div className="flex items-center gap-2 mb-2">
            {conectado ? <CheckCircle2 className="size-5 text-emerald-400" /> : <XCircle className="size-5 text-rose-400" />}
            <p className="text-[11px] uppercase text-slate-400">Status</p>
          </div>
          <p className={`text-lg font-bold ${conectado ? 'text-emerald-400' : 'text-rose-400'}`}>{conectado ? "Conectado" : "Desconectado"}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <div className="flex items-center gap-2 mb-2"><MessageCircle className="size-5 text-sky-400" /><p className="text-[11px] uppercase text-slate-400">Total Envios</p></div>
          <p className="text-lg font-bold text-sky-400">{logs.length}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <div className="flex items-center gap-2 mb-2"><p className="text-[11px] uppercase text-slate-400">Detalhes</p></div>
          <p className="text-sm text-slate-300">{status?.status || "Sem dados"}</p>
        </div>
      </div>

      {status?.erro && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400 text-sm">
          <b>Erro:</b> {status.erro}
          <br/>
          <span className="text-xs opacity-70">Tentando conectar em: {status.url_conectada || "Desconhecida"}</span>
        </div>
      )}

      <div className="glass p-6 rounded-2xl border border-slate-800">
        <h3 className="text-sm font-bold text-slate-100 mb-4 flex items-center gap-2"><Send className="size-4 text-sky-400"/> Testar Envio</h3>
        <div className="flex gap-3">
          <div className="flex-1">
            <Label className="text-xs text-slate-400">Telefone (com DDI)</Label>
            <Input placeholder="Ex: 5531999999999" value={telefoneTeste} onChange={e => setTelefoneTeste(e.target.value)} className="bg-slate-950 mt-1" />
          </div>
          <Button onClick={handleTestar} disabled={testar.isPending} className="bg-emerald-600 hover:bg-emerald-500 mt-5">
            {testar.isPending ? "Enviando..." : "Enviar Teste"}
          </Button>
        </div>
      </div>

      <div className="glass rounded-2xl overflow-hidden border border-slate-800">
        <div className="bg-slate-800/50 px-5 py-3 border-b border-slate-700"><h3 className="text-sm font-bold text-slate-200">Histórico</h3></div>
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900/50"><tr className="text-[11px] uppercase text-slate-400"><th className="px-5 py-3">Data</th><th className="px-3 py-3">Telefone</th><th className="px-3 py-3">Status</th></tr></thead>
          <tbody className="divide-y divide-slate-800">
            {logs.length === 0 ? <tr><td colSpan={3} className="p-8 text-center text-slate-400">Nenhum envio registrado.</td></tr> : logs.map((log: any) => (
              <tr key={log.id}>
                <td className="px-5 py-3 text-slate-300 text-xs">{new Date(log.data).toLocaleString("pt-BR")}</td>
                <td className="px-3 py-3 text-slate-200 font-mono text-xs">{log.telefone}</td>
                <td className="px-3 py-3">{log.sucesso ? <span className="text-emerald-400 text-xs font-bold">Enviado</span> : <span className="text-rose-400 text-xs font-bold">Falhou</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
