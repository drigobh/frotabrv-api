import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ERRO_LEAFLET_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "components", "MapaFornecedores.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/components/MapaFornecedores.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "MapaFornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Remover o ícone customizado do <Marker> (para evitar o erro _leaflet_events)
    c = c.replace('icon={isFocado ? truckIcon : undefined}', '')

    # 2. Manter o ícone padrão do Leaflet (DefaultIcon já está definido no topo)
    if 'L.Marker.prototype.options.icon = DefaultIcon;' not in c:
        c = c.replace(
            'const truckIcon = L.divIcon({',
            'L.Marker.prototype.options.icon = DefaultIcon;\n\nconst truckIcon = L.divIcon({'
        )

    # 3. Remover a injeção de CSS do caminhão (se ainda existir)
    c = re.sub(r'if \(typeof document !== \'undefined\'\) \{[\s\S]*?document\.head\.appendChild\(style\);\n\}', '', c, count=1)

    # 4. Simplificar o popup para garantir que funcione
    padrao_popup = re.compile(r'<Popup>[\s\S]*?</Popup>')
    novo_popup = '''<Popup>
                      <div className="text-sm space-y-1 min-w-[200px]">
                        <p className="font-bold text-base border-b pb-1">{f.nome}</p>
                        <p><strong>Endereço:</strong> {f.endereco || "—"}</p>
                        <p><strong>Cidade:</strong> {f.cidade} - {f.estado}</p>
                        <p><strong>Contato:</strong> {f.contato || "—"}</p>
                        <p><strong>WhatsApp:</strong> {f.whatsapp || "—"}</p>
                      </div>
                    </Popup>'''
    
    if padrao_popup.search(c):
        c = padrao_popup.sub(lambda m: novo_popup, c, count=1)
        print("✅ Popup simplificado (sem erros).")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Componente corrigido (sem o ícone customizado).")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")
    