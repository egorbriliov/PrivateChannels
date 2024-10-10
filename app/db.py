import sqlite3
from sqlite3 import Cursor, Connection

from typing import Union, Tuple, Literal, Optional

class DataBasePrivatesConnection:

    # Itiazation
    def __init__(self, table_name: str, table_params: list[list]) -> None:
        self.__table_name: str = table_name
        self.__db_file: str = f"PrivateChannels.db"
        self.__table_params: list[list] = table_params
        
    def __table_create(self) -> bool:
        """ 
        Creates table if does not exists
        Returns: bool
        """
        table_parametrs: str = ", ".join([" ".join(elem) for elem in self.__table_params])
        query: str = f'CREATE TABLE IF NOT EXISTS {self.__table_name} ({table_parametrs})'
        if self.cursor.execute(query): 
            return True            
        else: 
            return False

    def __enter__(self):
        self.__connection: Connection = sqlite3.connect(self.__db_file)
        self.cursor: Cursor = self.__connection.cursor()
        if not self.__table_create():
            print("Was an error while creating table")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.__connection.commit()
        except Exception as E:
            print("Was exception while commit: ", E)
        if self.__connection:
            self.__connection.close()

class TableActiveChannels():
    def __init__(self) -> None:
        self.__table_name: str = "active"
        self.__table_params: list[list[str]] = [
            ["GUILD_ID", "INTEGER"],
            ["CHANNEL_ID", "INTEGER"],
            ["OWNER_ID", "INTEGER"]
        ]
    
    def add(self, guild_id: int, channel_id: int, owner_id: int) -> bool:
        try: 
            with DataBasePrivatesConnection(self.__table_name, self.__table_params) as db:
                query = f"INSERT INTO {self.__table_name} VALUES (?, ?, ?)"
                db.cursor.execute(query, (guild_id, channel_id, owner_id))
            return True
        except Exception as e: 
            print(f"Error adding channel: {e}")
        return False
    
    def delete(self, guild_id: int, channel_id: int) -> bool:
        try: 
            with DataBasePrivatesConnection(self.__table_name, self.__table_params) as db:
                query = f"DELETE FROM {self.__table_name} WHERE GUILD_ID=(?) AND CHANNEL_ID=(?)"
                db.cursor.execute(query, (guild_id, channel_id))
            return True
        except Exception as e: 
            print(f"Error deleting channel: {e}")
        return False

    def get_data(self, guild_id: int, channel_id: int) -> Union[dict[str, int], Literal[False]]:
        try: 
            with DataBasePrivatesConnection(self.__table_name, self.__table_params) as db:
                query = f"SELECT * FROM {self.__table_name} WHERE GUILD_ID = ? AND CHANNEL_ID = ?"
                db.cursor.execute(query, (guild_id, channel_id))
                values: list = list(db.cursor.fetchall()[0])
                keys: list = [params_list[0] for params_list in self.__table_params]
            return dict(zip(keys, values))
        except Exception as e: 
            print(f"Error find channel: {e}")
        return False

    def get_owner_id(self, guild_id: int, channel_id: int) -> Union[Literal[False], int]:  
        try:
            channel_data = self.get_data(guild_id=guild_id, channel_id=channel_id)
            if channel_data:
                owner_id = channel_data.get("OWNER_ID")
                if owner_id:
                    return owner_id
        except Exception as E:
            print("There was an error retrieving channel data")
        return False

    def new_owner(self, guild_id: int, channel_id: int, owner_id: int) -> bool:
        try:
            if self.delete(guild_id=guild_id, channel_id=channel_id) and self.add(guild_id=guild_id, channel_id=channel_id, owner_id=owner_id):
                return True
        except Exception as e:
            print(f"Error set new owner channel: {e}")
        return False
    
    def delete_all_data(self) -> bool:
        try:
            with DataBasePrivatesConnection(self.__table_name, self.__table_params) as db:
                query = f"DROP TABLE {self.__table_name}"
                db.cursor.execute(query)
                return True
        except Exception as e:
            print(f"Error deleting table: {e}")
        return False

class Guild:
    def __init__(self, guild_id: int, channel_id: int, category_id: int) -> None:
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.category_id = category_id
    

class TableConnectedGuilds():
    def __init__(self) -> None:
        self.__table_name: str = "active"
        self.__table_params: list[list[str]] = [
            ["GUILD_ID", "INTEGER"],
            ["CATEGORY_ID", "INTEGER"],
            ["CHANNEL_ID", "INTEGER"]
        ]
        self.guilds_id: list[int] = self.__get_servers_id()
    
    def __get_servers_id(self):
        try:
            with DataBasePrivatesConnection(self.__table_name, self.__table_params) as db:
                query: str = f"SELECT GUILD_ID FROM {self.__table_name}"
                db.cursor.execute(query)
                return True
        except Exception as e:
            print(f"Error getting server ids")
        return False

    def add(self, guild: Guild) -> bool:
        try: 
            with DataBasePrivatesConnection(self.__table_name, self.__table_params) as db:
                query = f"INSERT INTO {self.__table_name} VALUES (?, ?, ?)"
                db.cursor.execute(query, (guild.guild_id, guild.category_id, guild.channel_id))
            return True
        except Exception as e: 
            print(f"Error adding channel: {e}")
        return False
     
    def delete(self, guild: Guild) -> bool:
        try: 
            with DataBasePrivatesConnection(self.__table_name, self.__table_params) as db:
                query = f"DELETE FROM {self.__table_name} WHERE (?)"
                db.cursor.execute(query, (guild.guild_id))
            return True
        except Exception as e: 
            print(f"Error deleting guild: {e}")
        return False
    
    def get_data(self, guild: Guild) -> Union[dict, Literal[False]]:
        try: 
            with DataBasePrivatesConnection(self.__table_name, self.__table_params) as db:
                query = f"SELECT * FROM {self.__table_name} WHERE GUILD_ID = ?"
                db.cursor.execute(query, (guild.guild_id))
                values: list = list(db.cursor.fetchall()[0])
                keys: list = [params_list[0] for params_list in self.__table_params]
            return dict(zip(keys, values))
        except Exception as e: 
            print(f"Error find channel: {e}")
        return False

    def replace_data(self, guild: Guild):
        try:
            if self.delete(guild=guild) and self.add(guild=guild):
                return True
        except Exception as e:
            print(f"Error set new owner channel: {e}")
        return False
    
