import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_visual_carretas_{agora}.zip"
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print(f"📦 Criando Backup Full do Sistema...")
    ignorar = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build']
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta_alvo in ['app', 'frontend']:
            caminho_pasta = os.path.join(raiz, pasta_alvo)
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in ignorar]
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try:
                        zipf.write(caminho_completo, caminho_relativo)
                    except Exception:
                        pass
    print(f"✅ Backup Full salvo em: _automacao/backups/{nome_backup}")

def atualizar_tela_carretas(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Carretas.tsx")
    if not os.path.exists(caminho):
        print("❌ Erro: Carretas.tsx não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # O script vai procurar o bloco onde o formulário de cadastro é renderizado.
    # Como o React é estruturado, vamos fazer uma substituição do bloco de inputs do formulário modal.
    # ATENÇÃO: Esta é uma substituição baseada no padrão original do projeto.
    
    # 1. Atualizar o bloco de inputs do formulário (código, tipo, observacoes -> adicionar os novos)
    busca_inputs = '''            <div className="space-y-2">
              <Label htmlFor="codigo">Código</Label>
              <Input
                id="codigo"
                value={form.codigo}
                onChange={(e) => setForm({ ...form, codigo: e.target.value })}
                placeholder="CR-001"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="tipo">Tipo</Label>
              <Select
                value={form.tipo}
                onValueChange={(v) => setForm({ ...form, tipo: v })}
              >
                <SelectTrigger id="tipo">
                  <SelectValue placeholder="Selecione o tipo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Bau">Bau</SelectItem>
                  <SelectItem value="Sider">Sider</SelectItem>
                  <SelectItem value="Graneleiro">Graneleiro</SelectItem>
                  <SelectItem value="Frigorifico">Frigorífico</SelectItem>
                  <SelectItem value="Tanque">Tanque</SelectItem>
                  <SelectItem value="Prancha">Prancha</SelectItem>
                  <SelectItem value="Cacamba">Caçamba</SelectItem>
                  <SelectItem value="Porta-conteiner">Porta-contêiner</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="observacoes">Observações</Label>
              <Textarea
                id="observacoes"
                value={form.observacoes}
                onChange={(e) => setForm({ ...form, observacoes: e.target.value })}
                placeholder="Opcional"
              />
            </div>'''

    novo_inputs = '''            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="codigo">Código *</Label>
                <Input
                  id="codigo"
                  value={form.codigo}
                  onChange={(e) => setForm({ ...form, codigo: e.target.value })}
                  placeholder="CR-001"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="placa">Placa</Label>
                <Input
                  id="placa"
                  value={form.placa || ''}
                  onChange={(e) => setForm({ ...form, placa: e.target.value })}
                  placeholder="ABC-1234"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="modelo">Modelo</Label>
                <Input
                  id="modelo"
                  value={form.modelo || ''}
                  onChange={(e) => setForm({ ...form, modelo: e.target.value })}
                  placeholder="Ex: Graneleiro"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="ano">Ano</Label>
                <Input
                  id="ano"
                  type="number"
                  value={form.ano || ''}
                  onChange={(e) => setForm({ ...form, ano: Number(e.target.value) })}
                  placeholder="2024"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="hodometro_km">Hodômetro (KM)</Label>
                <Input
                  id="hodometro_km"
                  type="number"
                  value={form.hodometro_km || 0}
                  onChange={(e) => setForm({ ...form, hodometro_km: Number(e.target.value) })}
                  placeholder="0"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="tipo">Tipo *</Label>
                <Select
                  value={form.tipo}
                  onValueChange={(v) => setForm({ ...form, tipo: v })}
                >
                  <SelectTrigger id="tipo">
                    <SelectValue placeholder="Selecione" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Bau">Bau</SelectItem>
                    <SelectItem value="Sider">Sider</SelectItem>
                    <SelectItem value="Graneleiro">Graneleiro</SelectItem>
                    <SelectItem value="Frigorifico">Frigorífico</SelectItem>
                    <SelectItem value="Tanque">Tanque</SelectItem>
                    <SelectItem value="Prancha">Prancha</SelectItem>
                    <SelectItem value="Cacamba">Caçamba</SelectItem>
                    <SelectItem value="Porta-conteiner">Porta-contêiner</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="observacoes">Observações</Label>
              <Textarea
                id="observacoes"
                value={form.observacoes}
                onChange={(e) => setForm({ ...form, observacoes: e.target.value })}
                placeholder="Opcional"
              />
            </div>'''

    if busca_inputs in conteudo:
        conteudo = conteudo.replace(busca_inputs, novo_inputs)
        print("⚙️ Frontend: Formulário de Carretas atualizado com sucesso!")
    else:
        print("⚠️ Aviso: O padrão do formulário não foi encontrado. O layout pode ser diferente.")

    # 2. Atualizar as colunas da tabela
    busca_th = '''              <TableHead>Código</TableHead>
              <TableHead>Tipo</TableHead>
              <TableHead>Observações</TableHead>'''
    novo_th = '''              <TableHead>Código</TableHead>
              <TableHead>Placa</TableHead>
              <TableHead>Modelo</TableHead>
              <TableHead>Ano</TableHead>
              <TableHead>KM</TableHead>
              <TableHead>Tipo</TableHead>'''
    
    if busca_th in conteudo:
        conteudo = conteudo.replace(busca_th, novo_th)
        print("⚙️ Frontend: Cabeçalho da tabela atualizado!")

    busca_td = '''                <TableCell className="font-medium">{item.codigo}</TableCell>
                <TableCell>{item.tipo}</TableCell>'''
    novo_td = '''                <TableCell className="font-medium">{item.codigo}</TableCell>
                <TableCell>{item.placa || '-'}</TableCell>
                <TableCell>{item.modelo || '-'}</TableCell>
                <TableCell>{item.ano || '-'}</TableCell>
                <TableCell>{item.hodometro_km || 0}</TableCell>
                <TableCell>{item.tipo}</TableCell>'''
    
    if busca_td in conteudo:
        conteudo = conteudo.replace(busca_td, novo_td)
        print("⚙️ Frontend: Linhas da tabela atualizadas!")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação Visual de Carretas...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    atualizar_tela_carretas(raiz)

    print("🚀 Automação concluída! Faça o commit e push para o Render.")

if __name__ == "__main__":
    executar()