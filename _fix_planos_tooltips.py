import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PLANOS_TOOLTIPS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "PlanosManutencao.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/PlanosManutencao.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "PlanosManutencao.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Corrigir a formatação da data para dd/mm/yyyy
    c = c.replace(
        'value={form.data_abertura}',
        'value={form.data_abertura ? form.data_abertura.split("-").reverse().join("/") : ""}'
    )
    print("✅ Data formatada para dd/mm/yyyy.")

    # 2. Adicionar os Tooltips (ícones de ajuda) nos labels
    # Importar o ícone HelpCircle
    if 'HelpCircle' not in c.split('lucide-react')[0]:
        c = c.replace(
            'import { Wrench, Plus, Pencil, Trash2, Info, User, Gauge, Calendar }',
            'import { Wrench, Plus, Pencil, Trash2, Info, User, Gauge, Calendar, HelpCircle }'
        )

    # Tooltip: Tipo de Gatilho
    c = c.replace(
        '<Label className="text-xs text-slate-400">Tipo de Gatilho</Label>',
        '''<Label className="text-xs text-slate-400 flex items-center gap-1">
                  Tipo de Gatilho
                  <div className="group relative">
                    <HelpCircle className="size-3 text-slate-500 cursor-help" />
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-64 bg-slate-800 border border-slate-700 text-slate-200 text-xs p-3 rounded-lg shadow-xl z-50">
                      <p className="font-bold mb-1 text-sky-400">Qual a base para a próxima manutenção?</p>
                      <ul className="space-y-1 text-slate-400">
                        <li><strong className="text-slate-300">KM:</strong> Ideal para motores, transmissão e rodagem (baseado no hodômetro).</li>
                        <li><strong className="text-slate-300">Horas:</strong> Essencial para equipamentos com PTO, bombas ou geradores.</li>
                        <li><strong className="text-slate-300">Tempo:</strong> Para itens que degradam com o tempo (ex: óleo, borrachas), independente do uso.</li>
                      </ul>
                    </div>
                  </div>
                </Label>'''
    )

    # Tooltip: Recorrência
    c = c.replace(
        '<Label className="text-xs text-slate-400">Recorrência</Label>',
        '''<Label className="text-xs text-slate-400 flex items-center gap-1">
                  Recorrência
                  <div className="group relative">
                    <HelpCircle className="size-3 text-slate-500 cursor-help" />
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-64 bg-slate-800 border border-slate-700 text-slate-200 text-xs p-3 rounded-lg shadow-xl z-50">
                      <p className="font-bold mb-1 text-sky-400">Como este serviço se repete?</p>
                      <ul className="space-y-1 text-slate-400">
                        <li><strong className="text-slate-300">Periódico:</strong> O serviço se repete a cada intervalo definido (ex: troca de óleo a cada 20.000 km).</li>
                        <li><strong className="text-slate-300">Vitalício:</strong> O serviço é feito uma única vez na vida útil do ativo (ex: descarbonização, troca de correia dentada).</li>
                      </ul>
                    </div>
                  </div>
                </Label>'''
    )

    # Tooltip: Intervalo
    c = c.replace(
        '<Label className="text-xs text-slate-400">Intervalo</Label>',
        '''<Label className="text-xs text-slate-400 flex items-center gap-1">
                  Intervalo
                  <div className="group relative">
                    <HelpCircle className="size-3 text-slate-500 cursor-help" />
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-64 bg-slate-800 border border-slate-700 text-slate-200 text-xs p-3 rounded-lg shadow-xl z-50">
                      <p className="font-bold mb-1 text-sky-400">Qual a frequência?</p>
                      <p className="text-slate-400">Digite o número que representa a distância (km), tempo (horas) ou período (dias/meses/anos) entre cada manutenção.</p>
                    </div>
                  </div>
                </Label>'''
    )

    # Tooltip: Unidade de Tempo
    c = c.replace(
        '<Label className="text-xs text-slate-400">Unidade de Tempo</Label>',
        '''<Label className="text-xs text-slate-400 flex items-center gap-1">
                    Unidade de Tempo
                    <div className="group relative">
                      <HelpCircle className="size-3 text-slate-500 cursor-help" />
                      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-64 bg-slate-800 border border-slate-700 text-slate-200 text-xs p-3 rounded-lg shadow-xl z-50">
                        <p className="font-bold mb-1 text-sky-400">Unidade do intervalo</p>
                        <p className="text-slate-400">Escolha se o intervalo é contado em dias, meses ou anos.</p>
                      </div>
                    </div>
                  </Label>'''
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Tooltips adicionados e data formatada.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")
    