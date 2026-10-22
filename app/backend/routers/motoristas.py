from lib.cadastro_base import build_cadastro_router
from models.cadastros import MotoristaCreate, Motorista

router = build_cadastro_router(
    prefix="/motoristas", collection="motoristas", entidade="Motorista",
    create_model=MotoristaCreate, out_model=Motorista,
    unique_field="cnh", unique_label="CNH", acop_field="motorista_id", sort_field="nome"
)
