import os

def limpar_duplicatas(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Estoque.tsx")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    novas_linhas = []
    ja_tem_openInvConfirm = False
    removidas = 0

    for linha in linhas:
        if 'const [openInvConfirm, setOpenInvConfirm] = useState(false);' in linha:
            if ja_tem_openInvConfirm:
                removidas += 1
                continue  # Pula a duplicata
            else:
                ja_tem_openInvConfirm = True
        
        novas_linhas.append(linha)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.writelines(novas_linhas)
    
    print(f"✅ Limpeza concluída! {removidas} declaração(ões) duplicada(s) de 'openInvConfirm' removida(s).")

if __name__ == "__main__":
    limpar_duplicatas(os.getcwd())