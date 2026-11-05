import os
import re

# 1. Verificar como o AppLayout está exportado
path_layout = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "AppLayout.tsx")

with open(path_layout, "r", encoding="utf-8") as f:
    layout_content = f.read()

# Verifica o tipo de export
if "export default function AppLayout" in layout_content:
    export_type = "default"
    print("✅ AppLayout é exportado como 'default'.")
elif "export function AppLayout" in layout_content:
    export_type = "named"
    print("✅ AppLayout é exportado como 'named'.")
elif "export const AppLayout" in layout_content:
    export_type = "const"
    print("✅ AppLayout é exportado como 'const'.")
else:
    export_type = "unknown"
    print("⚠️ Formato de export não reconhecido. Verifique o arquivo AppLayout.tsx.")

# 2. Ajustar o App.tsx
path_app = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")

with open(path_app, "r", encoding="utf-8") as f:
    c = f.read()

# Remove a importação atual
c = re.sub(r'import\s+\{\s*AppLayout\s*\}\s+from\s+"@/components/layout/AppLayout";\n?', '', c)
c = re.sub(r'import\s+AppLayout\s+from\s+"@/components/layout/AppLayout";\n?', '', c)

# Adiciona a importação correta
if export_type == "default":
    c = c.replace(
        'import { ProtectedRoute } from "@/components/auth/ProtectedRoute";',
        'import { ProtectedRoute } from "@/components/auth/ProtectedRoute";\nimport AppLayout from "@/components/layout/AppLayout";'
    )
elif export_type == "named":
    c = c.replace(
        'import { ProtectedRoute } from "@/components/auth/ProtectedRoute";',
        'import { ProtectedRoute } from "@/components/auth/ProtectedRoute";\nimport { AppLayout } from "@/components/layout/AppLayout";'
    )
elif export_type == "const":
    c = c.replace(
        'import { ProtectedRoute } from "@/components/auth/ProtectedRoute";',
        'import { ProtectedRoute } from "@/components/auth/ProtectedRoute";\nimport { AppLayout } from "@/components/layout/AppLayout";'
    )

with open(path_app, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ App.tsx ajustado com a importação correta do AppLayout.")