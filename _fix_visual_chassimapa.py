import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "components", "ChassiMapa.tsx")

if not os.path.exists(path):
    print("❌ ChassiMapa.tsx não encontrado.")
else:
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # 1. Corrigir a cor do pneu (fundo e texto)
    # Se o pneu está alocado (tem numero_fogo), fica azul claro
    # Se está vazio, fica branco
    c = c.replace(
        'className="text-slate-200"',
        'className="text-sky-300 font-bold"'
    )
    c = c.replace(
        'className="text-slate-400"',
        'className="text-white font-bold"'
    )
    c = c.replace(
        'className="text-slate-300"',
        'className="text-sky-300 font-bold"'
    )

    # 2. Corrigir o fundo dos pneus vazios
    c = c.replace(
        'bg-slate-800',
        'bg-slate-800/50 border border-slate-600'
    )
    c = c.replace(
        'border-slate-700',
        'border-sky-500/30'
    )

    # 3. Garantir que o texto do número de fogo fique bem visível
    c = re.sub(
        r'<p className="text-xs font-medium([^"]*)">\{p\.numero_fogo\}</p>',
        r'<p className="text-xs font-bold text-sky-300 \1">{p.numero_fogo}</p>',
        c
    )

    # 4. Se a estrutura for diferente, vamos garantir que a classe seja text-white para pneus vazios
    c = c.replace(
        'className="text-slate-500"',
        'className="text-white/70"'
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)

    print("✅ ChassiMapa.tsx: Cores ajustadas (Pneu alocado = azul claro, Vazio = branco).")