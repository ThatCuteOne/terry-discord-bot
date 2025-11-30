import duckdb
import json
from pydantic import BaseModel, ValidationError
from typing import List, Optional

setting_types = {
    "quote_channel":{
        "type": "channel",
        "native_type": str
    },
    "auto_thread_channels":{
        "type": "channel",
        "native_type": list
    }
}


class Config(BaseModel):
    quote_channel: int = -1
    auto_thread_channels: List[int] = []


class TerrySettings():

    def __init__(self):
        self.database = duckdb.connect("botsettings.db")
        self._init_database()
    def _init_database(self):
        self.database.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id BIGINT PRIMARY KEY,
                settings JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    async def init_guild_entry(self,guild_id):
        self.database.execute(f"""
                              INSERT INTO guild_settings (guild_id,settings)
                              VALUES ({guild_id},'{Config().model_dump_json()}')
                              """
                        )

    async def get_settings_for_guild(self,guild_id):
        result = self.database.execute(f"SELECT settings FROM guild_settings WHERE guild_id = {guild_id}").fetchone()
        if result and result[0]:
            return Config(**json.loads(result[0]))
        
        await self.init_guild_entry(guild_id)
        return Config()

    async def set_setting_for_guild(self,guild_id,key,value):
        if key not in Config().model_dump().keys():
            raise ValueError(f"{key} is not a valid setting")
        settings = await self.get_settings_for_guild(guild_id)
        settings_dict = settings.model_dump()
        settings_dict[key] = value
        await self.replace_settings(guild_id,Config(**settings_dict))

    async def replace_settings(self,guild_id,settings:Config):
        self.database.execute(f"""
                        UPDATE guild_settings
                        SET settings = '{settings.model_dump_json()}'
                        WHERE guild_id = {guild_id}
                    """)
