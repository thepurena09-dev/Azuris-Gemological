"""People repositories — admin & customer (Sprint 5). No auth logic here."""

from typing import Optional

from models.people import Admin, Customer
from repositories.domain import DomainRepository


class AdminRepository(DomainRepository[Admin]):
    model = Admin
    collection_name = "admins"

    async def get_by_email(self, email: str) -> Optional[Admin]:
        doc = await self.find_one({"email": email})
        return self.model.from_mongo(doc)


class CustomerRepository(DomainRepository[Customer]):
    model = Customer
    collection_name = "customers"
