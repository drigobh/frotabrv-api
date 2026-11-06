import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "LeitorQRCode.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Adicionar o import do ChassiMapa
if "ChassiMapa" not in c:
    c = c.replace(
        'import { apiGet, apiPost } from "@/lib/api";',
        'import { apiGet, apiPost } from "@/lib/api";\nimport { ChassiMapa } from "@/components/ChassiMapa";'
    )

# 2. Garantir o estado do modal do mapa
if "const [mostrarMapa, setMostrarMapa] = useState(false);" not in c:
    c = c.replace(
        'const [naoConformidade, setNaoConformidade] = useState(false);',
        'const [naoConformidade, setNaoConformidade] = useState(false);\n  const [mostrarMapa, setMostrarMapa] = useState(false);'
    )

# 3. Adicionar o modal do mapa no final do componente
if "mostrarMapa &&" not in c:
    modal = '''
      {/* Modal do Mapa */}
      {mostrarMapa && pneu && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-4xl p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-slate-100">Mapa do Chassi</h2>
              <Button variant="ghost" size="icon" onClick={() => setMostrarMapa(false)}>
                <X className="size-5" />
              </Button>
            </div>
            <div className="max-h-[70vh] overflow-auto">
              <ChassiMapa 
                pneus={[pneu]} 
                veiculoId={pneu.veiculo_id} 
                tipo="cavalo" 
                templateChassiId={veiculo?.template_chassi_id} 
              />
            </div>
          </div>
        </div>
      )}
    '''
    # Insere antes do fechamento do return principal
    c = c.replace("    </div>\n  );\n}", modal + "    </div>\n  );\n}")
    
    # Garantir o import do X e do ChassiMapa
    if "X" not in c.split("from \"lucide-react\"")[0]:
        c = c.replace("import {", "import { X,")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ LeitorQRCode.tsx: Botão 'Visualizar Mapa' agora abre o modal com o chassi.")