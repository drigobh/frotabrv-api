import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MAPA_SPLIT_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "components", "MapaFornecedores.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/components/MapaFornecedores.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def recriar(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "MapaFornecedores.tsx")
    
    codigo = '''import { useState, useMemo } from "react";
import { MapPin, X, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";
let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

// Coordenadas centrais de cada estado (Lat, Lon)
const ESTADOS_COORDS: Record<string, [number, number]> = {
  AC: [-9.0238, -70.812], AL: [-9.5713, -36.782], AP: [1.415, -51.771], AM: [-3.4168, -65.8561],
  BA: [-12.5797, -41.7007], CE: [-5.4984, -39.3206], DF: [-15.7801, -47.9292], ES: [-19.1834, -40.3089],
  GO: [-15.827, -49.8362], MA: [-4.9609, -45.2744], MT: [-12.6819, -56.9211], MS: [-20.7722, -54.7852],
  MG: [-18.5122, -44.555], PA: [-1.9981, -54.9306], PB: [-7.2399, -36.7819], PR: [-25.2521, -52.0215],
  PE: [-8.8137, -36.9541], PI: [-7.7183, -42.7289], RJ: [-22.9068, -43.1729], RN: [-5.7945, -36.9003],
  RS: [-30.0346, -51.2177], RO: [-11.5057, -63.5806], RR: [2.7376, -62.0751], SC: [-27.2423, -50.2189],
  SP: [-23.5505, -46.6333], SE: [-10.5741, -37.3857], TO: [-10.1753, -48.2982]
};

interface MapaProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fornecedores: any[];
}

// Componente para controlar o zoom e centralização do mapa
function MapController({ center, zoom }: { center: [number, number], zoom: number }) {
  const map = useMap();
  map.setView(center, zoom);
  return null;
}

export function MapaFornecedores({ open, onOpenChange, fornecedores }: MapaProps) {
  const [estadoSelecionado, setEstadoSelecionado] = useState("");
  const [filtroNome, setFiltroNome] = useState("");
  const [filtroTipo, setFiltroTipo] = useState("");
  const [fornecedorFocado, setFornecedorFocado] = useState<any>(null);

  // Lista filtrada baseada no estado e nos filtros de texto
  const fornecedoresFiltrados = useMemo(() => {
    let filtered = fornecedores;
    if (estadoSelecionado) filtered = filtered.filter(f => f.estado === estadoSelecionado);
    if (filtroNome) filtered = filtered.filter(f => f.nome.toLowerCase().includes(filtroNome.toLowerCase()));
    if (filtroTipo) filtered = filtered.filter(f => f.tipo_fornecedor_id === filtroTipo);
    return filtered;
  }, [fornecedores, estadoSelecionado, filtroNome, filtroTipo]);

  if (!open) return null;

  const estados = [...new Set(fornecedores.map(f => f.estado))].filter(Boolean).sort();

  // Define o centro com base no fornecedor focado ou no primeiro fornecedor da lista
  let center: [number, number] = [-15.7801, -47.9292];
  let zoom = 4;

  if (fornecedorFocado && ESTADOS_COORDS[fornecedorFocado.estado]) {
    center = ESTADOS_COORDS[fornecedorFocado.estado];
    zoom = 10; // Zoom alto no fornecedor focado
  } else if (estadoSelecionado && ESTADOS_COORDS[estadoSelecionado]) {
    center = ESTADOS_COORDS[estadoSelecionado];
    zoom = 6; // Zoom médio no estado
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-[95vw] h-[90vh] flex flex-col">
        
        {/* Cabeçalho */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900 rounded-t-2xl">
          <h2 className="text-lg font-bold text-slate-100">Mapa dos Fornecedores</h2>
          <button onClick={() => onOpenChange(false)} className="text-slate-400 hover:text-white">
            <X className="size-5" />
          </button>
        </div>

        {/* Barra de Filtros de Estado */}
        <div className="px-6 py-3 border-b border-slate-800 flex gap-2 overflow-x-auto">
          <Button variant={estadoSelecionado === "" ? "default" : "outline"} onClick={() => setEstadoSelecionado("")} className="h-8">Todos</Button>
          {estados.map(uf => (
            <Button key={uf} variant={estadoSelecionado === uf ? "default" : "outline"} onClick={() => setEstadoSelecionado(uf)} className="h-8">
              {uf} ({fornecedores.filter(f => f.estado === uf).length})
            </Button>
          ))}
        </div>

        {/* Corpo (Split View) */}
        <div className="flex-1 flex overflow-hidden">
          
          {/* Coluna Esquerda: Lista */}
          <div className="w-1/3 border-r border-slate-800 flex flex-col bg-slate-900/50">
            <div className="p-4 border-b border-slate-800 space-y-2">
              <Input 
                placeholder="Buscar fornecedor..." 
                value={filtroNome} 
                onChange={(e) => setFiltroNome(e.target.value)} 
                className="h-9 bg-slate-950" 
              />
            </div>
            
            <div className="flex-1 overflow-y-auto p-2 space-y-1">
              {fornecedoresFiltrados.length === 0 ? (
                <p className="text-center text-slate-500 py-10 text-sm">Nenhum fornecedor encontrado.</p>
              ) : (
                fornecedoresFiltrados.map(f => (
                  <button
                    key={f.id}
                    onClick={() => setFornecedorFocado(f)}
                    className={`w-full text-left p-3 rounded-lg transition-colors flex flex-col gap-1 ${
                      fornecedorFocado?.id === f.id ? "bg-sky-600/20 border border-sky-500/50" : "hover:bg-slate-800 border border-transparent"
                    }`}
                  >
                    <span className="text-sm font-medium text-slate-200">{f.nome}</span>
                    <span className="text-xs text-slate-500 flex items-center gap-1"><MapPin className="size-3" /> {f.cidade} - {f.estado}</span>
                  </button>
                ))
              )}
            </div>
          </div>

          {/* Coluna Direita: Mapa */}
          <div className="w-2/3 relative z-0">
            <MapContainer center={center} zoom={zoom} style={{ height: "100%", width: "100%" }}>
              <MapController center={center} zoom={zoom} />
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {fornecedoresFiltrados.map(f => {
                const coords = ESTADOS_COORDS[f.estado] || [-15.7801, -47.9292];
                // Offset para não sobrepor os pins
                const offsetLat = (Math.random() - 0.5) * 1.5;
                const offsetLon = (Math.random() - 0.5) * 1.5;
                return (
                  <Marker key={f.id} position={[coords[0] + offsetLat, coords[1] + offsetLon]}>
                    <Popup>
                      <strong>{f.nome}</strong><br/>
                      {f.endereco}<br/>
                      {f.cidade} - {f.estado}
                    </Popup>
                  </Marker>
                );
              })}
            </MapContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
'''
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Componente MapaFornecedores.tsx atualizado para Split View (Lista + Mapa).")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    recriar(raiz)