import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MAPA_DESTRAVAR_{agora}.zip")
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

    # 1. Limpar o coordsFocado ao mudar o estado
    if 'setCoordsFocado(null);' not in c:
        # Adiciona a limpeza no botão "Todos" e nos estados
        c = c.replace(
            'onClick={() => setEstadoSelecionado("")}',
            'onClick={() => { setEstadoSelecionado(""); setCoordsFocado(null); setFornecedorFocado(null); }}'
        )
        c = c.replace(
            'onClick={() => setEstadoSelecionado(uf)}',
            'onClick={() => { setEstadoSelecionado(uf); setCoordsFocado(null); setFornecedorFocado(null); }}'
        )
        print("✅ Limpeza de coordsFocado adicionada aos filtros de estado.")

    # 2. Limpar o coordsFocado ao focar em outro fornecedor (caso falhe o geocode)
    if 'const focarFornecedor =' in c:
        # Verifica se a função já reseta o estado antes de buscar
        if 'setCoordsFocado(null);' not in c.split('const focarFornecedor =')[1].split('};')[0]:
            # Reescreve a função inteira para garantir a limpeza
            padrao_func = re.compile(r'const focarFornecedor = async \(f: any\) => \{[\s\S]*?\};')
            nova_func = '''const focarFornecedor = async (f: any) => {
    setFornecedorFocado(f);
    setCoordsFocado(null); // Limpa a coordenada anterior

    if (f.latitude && f.longitude) {
      setCoordsFocado([f.latitude, f.longitude]);
      return;
    }

    try {
      const res = await fetch(`/api/empresa/geocode?endereco=${encodeURIComponent(`${f.endereco}, ${f.cidade}, ${f.estado}`)}`);
      const data = await res.json();
      
      if (data.lat && data.lon) {
        setCoordsFocado([data.lat, data.lon]);
      } else {
        const resCidade = await fetch(`/api/empresa/geocode?endereco=${encodeURIComponent(`${f.cidade}, ${f.estado}`)}`);
        const dataCidade = await resCidade.json();
        if (dataCidade.lat && dataCidade.lon) setCoordsFocado([dataCidade.lat, dataCidade.lon]);
      }
    } catch (e) {
      console.error("Erro ao geocodificar:", e);
    }
  };'''
            c = padrao_func.sub(nova_func, c, count=1)
            print("✅ Função 'focarFornecedor' atualizada para limpar o estado.")

    # 3. Garantir que o MapController reaja ao coordsFocado (useEffect)
    if 'useEffect' not in c:
        # Importa useEffect
        c = c.replace(
            'import { useState, useMemo } from "react";',
            'import { useState, useMemo, useEffect } from "react";'
        )
        print("✅ Import do useEffect adicionado.")

    # 4. Atualizar o MapController para aceitar a prop 'center' e 'zoom'
    # (já deve estar correto, mas vamos garantir)
    if 'function MapController({ center, zoom }' not in c:
        c = c.replace(
            'L.Marker.prototype.options.icon = DefaultIcon;',
            '''L.Marker.prototype.options.icon = DefaultIcon;

function MapController({ center, zoom }: { center: [number, number], zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
}'''
        )
        print("✅ MapController atualizado com useEffect.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ MapaFornecedores.tsx atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")