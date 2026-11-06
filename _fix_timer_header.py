import os
import re

# ==========================================
# 1. GARANTIR QUE O COMPONENTE TIMER EXISTE
# ==========================================
path_timer = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "SessionTimer.tsx")

if not os.path.exists(path_timer):
    conteudo_timer = r'''import { useState, useEffect } from "react";
import { Clock } from "lucide-react";

export function SessionTimer({ timeoutMinutos, onTimeout }: { timeoutMinutos: number, onTimeout: () => void }) {
  const [segundosRestantes, setSegundosRestantes] = useState(timeoutMinutos * 60);

  useEffect(() => {
    if (segundosRestantes <= 0) {
      onTimeout();
      return;
    }
    const interval = setInterval(() => {
      setSegundosRestantes((s) => s - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [segundosRestantes, onTimeout]);

  const minutos = Math.floor(segundosRestantes / 60);
  const segundos = segundosRestantes % 60;

  return (
    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/50 text-xs text-slate-400">
      <Clock className="size-3.5" />
      <span className="font-mono">{String(minutos).padStart(2, '0')}:{String(segundos).padStart(2, '0')}</span>
    </div>
  );
}
'''
    with open(path_timer, "w", encoding="utf-8") as f:
        f.write(conteudo_timer)
    print("✅ Componente SessionTimer criado.")

# ==========================================
# 2. INJETAR O TIMER NO APPLAYOUT
# ==========================================
path_layout = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "AppLayout.tsx")

with open(path_layout, "r", encoding="utf-8") as f:
    c = f.read()

# 2.1. Garantir o import do Timer
if "SessionTimer" not in c:
    c = c.replace(
        'import { useMe } from "@/hooks/useSession";',
        'import { useMe } from "@/hooks/useSession";\nimport { SessionTimer } from "./SessionTimer";\nimport { realizarLogoff } from "@/lib/logoff";'
    )
    print("✅ Import do SessionTimer adicionado.")

# 2.2. Injetar o Timer na barra de topo
# O AppLayout geralmente tem uma <div> no topo (com "Bem-vindo", "Notificações", "Perfil", etc.)
# Vamos procurar um elemento que contenha o nome do usuário ou um ícone de notificação
# para inserir o timer ao lado.

# Procura a div de ações do header (que geralmente tem "Sair" ou "Perfil")
# Vamos usar uma abordagem mais genérica: procurar a primeira div que tenha "flex items-center gap" no topo do layout
match_header = re.search(r'(<header[^>]*>|<div[^>]*flex items-center justify-between[^>]*>)', c)

if match_header:
    # Se encontrou um cabeçalho, insere o Timer logo antes do fechamento da tag (ou antes de um botão)
    # Para simplificar, vamos adicionar o Timer como o primeiro elemento dentro do cabeçalho
    header_tag = match_header.group(1)
    c = c.replace(header_tag, header_tag + '\n        <SessionTimer timeoutMinutos={30} onTimeout={realizarLogoff} />')
    print("✅ Timer injetado no cabeçalho (via tag encontrada).")
else:
    # Fallback: procura um lugar onde tenha o nome do usuário e injeta antes
    match_user = re.search(r'(\{me\?\.nome\})', c)
    if match_user:
        c = c.replace(match_user.group(1), '<SessionTimer timeoutMinutos={30} onTimeout={realizarLogoff} />\n        ' + match_user.group(1))
        print("✅ Timer injetado ao lado do nome do usuário (fallback).")
    else:
        print("⚠️ Não foi possível encontrar o cabeçalho no AppLayout. Verifique manualmente.")

with open(path_layout, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ AppLayout atualizado!")