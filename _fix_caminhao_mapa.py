import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_CAMINHAO_MAPA_{agora}.zip")
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

    # 1. Criar o ícone customizado de caminhão vermelho piscando
    if 'const truckIcon' not in c:
        icone = '''
// Ícone customizado de caminhão vermelho piscando
const truckIcon = L.divIcon({
  className: 'custom-truck-icon',
  html: `<div class="truck-icon-container">
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="animate-pulse text-red-500 drop-shadow-[0_0_8px_rgba(239,68,68,0.9)]">
      <path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"></path>
      <path d="M15 18H9"></path>
      <path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"></path>
      <circle cx="17" cy="18" r="2"></circle>
      <circle cx="7" cy="18" r="2"></circle>
    </svg>
  </div>`,
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
});
'''
        # Adiciona o ícone após a definição do DefaultIcon
        c = c.replace(
            'L.Marker.prototype.options.icon = DefaultIcon;',
            'L.Marker.prototype.options.icon = DefaultIcon;\n' + icone
        )
        print("✅ Ícone de caminhão vermelho criado.")

    # 2. Adicionar o CSS para o ícone
    if '.truck-icon-container' not in c:
        css = '''
// CSS inline para o ícone (vai no index.css, mas vamos forçar aqui no componente)
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.innerHTML = `
    .custom-truck-icon {
      background: transparent;
      border: none;
    }
    .truck-icon-container {
      animation: pulse-truck 1s infinite;
    }
    @keyframes pulse-truck {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.7; transform: scale(1.1); }
    }
  `;
  document.head.appendChild(style);
}
'''
        # Adiciona antes da definição do componente
        idx = c.find('export function MapaFornecedores')
        if idx != -1:
            c = c[:idx] + css + '\n\n' + c[idx:]
            print("✅ CSS do ícone piscante adicionado.")

    # 3. Substituir o <Marker> para usar o truckIcon e o Popup simplificado
    padrao_marker = re.compile(r'<Marker key=\{f\.id\} position=\{\[[^\]]+\]\}>[\s\S]*?</Marker>', re.DOTALL)
    
    novo_marker = '''<Marker key={f.id} position={[coords[0] + offsetLat, coords[1] + offsetLon]} icon={truckIcon}>
                      <Popup>
                        <div className="text-sm space-y-1 min-w-[200px]">
                          <p className="font-bold text-base border-b pb-1">{f.nome}</p>
                          <p><strong>Endereço:</strong> {f.endereco || "—"}</p>
                          <p><strong>Cidade:</strong> {f.cidade} - {f.estado}</p>
                          <p><strong>Contato:</strong> {f.contato || "—"}</p>
                          <p><strong>WhatsApp:</strong> {f.whatsapp || "—"}</p>
                        </div>
                      </Popup>
                    </Marker>'''
    
    if padrao_marker.search(c):
        c = padrao_marker.sub(lambda m: novo_marker, c, count=1)
        print("✅ Marker atualizado com o ícone de caminhão e popup simplificado.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ MapaFornecedores.tsx atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")