import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ZOOM_EXATO_{agora}.zip")
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

    # 1. Adicionar estado para guardar a coordenada exata do fornecedor selecionado
    if 'coordsFocado' not in c:
        c = c.replace(
            'const [fornecedorFocado, setFornecedorFocado] = useState<any>(null);',
            'const [fornecedorFocado, setFornecedorFocado] = useState<any>(null);\n  const [coordsFocado, setCoordsFocado] = useState<[number, number] | null>(null);'
        )
        print("✅ Estado 'coordsFocado' adicionado.")

    # 2. Criar a função de focar no fornecedor (chama a API de geocode)
    if 'const focarFornecedor =' not in c:
        funcao = '''
  const focarFornecedor = async (f: any) => {
    setFornecedorFocado(f);
    
    // Se o fornecedor já tiver lat/long salvo, usa direto
    if (f.latitude && f.longitude) {
      setCoordsFocado([f.latitude, f.longitude]);
      return;
    }

    // Se não, busca pelo endereço via API
    try {
      const res = await fetch(`/api/empresa/geocode?endereco=${encodeURIComponent(`${f.endereco}, ${f.cidade}, ${f.estado}`)}`);
      const data = await res.json();
      
      if (data.lat && data.lon) {
        setCoordsFocado([data.lat, data.lon]);
      } else {
        // Fallback: busca cidade
        const resCidade = await fetch(`/api/empresa/geocode?endereco=${encodeURIComponent(`${f.cidade}, ${f.estado}`)}`);
        const dataCidade = await resCidade.json();
        if (dataCidade.lat && dataCidade.lon) setCoordsFocado([dataCidade.lat, dataCidade.lon]);
      }
    } catch (e) {
      console.error("Erro ao geocodificar:", e);
    }
  };
'''
        # Adiciona antes do if (!open) return null;
        idx = c.find('if (!open) return null;')
        if idx != -1:
            c = c[:idx] + funcao + c[idx:]
            print("✅ Função 'focarFornecedor' criada.")

    # 3. Atualizar o botão da lista para usar a nova função
    c = c.replace(
        'onClick={() => setFornecedorFocado(f)}',
        'onClick={() => focarFornecedor(f)}'
    )
    print("✅ Botão da lista atualizado.")

    # 4. Atualizar a lógica do centro do mapa para usar 'coordsFocado'
    if 'coordsFocado ? coordsFocado' not in c:
        # Substitui a lógica antiga que usava ESTADOS_COORDS
        c = c.replace(
            '''if (fornecedorFocado && ESTADOS_COORDS[fornecedorFocado.estado]) {
    center = ESTADOS_COORDS[fornecedorFocado.estado];
    zoom = 10;
  } else if (estadoSelecionado && ESTADOS_COORDS[estadoSelecionado]) {
    center = ESTADOS_COORDS[estadoSelecionado];
    zoom = 6;
  }''',
            '''if (coordsFocado) {
    center = coordsFocado;
    zoom = 16; // Zoom alto no endereço exato
  } else if (estadoSelecionado && ESTADOS_COORDS[estadoSelecionado]) {
    center = ESTADOS_COORDS[estadoSelecionado];
    zoom = 6;
  }'''
        )
        print("✅ Lógica do centro do mapa atualizada para usar coordsFocado.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ MapaFornecedores.tsx atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")