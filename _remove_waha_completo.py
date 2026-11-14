import os
import shutil

raiz = os.getcwd()

# ============================================================
# 1. APAGAR ARQUIVOS FÍSICOS DO WAHA
# ============================================================
arquivos_para_apagar = [
    "app/backend/services/whatsapp_service.py",
    "app/backend/routers/whatsapp.py",
    "frontend/src/pages/WhatsAppConfig.tsx",
]

for rel_path in arquivos_para_apagar:
    path_abs = os.path.join(raiz, rel_path)
    if os.path.exists(path_abs):
        os.remove(path_abs)
        print(f"🗑️ Apagado: {rel_path}")
    else:
        print(f"ℹ️ Já não existia: {rel_path}")

# ============================================================
# 2. LIMPAR O SERVER.PY (Remover import e include_router)
# ============================================================
path_server = os.path.join(raiz, "app", "backend", "server.py")
with open(path_server, "r", encoding="utf-8") as f:
    linhas = f.readlines()

novas_linhas = []
for linha in linhas:
    # Remove o import do whatsapp (se estiver na lista de routers)
    if "from routers import" in linha and "whatsapp" in linha:
        linha = linha.replace(", whatsapp", "").replace("whatsapp, ", "").replace("whatsapp", "")
        # Limpa vírgulas duplas ou no final
        linha = linha.replace(", ,", ",").replace(", )", ")").replace(", \n", "\n")
    # Remove a linha do include_router
    if "api_router.include_router(whatsapp.router)" in linha or "app.include_router(whatsapp.router)" in linha:
        continue
    novas_linhas.append(linha)

with open(path_server, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(novas_linhas)
print("✅ server.py limpo (import e include_router do whatsapp removidos).")

# ============================================================
# 3. LIMPAR O APP.TSX (Remover import e rota)
# ============================================================
path_app = os.path.join(raiz, "frontend", "src", "App.tsx")
with open(path_app, "r", encoding="utf-8") as f:
    c_app = f.read()

c_app = c_app.replace('import WhatsAppConfig from "@/pages/WhatsAppConfig";\n', "")
c_app = c_app.replace('<Route path="/admin/whatsapp" element={<WhatsAppConfig />} />\n', "")

with open(path_app, "w", encoding="utf-8", newline="\n") as f:
    f.write(c_app)
print("✅ App.tsx limpo (import e rota do WhatsApp removidos).")

# ============================================================
# 4. LIMPAR O SIDEBAR.TSX (Remover item do menu)
# ============================================================
path_sidebar = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
with open(path_sidebar, "r", encoding="utf-8") as f:
    linhas = f.readlines()

novas_linhas = []
for linha in linhas:
    if 'label: "WhatsApp Automático"' in linha:
        continue
    novas_linhas.append(linha)

with open(path_sidebar, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(novas_linhas)
print("✅ Sidebar.tsx limpo (item do menu removido).")

# ============================================================
# 5. VERIFICAR SE AINDA HÁ REFERÊNCIAS AO WAHA NO PROJETO
# ============================================================
print("\n🔍 Verificando referências restantes ao WAHA...")
referencias = []
for root, dirs, files in os.walk(raiz):
    # Ignora pastas de sistema e node_modules
    dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build']]
    for file in files:
        if file.endswith(('.py', '.tsx', '.ts')):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                conteudo = f.read()
                if "WAHA" in conteudo or "waha" in conteudo:
                    referencias.append(path)

if referencias:
    print("⚠️ Referências ao WAHA ainda encontradas nos arquivos:")
    for ref in referencias:
        print(f"   - {ref}")
else:
    print("✅ Nenhuma referência ao WAHA encontrada no projeto.")

# ============================================================
# 6. COMMIT E PUSH
# ============================================================
import subprocess
print("\n📤 Fazendo commit e push da limpeza...")
subprocess.run(["git", "add", "-A"], cwd=raiz)
subprocess.run(["git", "commit", "-m", "chore: remove integracao completa com WAHA"], cwd=raiz)
subprocess.run(["git", "push"], cwd=raiz)
print("✅ Push feito.")