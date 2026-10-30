import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PNEUS_TESTID_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Pneus.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Se o erro do testId já foi resolvido ou se o arquivo não tem os FieldSelects novos, não faz nada.
    if 'testId="pneu-marca"' in c:
        print("ℹ️ Os campos já estão com testId.")
        return

    # Inserindo o testId em cada FieldSelect do modal
    c = c.replace(
        'options={marcasDb.map((m: any) => ({ value: m.nome, label: m.nome }))} \n                  placeholder="Selecione a Marca..."',
        'options={marcasDb.map((m: any) => ({ value: m.nome, label: m.nome }))} \n                  placeholder="Selecione a Marca..."\n                  testId="pneu-marca"'
    )
    
    c = c.replace(
        'options={modelosDb.map((m: any) => ({ value: m.nome, label: m.nome }))} \n                  placeholder="Selecione o Modelo..."',
        'options={modelosDb.map((m: any) => ({ value: m.nome, label: m.nome }))} \n                  placeholder="Selecione o Modelo..."\n                  testId="pneu-modelo"'
    )

    c = c.replace(
        'options={medidasDb.map((m: any) => ({ value: m.medida, label: m.medida }))} \n                  placeholder="Selecione a Medida..."',
        'options={medidasDb.map((m: any) => ({ value: m.medida, label: m.medida }))} \n                  placeholder="Selecione a Medida..."\n                  testId="pneu-medida"'
    )

    # Verifica se a substituição simples funcionou, senão tenta a versão com quebras de linha menores (dependendo de como o VS Code formatou)
    if 'testId="pneu-marca"' not in c:
        c = c.replace(
            'placeholder="Selecione a Marca..." \n                />',
            'placeholder="Selecione a Marca..." \n                  testId="pneu-marca"\n                />'
        )
        c = c.replace(
            'placeholder="Selecione o Modelo..." \n                />',
            'placeholder="Selecione o Modelo..." \n                  testId="pneu-modelo"\n                />'
        )
        c = c.replace(
            'placeholder="Selecione a Medida..." \n                />',
            'placeholder="Selecione a Medida..." \n                  testId="pneu-medida"\n                />'
        )

    # Para Tipo e Status que estão na mesma linha
    c = c.replace(
        '<FieldSelect value={form.tipo} onChange={(v) => setForm(s => ({ ...s, tipo: v }))} options={TIPOS_PNEU.map(t => ({ value: t, label: t }))} />',
        '<FieldSelect value={form.tipo} onChange={(v) => setForm(s => ({ ...s, tipo: v }))} options={TIPOS_PNEU.map(t => ({ value: t, label: t }))} testId="pneu-tipo" />'
    )
    c = c.replace(
        '<FieldSelect value={form.status} onChange={(v) => setForm(s => ({ ...s, status: v }))} options={STATUS_PNEU.map(s => ({ value: s, label: s }))} />',
        '<FieldSelect value={form.status} onChange={(v) => setForm(s => ({ ...s, status: v }))} options={STATUS_PNEU.map(s => ({ value: s, label: s }))} testId="pneu-status" />'
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Pneus.tsx atualizado com os testIds obrigatórios.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")