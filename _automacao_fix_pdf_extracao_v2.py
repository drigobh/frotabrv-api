import os
import re

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Substituir a função handleImportPDF inteira
    padrao = re.compile(r'const handleImportPDF = async[\s\S]*?\n  \};', re.DOTALL)
    
    nova_funcao = '''const handleImportPDF = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      let text = "";

      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const content = await page.getTextContent();
        text += content.items.map((item: any) => item.str).join(" ") + "\\n";
      }

      // 1. Extração da Placa
      const placaMatch = text.match(/PLACA[:\\s]*([A-Z]{3}[0-9][A-Z0-9][0-9]{2})/i) || text.match(/PLACA[:\\s]*([A-Z0-9]{7})/i);
      
      // 2. Extração do KM (Lida como número inteiro, ignorando pontos)
      const kmMatch = text.match(/KM[:\\s]*([\\d.,]+)/i);
      const kmNum = kmMatch ? Number(String(kmMatch[1]).replace(/\\D/g, "")) : 0;

      // 3. Extração de Litros e Preço
      const litrosMatch = text.match(/L\\s+([\\d.,]+)\\s+([\\d.,]+)\\s+([\\d.,]+)/i) || text.match(/L\\s+([\\d.,]+)\\s+([\\d.,]+)/i);
      
      // 4. Extração do Posto (Emitente)
      const postoMatch = text.match(/RECEBEMOS DE\\s+([A-Z0-9\\s\\-.]+)\\s*\\(/i) || text.match(/RECEBEMOS DE\\s+([A-Z0-9\\s\\-.]+)/i);
      
      // 5. Extração do Produto
      const produtoMatch = text.match(/(OLEO DIESEL[A-Z0-9\\s]*|DIESEL[A-Z0-9\\s]*|ARLA[A-Z0-9\\s]*)/i);

      // 6. Extração da Data de Emissão
      const dateMatch = text.match(/DATA DA EMISSÃO\\s*(\\d{2}\\/\\d{2}\\/\\d{4})/i);
      let dataStr = new Date().toISOString().split('T')[0]; // Fallback para hoje
      if (dateMatch) {
         const [d, m, y] = dateMatch[1].split("/");
         dataStr = `${y}-${m}-${d}`;
      }

      const parseNum = (val: string) => {
        if (!val) return 0;
        let str = String(val).replace(/[^\\d.,]/g, "");
        if (str.includes('.') && str.includes(',')) {
            str = str.replace(/\\./g, '').replace(',', '.');
        } else if (str.includes(',')) {
            str = str.replace(',', '.');
        }
        return Number(str);
      };

      const payload = {
        data: dataStr,
        hora: null, 
        numero_nf: null, 
        chave_nfe: null, 
        cnpj: null, 
        fornecedor: postoMatch ? postoMatch[1].trim() : "Importado",
        placa: placaMatch ? placaMatch[1].toUpperCase() : null, 
        litros: litrosMatch ? parseNum(litrosMatch[1]) : 0,
        preco_litro: litrosMatch ? parseNum(litrosMatch[2]) : 0, 
        km: kmNum, 
        origem: "pdf",
        produto: produtoMatch ? produtoMatch[0].trim().toUpperCase() : "DIESEL S-10"
      };

      await apiPost("/abastecimentos/importar", payload);
      toast.success("Nota Fiscal importada com sucesso!");
      invalidate();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao importar o PDF.");
    }
  };'''

    if padrao.search(c):
        # O SEGREDO ESTÁ AQUI: usar lambda para não interpretar \s como escape do Python
        c = padrao.sub(lambda m: nova_funcao, c)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Função handleImportPDF reescrita com sucesso.")
    else:
        print("⚠️ Não foi possível encontrar a função handleImportPDF.")

if __name__ == "__main__":
    fix_frontend(os.getcwd())