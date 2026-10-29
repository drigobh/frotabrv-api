import { useState } from "react";
import { MapPin, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
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

interface MapaProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fornecedores: any[];
}

export function MapaFornecedores({ open, onOpenChange, fornecedores }: MapaProps) {
  const [estadoSelecionado, setEstadoSelecionado] = useState("");
  const [fornecedoresMapa, setFornecedoresMapa] = useState<any[]>([]);
  const [selecionadosMapa, setSelecionadosMapa] = useState<string[]>([]);
  const [mostrarMapa, setMostrarMapa] = useState(false);
  const [coords, setCoords] = useState<Record<string, [number, number]>>({});
  const [carregando, setCarregando] = useState(false);

  if (!open) return null;

  const estados = [...new Set(fornecedores.map(f => f.estado))].filter(Boolean).sort();

  const carregarFornecedoresEstado = (uf: string) => {
    setEstadoSelecionado(uf);
    const filtrados = fornecedores.filter(f => (uf === "TODOS" || f.estado === uf) && f.endereco && f.cidade);
    setFornecedoresMapa(filtrados);
    setSelecionadosMapa([]);
    setMostrarMapa(false);
  };

  const toggleFornecedor = (id: string) => {
    setSelecionadosMapa(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  const toggleTodos = () => {
    if (selecionadosMapa.length === fornecedoresMapa.length) {
      setSelecionadosMapa([]);
    } else {
      setSelecionadosMapa(fornecedoresMapa.map(f => f.id));
    }
  };

  const abrirMapaReal = async () => {
    const lista = fornecedoresMapa.filter(f => selecionadosMapa.includes(f.id));
    if (lista.length === 0) return;

    setCarregando(true);
    const promises = lista.map(async (f) => {
      try {
        const res = await fetch(`/api/empresa/geocode?endereco=${encodeURIComponent(`${f.endereco}, ${f.cidade}, ${f.estado}`)}`);
        const data = await res.json();
        if (data && data.lat && data.lon) {
          return { id: f.id, lat: data.lat, lon: data.lon };
        }
      } catch (e) {}
      return null;
    });

    const results = await Promise.all(promises);
    const newCoords: Record<string, [number, number]> = {};
    results.forEach((res) => {
      if (res) newCoords[res.id] = [res.lat, res.lon];
    });
    
    setCoords(newCoords);
    setMostrarMapa(true);
    setCarregando(false);
  };

  const center = Object.values(coords).length > 0 
    ? [Object.values(coords)[0][0], Object.values(coords)[0][1]] 
    : [-15.7801, -47.9292];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      {/* Modal expandido (95% da tela) */}
      <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-[95vw] h-[90vh] flex flex-col">
        
        {/* Cabeçalho */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900 rounded-t-2xl">
          <h2 className="text-lg font-bold text-slate-100">Mapa dos Fornecedores</h2>
          <button onClick={() => onOpenChange(false)} className="text-slate-400 hover:text-white">
            <X className="size-5" />
          </button>
        </div>

        {/* Corpo */}
        <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4 relative">
          {mostrarMapa ? (
            <div className="w-full h-full rounded-xl overflow-hidden border border-slate-700 relative z-0">
              <MapContainer center={center as any} zoom={8} style={{ height: "100%", width: "100%" }}>
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {fornecedoresMapa.filter(f => selecionadosMapa.includes(f.id)).map(f => {
                  const c = coords[f.id];
                  if (!c) return null;
                  return (
                    <Marker key={f.id} position={c}>
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
          ) : !estadoSelecionado ? (
            <div className="flex flex-col gap-3">
              <Label className="text-slate-400">Selecione o Estado</Label>
              <div className="grid grid-cols-4 gap-2">
                <Button variant="outline" onClick={() => carregarFornecedoresEstado("TODOS")} className="h-10">
                  Todos
                </Button>
                {estados.map(uf => (
                  <Button key={uf} variant="outline" onClick={() => carregarFornecedoresEstado(uf)} className="h-10">
                    {uf} ({fornecedores.filter(f => f.estado === uf).length})
                  </Button>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-3 h-full">
              <div className="flex justify-between items-center">
                <Label className="text-slate-400">Fornecedores em {estadoSelecionado} ({fornecedoresMapa.length})</Label>
                <Button variant="ghost" size="sm" onClick={toggleTodos} className="text-sky-400">Marcar/Desmarcar Todos</Button>
              </div>
              
              <div className="border border-slate-800 rounded-lg flex-1 overflow-y-auto">
                {fornecedoresMapa.length === 0 ? (
                  <p className="text-center text-slate-500 py-10">Nenhum fornecedor com endereço completo neste estado.</p>
                ) : (
                  fornecedoresMapa.map(f => (
                    <label key={f.id} className="flex items-center gap-3 p-3 border-b border-slate-800 last:border-0 hover:bg-slate-800/50 cursor-pointer">
                      <input type="checkbox" checked={selecionadosMapa.includes(f.id)} onChange={() => toggleFornecedor(f.id)} className="size-4 accent-sky-500" />
                      <div>
                        <p className="text-sm font-medium text-slate-200">{f.nome}</p>
                        <p className="text-xs text-slate-500">{f.endereco}, {f.cidade} - {f.estado}</p>
                      </div>
                    </label>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Rodapé */}
        <div className="flex items-center justify-end px-6 py-4 border-t border-slate-800 gap-3 bg-slate-900 rounded-b-2xl">
          {mostrarMapa ? (
            <Button variant="outline" onClick={() => setMostrarMapa(false)}>Voltar para Lista</Button>
          ) : estadoSelecionado ? (
            <>
              <Button variant="outline" onClick={() => setEstadoSelecionado("")}>Voltar</Button>
              <Button onClick={abrirMapaReal} disabled={selecionadosMapa.length === 0 || carregando} className="bg-emerald-600 hover:bg-emerald-500">
                <MapPin className="size-4 mr-2" /> {carregando ? "Carregando Mapa..." : `Abrir no Mapa (${selecionadosMapa.length})`}
              </Button>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
