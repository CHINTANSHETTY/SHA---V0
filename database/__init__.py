"""
Database Package.
Exposes database manager functions for seamless compatibility.
"""

from database.db_manager import (
    createDatabase,
    createDefaultDoctor,
    validateDoctor,
    saveRecord,
    showAllRecords,
    getRecord,
    updateRecord,
    deleteRecord,
    hash_password,
    verify_password,
)

__all__ = [
    "createDatabase",
    "createDefaultDoctor",
    "validateDoctor",
    "saveRecord",
    "showAllRecords",
    "getRecord",
    "updateRecord",
    "deleteRecord",
    "hash_password",
    "verify_password",
]
