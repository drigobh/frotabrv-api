import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PNEUS_FASE2_2_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = ["frontend/src/pages/Pneus.tsx"]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def criar_componente_mapa(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "ChassiMapa.tsx")
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write('''import { Disc, AlertTriangle, CheckCircle2, XCircle } from "lucide-react";

interface Pneu {
  id: string;
  numero_fogo: string;
  marca: string;
  medida: string;
  status: string;
  veiculo_id?: string;
  carreta_id?: string;
  posicao?: string;
  sulco_atual?: number;
  pressao_atual?: number;
}

interface ChassiMapaProps {
  pneus: Pneu[];
  veiculoId: string;
  configuracao: string; // Ex: "6x2"
  tipo: "cavalo" | "carreta";
}

export function ChassiMapa({ pneus, veiculoId, configuracao, tipo }: ChassiMapaProps) {
  // Filtra os pneus do veículo específico
  const pneusDoVeiculo = pneus.filter(p => 
    tipo === "cavalo" ? p.veiculo_id === veiculoId : p.carreta_id === veiculoId
  );

  // Função para buscar o pneu em uma posição específica
  const getPneu = (posicao: string) => {
    return pneusDoVeiculo.find(p => p.posicao === posicao);
  };

  // Cores com base no sulco (mm)
  const getCorSulco = (sulco?: number) => {
    if (!sulco) return "bg-slate-800 border-slate-700 text-slate-500";
    if (sulco <= 1.6) return "bg-black border-black text-white"; // Crítico legal
    if (sulco <= 3.0) return "bg-rose-500/20 border-rose-500 text-rose-400"; // Vermelho
    if (sulco <= 5.9) return "bg-amber-500/20 border-amber-500 text-amber-400"; // Amarelo
    return "bg-emerald-500/20 border-emerald-500 text-emerald-400"; // Verde
  };

  const renderCardPneu = (posicao: string, label: string) => {
    const pneu = getPneu(posicao);
    
    if (!pneu) {
      return (
        <div className="flex flex-col items-center gap-1">
          <div className="size-12 rounded-lg border-2 border-dashed border-slate-700 flex items-center justify-center text-slate-600">
            <Disc className="size-5" />
          </div>
          <span className="text-[9px] text-slate-600">{label}</span>
        </div>
      );
    }

    return (
      <div className="flex flex-col items-center gap-1 group relative">
        <div className={`size-12 rounded-lg border-2 flex flex-col items-center justify-center transition-all cursor-pointer ${getCorSulco(pneu.sulco_atual)} hover:scale-110`}>
          <span className="text-[10px] font-bold">{pneu.numero_fogo.slice(0, 6)}</span>
          <span className="text-[8px] opacity-70">{pneu.sulco_atual ? `${pneu.sulco_atual}mm` : "—"}</span>
        </div>
        <span className="text-[9px] text-slate-500">{label}</span>
        
        {/* Tooltip */}
        <div className="absolute bottom-full mb-2 hidden group-hover:block w-40 bg-slate-800 border border-slate-700 rounded-lg p-2 text-xs z-50 shadow-xl">
          <p className="font-bold text-slate-200">{pneu.numero_fogo}</p>
          <p className="text-slate-400">{pneu.marca} - {pneu.medida}</p>
          <p className="text-slate-400">Sulco: {pneu.sulco_atual || "—"} mm</p>
          <p className="text-slate-400">Pressão: {pneu.pressao_atual || "—"} psi</p>
        </div>
      </div>
    );
  };

  // Renderiza o mapa para Cavalo (6x2)
  if (tipo === "cavalo" && configuracao === "6x2") {
    return (
      <div className="glass p-6 rounded-2xl">
        <h3 className="text-sm font-bold text-slate-300 mb-4 flex items-center gap-2">
          <Disc className="size-4 text-sky-400" /> Chassi do Cavalo Mecânico ({configuracao})
        </h3>
        
        <div className="flex flex-col gap-4">
          {/* Eixo 1 - Direcional */}
          <div className="flex justify-between items-center px-8">
            {renderCardPneu("1-E", "1-ESQ")}
            <div className="text-[10px] text-slate-500 font-bold uppercase">Eixo 1 (Direcional)</div>
            {renderCardPneu("1-D", "1-DIR")}
          </div>
          
          {/* Eixo 2 - Tração */}
          <div className="flex justify-between items-center px-8 border-t border-slate-800 pt-4">
            <div className="flex gap-1">
              {renderCardPneu("2-EI", "2-EI")}
              {renderCardPneu("2-EE", "2-EE")}
            </div>
            <div className="text-[10px] text-slate-500 font-bold uppercase">Eixo 2 (Tração)</div>
            <div className="flex gap-1">
              {renderCardPneu("2-DI", "2-DI")}
              {renderCardPneu("2-DE", "2-DE")}
            </div>
          </div>
          
          {/* Eixo 3 - Truck */}
          <div className="flex justify-between items-center px-8 border-t border-slate-800 pt-4">
            <div className="flex gap-1">
              {renderCardPneu("3-EI", "3-EI")}
              {renderCardPneu("3-EE", "3-EE")}
            </div>
            <div className="text-[10px] text-slate-500 font-bold uppercase">Eixo 3 (Truck)</div>
            <div className="flex gap-1">
              {renderCardPneu("3-DI", "3-DI")}
              {renderCardPneu("3-DE", "3-DE")}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Renderiza o mapa para Carreta (3 Eixos)
  if (tipo === "carreta" && configuracao === "3 eixos") {
    return (
      <div className="glass p-6 rounded-2xl">
        <h3 className="text-sm font-bold text-slate-300 mb-4 flex items-center gap-2">
          <Disc className="size-4 text-sky-400" /> Chassi da Carreta ({configuracao})
        </h3>
        
        <div className="flex flex-col gap-4">
          {[4, 5, 6].map((eixo) => (
            <div key={eixo} className={`flex justify-between items-center px-8 ${eixo > 4 ? 'border-t border-slate-800 pt-4' : ''}`}>
              <div className="flex gap-1">
                {renderCardPneu(`${eixo}-EI`, `${eixo}-EI`)}
                {renderCardPneu(`${eixo}-EE`, `${eixo}-EE`)}
              </div>
              <div className="text-[10px] text-slate-500 font-bold uppercase">Eixo {eixo} (Carreta)</div>
              <div className="flex gap-1">
                {renderCardPneu(`${eixo}-DI`, `${eixo}-DI`)}
                {renderCardPneu(`${eixo}-DE`, `${eixo}-DE`)}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Fallback para configurações não mapeadas
  return (
    <div className="glass p-6 rounded-2xl text-center text-slate-500">
      <AlertTriangle className="size-8 mx-auto mb-2" />
      <p className="text-sm">Configuração de eixos "{configuracao}" ainda não mapeada.</p>
    </div>
  );
}
''')
    print("✅ Componente ChassiMapa.tsx criado.")

def atualizar_pneus(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar import do ChassiMapa
    if 'ChassiMapa' not in c:
        c = c.replace(
            'import { FieldSelect } from "@/components/common/FieldSelect";',
            'import { FieldSelect } from "@/components/common/FieldSelect";\nimport { ChassiMapa } from "@/components/ChassiMapa";'
        )

    # 2. Adicionar seção do mapa no final da tela (antes do fechamento)
    if 'Chassi do Veículo' not in c:
        # Adiciona após a tabela de pneus
        idx = c.rfind('</div>\n  );')
        if idx != -1:
            secao_mapa = '''
      {/* Mapa de Chassi */}
      <div className="mt-8">
        <h3 className="text-lg font-bold text-slate-100 mb-4">Chassi do Veículo</h3>
        <div className="grid grid-cols-1 gap-4">
          <ChassiMapa 
            pneus={pneus} 
            veiculoId="00000000-0000-0000-0000-000000000000" 
            configuracao="6x2" 
            tipo="cavalo" 
          />
          <ChassiMapa 
            pneus={pneus} 
            veiculoId="00000000-0000-0000-0000-000000000000" 
            configuracao="3 eixos" 
            tipo="carreta" 
          />
        </div>
      </div>
'''
            c = c[:idx] + secao_mapa + c[idx:]
            print("✅ Seção do mapa de chassi adicionada à tela de Pneus.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Pneus.tsx atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    criar_componente_mapa(raiz)
    atualizar_pneus(raiz)
    print("\n✅ Fase 2.2 aplicada com sucesso!")