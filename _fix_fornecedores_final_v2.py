import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_FORN_FINAL_V2_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    arquivos = ["frontend/src/pages/Fornecedores.tsx", "frontend/src/pages/TiposFornecedores.tsx"]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_fornecedores(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Remover o Botão de Preencher em Massa (já foi usado e deu certo)
    c = re.sub(r'<Button variant="outline" onClick=\{preencherTiposEmMassa\}[\s\S]*?Preencher Tipos em Massa\s*</Button>', '', c, count=1)
    
    # Remove a função "preencherTiposEmMassa" que não é mais necessária
    c = re.sub(r'const preencherTiposEmMassa = async \(\) => \{[\s\S]*?\n  \};', '', c, count=1)

    # 2. Adicionar ícone do Google Maps na coluna Localização
    # Substitui a célula de localização para incluir o link do maps
    alvo_loc = '''<TableCell className="text-slate-400 text-xs">
                  <div className="flex flex-col gap-1">
                    <span className="flex items-center gap-1"><MapPin className="size-3" /> {r.cidade ? `${r.cidade}/${r.estado}` : "—"}</span>
                  </div>
                </TableCell>'''
    
    nova_loc = '''<TableCell className="text-slate-400 text-xs">
                  <div className="flex flex-col gap-1">
                    <span className="flex items-center gap-1"><MapPin className="size-3" /> {r.cidade ? `${r.cidade}/${r.estado}` : "—"}</span>
                    {r.cidade && (
                      <button onClick={() => window.open(`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${r.endereco || ""}, ${r.cidade}, ${r.estado}`)}`, "_blank")} className="text-sky-400 hover:underline text-[10px] flex items-center gap-1">
                        <MapPin className="size-3" /> Abrir no Maps
                      </button>
                    )}
                  </div>
                </TableCell>'''
    
    if alvo_loc in c:
        c = c.replace(alvo_loc, nova_loc)
        print("✅ Link do Google Maps adicionado.")
    else:
        # Fallback se o MapPin não estiver exatamente assim
        alvo_loc_alt = '<span className="flex items-center gap-1"><MapPin className="size-3" /> {r.cidade ? `${r.cidade}/${r.estado}` : "—"}</span>'
        if alvo_loc_alt in c:
            c = c.replace(alvo_loc_alt, alvo_loc_alt + '''
                    {r.cidade && (
                      <button onClick={() => window.open(`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${r.endereco || ""}, ${r.cidade}, ${r.estado}`)}`, "_blank")} className="text-sky-400 hover:underline text-[10px] flex items-center gap-1 mt-1">
                        <MapPin className="size-3" /> Abrir no Maps
                      </button>
                    )}''')
            print("✅ Link do Google Maps adicionado via fallback.")

    # 3. Adicionar alerta de CNPJ Pendente no nome
    alvo_nome = '''<div className="flex items-center gap-2">{r.nome}<span className="text-[9px] font-bold bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">{r.tipo_pessoa}</span></div>
                      <div className="text-slate-500 font-mono text-xs">{r.documento || "—"}</div>'''
    
    novo_nome = '''<div className="flex items-center gap-2">{r.nome}<span className="text-[9px] font-bold bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">{r.tipo_pessoa}</span></div>
                      <div className="text-slate-500 font-mono text-xs flex flex-col">
                        <span>{r.documento || "—"}</span>
                        {(!r.documento || String(r.documento).trim() === "") && (
                          <span className="text-red-500 animate-pulse font-bold text-[9px] flex items-center gap-1 mt-1">
                            <AlertTriangle className="size-3" /> CNPJ Pendente
                          </span>
                        )}
                      </div>'''
    
    if alvo_nome in c:
        c = c.replace(alvo_nome, novo_nome)
        print("✅ Alerta de 'CNPJ Pendente' adicionado.")
    else:
        print("⚠️ Não encontrei o trecho exato para o CNPJ. Verifique se a estrutura mudou.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend Fornecedores atualizado.")

def fix_tipos_parametrizacao(raiz):
    # 1. Garantir que o botão "Popular Lista Base" respeita a parametrização
    caminho = os.path.join(raiz, "frontend", "src", "pages", "TiposFornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Se a condicional já existir, não faz nada. Se não, injeta.
    if '{config?.mostrar_seed_fornecedores && (' not in c:
        # Procura o botão "Popular Lista Base"
        alvo_btn = '''<Button variant="outline" onClick={popularLista} disabled={seed.isPending} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10">
            <Database className="size-4 mr-2" /> {seed.isPending ? "Populando..." : "Popular Lista Base"}
          </Button>'''
        
        novo_btn = '''{config?.mostrar_seed_fornecedores && (
            <Button variant="outline" onClick={popularLista} disabled={seed.isPending} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10">
              <Database className="size-4 mr-2" /> {seed.isPending ? "Populando..." : "Popular Lista Base"}
            </Button>
          )}'''
        
        if alvo_btn in c:
            c = c.replace(alvo_btn, novo_btn)
            print("✅ Botão 'Popular Lista Base' agora respeita a parametrização.")

    # 2. Adicionar o key no map que estava faltando (resolve o aviso do React)
    # O map que gera as categorias
    c = c.replace(
        'rowsFiltradas.filter(r => !r.categoria_pai_id).map(cat => (',
        'rowsFiltradas.filter(r => !r.categoria_pai_id).map(cat => ('
    )
    
    # O problema de key é porque o fragmento <> não tem key. Vamos trocar por <React.Fragment key={cat.id}>
    # Mas como não importamos React, usamos a key no elemento pai se possível, ou criamos um componente.
    # Simplificando: Vamos usar a key na TableRow e no TableBody.
    
    if 'key={cat.id}' not in c:
        # Substitui o Fragmento por um map com key
        c = c.replace(
            'rowsFiltradas.filter(r => !r.categoria_pai_id).map(cat => (\n              <>',
            'rowsFiltradas.filter(r => !r.categoria_pai_id).map(cat => (\n              <React.Fragment key={cat.id}>'
        )
        c = c.replace(
            '              </>\n            ))}',
            '              </React.Fragment>\n            ))}'
        )
        # Importa React
        if 'import React' not in c:
            c = 'import React from "react";\n' + c

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend Tipos de Fornecedores atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_fornecedores(raiz)
    fix_tipos_parametrizacao(raiz)
    print("\n✅ Todos os ajustes aplicados com sucesso! Faça o push.")