import xlrd
import os

def diagnosticar_xls():
    # ATENÇÃO: Coloque o caminho exato do arquivo XLS que você está tentando importar
    caminho_xls = rcaminho_xls = r"C:\Users\RAV\Downloads\Lista de Abastecimentos.xls"
    
    if not os.path.exists(caminho_xls):
        print(f"❌ Arquivo não encontrado em: {caminho_xls}")
        print("Por favor, edite o script e coloque o caminho correto da planilha.")
        return

    print(f"🔍 Lendo o arquivo: {caminho_xls}")
    
    try:
        workbook = xlrd.open_workbook(caminho_xls)
        sheet = workbook.sheet_by_index(0)
        
        print(f"\n--- Primeiras 20 linhas da planilha (Total: {sheet.nrows} linhas) ---")
        for i in range(min(20, sheet.nrows)):
            valores = []
            for j in range(sheet.ncols):
                celula = sheet.cell_value(i, j)
                if str(celula).strip():
                    valores.append(f"[{j}]: '{str(celula).strip()}'")
            
            if valores:
                print(f"Linha {i+1}: {' | '.join(valores)}")
            else:
                print(f"Linha {i+1}: (vazia)")
                
        print("\n💡 Dica: Veja em qual linha aparecem as palavras 'Data', 'Placa' e 'Litros' e qual é o índice da coluna (0, 1, 2...).")
    except Exception as e:
        print(f"❌ Erro ao ler o arquivo: {e}")

if __name__ == "__main__":
    diagnosticar_xls()