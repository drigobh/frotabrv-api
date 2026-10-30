import os
import shutil

def aplicar():
    raiz = os.getcwd()
    txt_path = os.path.join(raiz, "relatorios_completo.txt")
    tsx_path = os.path.join(raiz, "frontend", "src", "pages", "RelatorioManutencao.tsx")
    
    if not os.path.exists(txt_path):
        print("❌ Arquivo relatorios_completo.txt não encontrado.")
        return
        
    shutil.copy(txt_path, tsx_path)
    print("✅ RelatorioManutencao.tsx atualizado com sucesso.")

if __name__ == "__main__":
    aplicar()