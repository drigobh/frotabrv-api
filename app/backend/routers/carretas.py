from lib.cadastro_base import build_cadastro_router
from models.cadastros import CarretaCreate, Carreta

router = build_cadastro_router(
    prefix="/carretas", collection="carretas", entidade="Carreta",
    create_model=CarretaCreate, out_model=Carreta,
    unique_field="codigo", unique_label="Código", acop_field="carreta_id", sort_field="codigo"
)
