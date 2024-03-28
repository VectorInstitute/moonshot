import datetime
import glob
import json
import os
from pathlib import Path
from typing import Iterator

from moonshot.src.configs.env_variables import EnvironmentVars
from moonshot.src.storage.db.db_accessor import DBAccessor
from moonshot.src.storage.db.db_manager import DatabaseManager


class Storage:
    @staticmethod
    def create_object(
        obj_type: str, obj_id: str, obj_info: dict, obj_extension: str
    ) -> None:
        """
        Writes the object information to a JSON file.

        Args:
            obj_type (str): The type of the object (e.g., 'recipe', 'cookbook').
            obj_id (str): The ID of the object.
            obj_info (dict): A dictionary containing the object information.
            obj_extension (str): The file extension (e.g., 'json', 'py').
        """
        obj_filepath = f"{getattr(EnvironmentVars, obj_type)}/{obj_id}.{obj_extension}"
        with open(obj_filepath, "w") as json_file:
            json.dump(obj_info, json_file, indent=2)

    @staticmethod
    def read_object(obj_type: str, obj_id: str, obj_extension: str) -> dict:
        """
        Reads the object information from a JSON file.

        Args:
            obj_type (str): The type of the object (e.g., 'recipe', 'cookbook').
            obj_id (str): The ID of the object.
            obj_extension (str): The file extension (e.g., 'json', 'py').

        Returns:
            dict: A dictionary containing the object information.
        """
        obj_filepath = f"{getattr(EnvironmentVars, obj_type)}/{obj_id}.{obj_extension}"
        with open(obj_filepath, "r", encoding="utf-8") as json_file:
            obj_info = json.load(json_file)
        return obj_info

    @staticmethod
    def delete_object(obj_type: str, obj_id: str, obj_extension: str) -> None:
        """
        Deletes an object.

        Args:
            obj_type (str): The type of the object (e.g., 'recipe', 'cookbook').
            obj_id (str): The ID of the object.
            obj_extension (str): The file extension (e.g., 'json', 'py').
        """
        obj_filepath = Path(
            f"{getattr(EnvironmentVars, obj_type)}/{obj_id}.{obj_extension}"
        )
        if obj_filepath.exists():
            obj_filepath.unlink()
        else:
            raise RuntimeError(f"No {obj_type} found with ID: {obj_id}")

    @staticmethod
    def get_objects(obj_type: str, obj_extension: str) -> Iterator[str]:
        """
        Retrieves all the object files with the specified extension.

        Args:
            obj_type (str): The type of the object (e.g., 'recipe', 'cookbook').
            obj_extension (str): The file extension (e.g., 'json', 'py').

        Returns:
            Iterator[str]: An iterator that yields the filepaths of the object files.
        """
        return glob.iglob(f"{getattr(EnvironmentVars, obj_type)}/*.{obj_extension}")

    @staticmethod
    def get_creation_datetime(obj_type: str, obj_id: str, obj_extension: str):
        """
        Retrieves the creation datetime of an object.

        Args:
            obj_type (str): The type of the object (e.g., 'recipe', 'cookbook').
            obj_id (str): The ID of the object.
            obj_extension (str): The file extension (e.g., 'json', 'py').

        Returns:
            datetime: The creation datetime of the object.
        """
        obj_filepath = f"{getattr(EnvironmentVars, obj_type)}/{obj_id}.{obj_extension}"
        creation_timestamp = os.path.getctime(obj_filepath)
        creation_datetime = datetime.datetime.fromtimestamp(creation_timestamp)
        return creation_datetime

    @staticmethod
    def get_filepath(obj_type: str, obj_id: str, obj_extension: str) -> str:
        """
        Constructs the file path for the object.

        Args:
            obj_type (str): The type of the object (e.g., 'recipe', 'cookbook').
            obj_id (str): The ID of the object.
            obj_extension (str): The file extension (e.g., 'json', 'py').

        Returns:
            str: The file path of the object.
        """
        return f"{getattr(EnvironmentVars, obj_type)}/{obj_id}.{obj_extension}"

    @staticmethod
    def is_object_exists(obj_type: str, obj_id: str, obj_extension: str) -> bool:
        """
        Checks if the object exists.

        Args:
            obj_type (str): The type of the object (e.g., 'runner', 'recipe', 'cookbook').
            obj_id (str): The ID of the object.
            obj_extension (str): The file extension (e.g., 'json', 'py').

        Returns:
            bool: True if the object exists, False otherwise.
        """
        obj_filepath = Path(
            f"{getattr(EnvironmentVars, obj_type)}/{obj_id}.{obj_extension}"
        )
        return obj_filepath.exists()

    @staticmethod
    def create_database_connection(
        obj_type: str, obj_id: str, obj_extension: str
    ) -> DBAccessor:
        """
        Creates a database connection for the object.

        Args:
            obj_type (str): The type of the object (e.g., 'runner', 'recipe', 'cookbook').
            obj_id (str): The ID of the object.
            obj_extension (str): The file extension (e.g., 'json', 'py').

        Returns:
            DBAccessor: The database accessor instance.
        """
        database_file = Path(Storage.get_filepath(obj_type, obj_id, obj_extension))
        database_instance = DatabaseManager.create_connection(str(database_file))
        if not database_instance:
            raise RuntimeError("db instance is not initialised.")
        return database_instance

    @staticmethod
    def close_database_connection(database_instance: DBAccessor) -> None:
        """
        Closes the database connection.

        Args:
            database_instance (DBAccessor): The instance of the database accessor.

        Returns:
            None
        """
        if database_instance:
            database_instance.close_connection()
        else:
            raise RuntimeError("Database instance is not initialised.")

    @staticmethod
    def create_database_table(
        database_instance: DBAccessor, sql_create_table: str
    ) -> None:
        """
        Creates a table in the database.

        This method is used to create a table in the database. If the database instance is not initialised,
        it raises a RuntimeError. Otherwise, it calls the create_table method of the database instance.

        Args:
            database_instance (DBAccessor): The database accessor instance.
            sql_create_table (str): The SQL query to create a table.

        Returns:
            None
        """
        if database_instance:
            database_instance.create_table(sql_create_table)
        else:
            raise RuntimeError("Database instance is not initialised.")

    @staticmethod
    def create_database_record(
        database_instance: DBAccessor, data: tuple, sql_create_record: str
    ) -> None:
        """
        Creates a record in the database.

        This method is used to create a record in the database. If the database instance is not initialised,
        it raises a RuntimeError. Otherwise, it calls the create_record method of the database instance.

        Args:
            database_instance (DBAccessor): The database accessor instance.
            data (tuple): The data to be inserted.
            sql_create_record (str): The SQL query to create a record.

        Returns:
            None
        """
        if database_instance:
            database_instance.create_record(data, sql_create_record)
        else:
            raise RuntimeError("Database instance is not initialised.")

    @staticmethod
    def update_database_record(
        database_instance: DBAccessor, data: tuple, sql_update_record: str
    ) -> None:
        """
        Updates a record in the database.

        This method is used to update a record in the database. If the database instance is not initialised,
        it raises a RuntimeError. Otherwise, it calls the update_record method of the database instance.

        Args:
            database_instance (DBAccessor): The database accessor instance.
            data (tuple): The data to be updated.
            sql_update_record (str): The SQL query to update a record.

        Returns:
            None
        """
        if database_instance:
            database_instance.update_record(data, sql_update_record)
        else:
            raise RuntimeError("Database instance is not initialised.")
