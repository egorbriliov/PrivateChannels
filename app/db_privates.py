from pymongo import MongoClient
import pymongo


class CollectionActivePrivates:

    def __init__(self):
        self.client: MongoClient = MongoClient('mongodb://localhost:27017')
        self.db: client_session = self.client['PrivateChannels']
        self.collection: collection = self.db['privates']

    def new_channel(self, guild_id: int, channel_id: int, owner_id: int):
        self.collection.insert_one({"guild_id": guild_id,
                                    "channel_id": channel_id,
                                    "owner_id": owner_id})

    def delete_channel(self, guild_id: int, channel_id: int):
        self.collection.delete_one(filter={
            "guild_id": guild_id,
            "channel_id": channel_id})

    def get_channel_data(self, guild_id: int, channel_id: int):
        return self.collection.find_one({
            "guild_id": guild_id,
            "channel_id": channel_id
        })

    def get_owner_id(self, guild_id: int, channel_id: int):
        return (self.get_channel_data(guild_id=guild_id, channel_id=channel_id)).get("owner_id")

    def new_data_channel(self, guild_id: int, channel_id: int, **kwargs):
        if kwargs:
            data = self.get_channel_data(guild_id=guild_id, channel_id=channel_id)
            for key in kwargs.keys():
                data[key] = kwargs[key]
            self.collection.replace_one({
                "guild_id": guild_id,
                "channel_id": channel_id
            }, replacement=data)

    def delete_all_data(self):
        self.collection.delete_many({})


class CollectionServers:
    def __init__(self):
        # Initializing
        self.__client = MongoClient('mongodb://localhost:27017')
        self.__db = self.__client['PrivateChannels']
        self.__collection = self.__db['servers']
        # Global attributes
        self.servers_id: list[int, ...] = self.__servers()

    def __servers(self) -> list[int, ...]:
        """Returned list of all servers in database"""
        cursor: pymongo.cursor = self.__collection.find({}, {"server_id": 1})
        documents: list[dict, ...] = [document for document in cursor]
        guilds_id: list[int, ...] = [document.get("server_id") for document in documents]
        return guilds_id

    def add_new_server(self, server_id: int, category_id: int, channel_id: int) -> None:
        """Метод регистрирует новый сервер и созданную под него категорию"""
        self.__collection.insert_one({
            "server_id": server_id,
            "category_id": category_id,
            "channel_id": channel_id
        })

    def delete_server(self, server_id: int) -> None:
        """Метод удаляет сервер"""
        self.__collection.delete_one({
            "server_id": server_id
        })

    def get_server_data(self, server_id: int) -> dict:
        """Метод получает """
        return self.__collection.find_one({"server_id": server_id})

    def new_server_data(self, server_id: int, category_id=None, channel_id=None):
        """Обновляет значение для данных о сервере"""
        last_server_data = self.get_server_data(server_id=server_id)
        if category_id:
            last_server_data["category_id"] = category_id
        if channel_id:
            last_server_data["channel_id"] = channel_id
        self.__collection.replace_one({"server_id": server_id}, last_server_data)
