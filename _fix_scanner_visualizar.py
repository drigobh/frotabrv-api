import os

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "LeitorQRCode.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Adicionar o botão "Visualizar" ao lado do mini mapa
if "Visualizar Mapa" not in c:
    c = c.replace(
        '<p className="text-[10px] text-slate-500 uppercase tracking-widest mb-2">Mapa do Chassi</p>',
        '''<p className="text-[10px] text-slate-500 uppercase tracking-widest mb-2">Mapa do Chassi</p>
                <div className="flex gap-2 mb-2">
                  <Button size="sm" variant="outline" onClick={() => setMostrarMapa(!mostrarMapa)}>
                    <Eye className="size-4 mr-1" /> Visualizar Mapa
                  </Button>
                </div>'''
    )
    # Adicionar estado para controlar a visualização
    c = c.replace(
        'const [naoConformidade, setNaoConformidade] = useState(false);',
        'const [naoConformidade, setNaoConformidade] = useState(false);\n  const [mostrarMapa, setMostrarMapa] = useState(false);'
    )
    # Importar o ícone Eye
    if "Eye" not in c.split("from \"lucide-react\"")[0]:
        c = c.replace("import {", "import { Eye,")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ LeitorQRCode.tsx: Botão 'Visualizar Mapa' adicionado.")