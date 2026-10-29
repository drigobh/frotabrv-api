import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_DEFAULT_ICON_{agora}.zip")
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

    # 1. Definir o DefaultIcon se não existir
    if 'const DefaultIcon = L.icon' not in c and 'let DefaultIcon = L.icon' not in c:
        # Adiciona a definição do DefaultIcon logo após os imports do Leaflet
        c = c.replace(
            'import L from "leaflet";',
            '''import L from "leaflet";
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;'''
        )
        print("✅ DefaultIcon definido e aplicado.")

    # 2. Remover a referência ao truckIcon (se ainda existir) para evitar erros
    c = c.replace('icon={isFocado ? truckIcon : undefined}', '')
    
    # 3. Remover a definição do truckIcon (se existir)
    import re
    c = re.sub(r'const truckIcon = L\.divIcon\(\{[\s\S]*?\}\);', '', c)

    # 4. Garantir que a definição do DefaultIcon não está duplicada
    if c.count('L.Marker.prototype.options.icon = DefaultIcon;') > 1:
        # Remove as duplicatas, mantendo apenas a primeira
        primeiro = c.find('L.Marker.prototype.options.icon = DefaultIcon;')
        c = c[:primeiro + len('L.Marker.prototype.options.icon = DefaultIcon;')] + c[primeiro + len('L.Marker.prototype.options.icon = DefaultIcon;'):].replace('L.Marker.prototype.options.icon = DefaultIcon;', '')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Componente corrigido (DefaultIcon garantido).")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")