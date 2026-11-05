import os

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "VeiculoDetalhe.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Atualiza as chamadas do React Query para a nova rota unificada
c = c.replace(
    'const { data: veiculo } = useQuery({ queryKey: ["veiculo", id], queryFn: () => apiGet<any>(`/veiculos/${id}`) });',
    'const { data: detalhes, isLoading } = useQuery({ queryKey: ["veiculo-detalhes", id], queryFn: () => apiGet<any>(`/veiculos/detalhes/${id}`) });'
)

# Remove as 3 queries antigas (abastecimentos, manutencoes, pneus) pois tudo vem num pacote só agora
c = c.replace('const { data: abastecimentos = [] } = useQuery({ queryKey: ["abastecimentos", id], queryFn: () => apiGet<any[]>(`/abastecimentos?veiculo_id=${id}`) });', '')
c = c.replace('const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes", id], queryFn: () => apiGet<any[]>(`/manutencoes?veiculo_id=${id}`) });', '')
c = c.replace('const { data: pneus = [] } = useQuery({ queryKey: ["pneus", id], queryFn: () => apiGet<any[]>(`/pneus?veiculo_id=${id}`) });', '')

# Descompacta os dados
descompactar = '''
  const veiculo = detalhes?.veiculo;
  const abastecimentos = detalhes?.abastecimentos || [];
  const manutencoes = detalhes?.manutencoes || [];
  const pneus = detalhes?.pneus || [];
'''
c = c.replace('const { data: detalhes, isLoading } = useQuery({ queryKey: ["veiculo-detalhes", id], queryFn: () => apiGet<any>(`/veiculos/detalhes/${id}`) });', 'const { data: detalhes, isLoading } = useQuery({ queryKey: ["veiculo-detalhes", id], queryFn: () => apiGet<any>(`/veiculos/detalhes/${id}`) });\n' + descompactar)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Frontend: Página VeiculoDetalhe agora consome a rota unificada.")