import os
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_rapido_tela_base_{agora}.zip"
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print("📦 Criando Backup Rápido...")
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        pasta_front = os.path.join(raiz, "frontend", "src")
        for root, dirs, files in os.walk(pasta_front):
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', 'build']]
            for file in files:
                caminho_completo = os.path.join(root, file)
                caminho_relativo = os.path.relpath(caminho_completo, raiz)
                try:
                    zipf.write(caminho_completo, caminho_relativo)
                except Exception:
                    pass

def criar_componente_card(raiz):
    # Cria o componente Card se não existir
    pasta_ui = os.path.join(raiz, "frontend", "src", "components", "ui")
    os.makedirs(pasta_ui, exist_ok=True)
    caminho_card = os.path.join(pasta_ui, "card.tsx")
    
    if not os.path.exists(caminho_card):
        codigo_card = '''import * as React from "react"
import { cn } from "@/lib/utils"

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-xl border bg-card text-card-foreground shadow",
      className
    )}
    {...props}
  />
))
Card.displayName = "Card"

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
'''
        with open(caminho_card, 'w', encoding='utf-8') as f:
            f.write(codigo_card)
        print("✅ Componente Card criado.")

def recriar_tela_base(raiz):
    pasta_pages = os.path.join(raiz, "frontend", "src", "pages")
    caminho_base = os.path.join(pasta_pages, "Base.tsx")
    
    codigo_base = '''import { useState } from "react";
import { Database, Trash2, AlertTriangle } from "lucide-react";
import { toast } from "sonner";
import { apiPost } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const COLECOES = [
  { id: "veiculos", nome: "Veículos" },
  { id: "carretas", nome: "Carretas" },
  { id: "motoristas", nome: "Motoristas" },
  { id: "acoplamentos", nome: "Acoplamentos" },
  { id: "abastecimentos", nome: "Abastecimentos" },
];

export default function Base() {
  const [open, setOpen] = useState(false);
  const [colecaoAlvo, setColecaoAlvo] = useState<string | null>(null);
  const [confirmacao, setConfirmacao] = useState("");
  const [pending, setPending] = useState(false);

  const abrirDialogo = (id: string) => {
    setColecaoAlvo(id);
    setConfirmacao("");
    setOpen(true);
  };

  const limparBase = async () => {
    if (confirmacao !== "LIMPAR") {
      toast.error("Digite a palavra LIMPAR para confirmar.");
      return;
    }
    
    setPending(true);
    try {
      await apiPost(`/admin/limpar-base?colecao=${colecaoAlvo}`);
      toast.success(`Base de ${colecaoAlvo} limpa com sucesso! Backups gerados.`);
      setOpen(false);
    } catch (error: any) {
      toast.error(error.message || "Erro ao limpar a base.");
    } finally {
      setPending(false);
    }
  };

  return (
    <div>
      <PageHeader
        eyebrow="Administração"
        title="Limpeza de Base"
        description="Apague os dados de tabelas específicas. O sistema gera um backup automático antes de qualquer exclusão."
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {COLECOES.map((c) => (
          <div key={c.id} className="glass rounded-xl p-6 border border-slate-800 bg-[#0F172A]">
            <div className="flex items-center gap-2 text-slate-200 mb-2">
              <Database className="size-5 text-sky-400" />
              <h3 className="text-lg font-semibold">{c.nome}</h3>
            </div>
            <p className="text-sm text-slate-400 mb-4">Apaga todos os registros da tabela.</p>
            <Button variant="destructive" className="w-full" onClick={() => abrirDialogo(c.id)}>
              <Trash2 className="size-4 mr-2" /> Limpar {c.nome}
            </Button>
          </div>
        ))}
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-400">
              <AlertTriangle className="size-5" /> Atenção!
            </DialogTitle>
            <DialogDescription>
              Você está prestes a apagar <strong>TODOS</strong> os dados de <strong>{colecaoAlvo}</strong>.
              Um backup será gerado automaticamente, mas esta ação não pode ser desfeita pelo sistema.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-2 py-4">
            <Label>Digite <strong className="text-red-400">LIMPAR</strong> para confirmar:</Label>
            <Input value={confirmacao} onChange={(e) => setConfirmacao(e.target.value)} placeholder="LIMPAR" />
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setOpen(false)}>Cancelar</Button>
            <Button variant="destructive" disabled={confirmacao !== "LIMPAR" || pending} onClick={limparBase}>
              {pending ? "Limpando..." : "Confirmar Exclusão"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
'''
    
    with open(caminho_base, 'w', encoding='utf-8') as f:
        f.write(codigo_base)
    print("✅ Página Base.tsx recriada usando HTML puro.")

if __name__ == "__main__":
    raiz = os.getcwd()
    print("🤖 Iniciando Correção da Tela Base...")
    criar_backup_rapido(raiz)
    criar_componente_card(raiz)
    recriar_tela_base(raiz)
    print("\n🚀 Concluído! Reinicie o Vite para testar.")