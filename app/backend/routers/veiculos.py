from lib.cadastro_base import build_cadastro_router
from models.cadastros import VeiculoCreate, Veiculo

router = build_cadastro_router(
    prefix="/veiculos", collection="veiculos", entidade="Veículo",
    create_model=VeiculoCreate, out_model=Veiculo,
    unique_field="placa", unique_label="Placa", acop_field="veiculo_id", sort_field="placa"
)
