from typing import Optional, Dict, Any
from app.infrastructure.mongo import channels_col

class ChannelsRepository:
    def __init__(self):
        self.col = channels_col()

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        return self.col.find_one({"name": name})

    # índices sugeridos:
    # db.channels.createIndex({name:1},{unique:true})
