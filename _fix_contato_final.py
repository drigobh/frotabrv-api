import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_CONTATO_FINAL_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Fornecedores.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar contato e whatsapp no estado do form (se não existirem)
    if 'contato:' not in c:
        c = c.replace('telefone: "", email: "",', 'telefone: "", contato: "", whatsapp: "", email: "",')
        c = c.replace('telefone: r.telefone || "",', 'telefone: r.telefone || "", contato: r.contato || "", whatsapp: r.whatsapp || "",')
        print("✅ Campos contato e whatsapp adicionados ao estado do form.")

    # 2. Adicionar os campos no modal (se não existirem)
    if 'WhatsApp' not in c:
        # Procura o campo E-mail no modal e insere os dois novos campos depois dele
        alvo = '''<div className="grid gap-1"><Label className="text-xs">E-mail</Label><Input type="email" value={form.email} onChange={(e) => setForm(s => ({ ...s, email: e.target.value }))} className="h-9" /></div>'''
        novo = '''<div className="grid gap-1"><Label className="text-xs">E-mail</Label><Input type="email" value={form.email} onChange={(e) => setForm(s => ({ ...s, email: e.target.value }))} className="h-9" /></div>
            
            <div className="grid gap-1">
              <Label className="text-xs">Contato</Label>
              <Input value={form.contato} onChange={(e) => setForm(s => ({ ...s, contato: e.target.value }))} placeholder="Nome do contato" className="h-9" />
            </div>
            <div className="grid gap-1">
              <Label className="text-xs flex items-center gap-1">
                <MessageCircle className="size-3 text-emerald-500" /> WhatsApp
              </Label>
              <Input value={form.whatsapp} onChange={(e) => setForm(s => ({ ...s, whatsapp: e.target.value }))} placeholder="(00) 00000-0000" className="h-9" />
            </div>'''
        if alvo in c:
            c = c.replace(alvo, novo)
            print("✅ Campos Contato e WhatsApp adicionados ao modal.")

    # 3. Adicionar a célula de contato no grid (se não existir)
    if '{r.contato' not in c:
        # Procura a célula de Localização e insere a de contato depois
        padrao = re.compile(r'(<TableCell className="text-xs text-slate-400">\s*<div className="flex flex-col gap-1">[\s\S]*?\{r\.cidade[\s\S]*?</TableCell>)', re.DOTALL)
        match = padrao.search(c)
        if match:
            nova_cell = match.group(1) + '''
                <TableCell className="text-xs text-slate-400 text-center">
                  <div className="flex flex-col items-center justify-center">
                    <span className="font-medium text-slate-300">{r.contato || "—"}</span>
                    {r.whatsapp && (
                      <a href={`https://wa.me/55${r.whatsapp.replace(/\\D/g, '')}`} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-emerald-400 hover:text-emerald-300 mt-1">
                        <MessageCircle className="size-4 animate-pulse" />
                        <span className="text-[10px]">{r.whatsapp}</span>
                      </a>
                    )}
                  </div>
                </TableCell>'''
            c = c.replace(match.group(1), nova_cell)
            print("✅ Célula de Contato adicionada ao grid.")

    # 4. Garantir o import do ícone MessageCircle
    if 'MessageCircle' not in c.split('lucide-react')[0]:
        c = c.replace('import { Building2,', 'import { MessageCircle, Building2,')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)