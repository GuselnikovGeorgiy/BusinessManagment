from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Never, Optional

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from sqlalchemy.engine import Result


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, *args: Any, **kwargs: Any) -> Never:
        raise NotImplementedError

    @abstractmethod
    async def add_one_and_get_id(self, *args: Any, **kwargs: Any) -> Never:
        raise NotImplementedError

    async def add_one_and_get_object(self, *args: Any, **kwargs: Any) -> Never:
        raise NotImplementedError

    async def get_by_query_one_or_none(self, *args: Any, **kwargs: Any) -> Never:
        raise NotImplementedError

    @abstractmethod
    async def get_by_query_all(self, *args: Any, **kwargs: Any) -> Never:
        raise NotImplementedError

    @abstractmethod
    async def update_one_by_id(self, *args: Any, **kwargs: Any) -> Never:
        raise NotImplementedError

    @abstractmethod
    async def delete_one_by_id(self, *args: Any, **kwargs: Any) -> Never:
        raise NotImplementedError

    @abstractmethod
    async def delete_all(self) -> None:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_one(self, **kwargs: Any) -> None:
        query = insert(self.model).values(**kwargs)
        await self.session.execute(query)

    async def add_one_and_get_id(self, **kwargs: Any) -> int:
        query = insert(self.model).values(**kwargs).returning(self.model.id)
        obj_id: Result = await self.session.execute(query)
        return obj_id.scalar_one()

    async def add_one_and_get_object(self, **kwargs: Any) -> model:
        query = insert(self.model).values(**kwargs).returning(self.model)
        obj: Result = await self.session.execute(query)
        return obj.scalar_one()

    async def get_by_id(self, obj_id: int) -> Optional[Any]:
        return await self.session.get(self.model, obj_id)

    async def get_by_query_one_or_none(self, **kwargs: Any) -> Any | None:
        query = select(self.model).filter_by(**kwargs)
        res: Result = await self.session.execute(query)
        return res.scalar_one_or_none()

    async def get_by_query_all(self, **kwargs: Any) -> Sequence[model]:
        query = select(self.model).filter_by(**kwargs)
        res: Result = await self.session.execute(query)
        return res.scalars().all()

    async def update_one_by_id(self, obj_id: int, **kwargs: Any) -> model:
        query = update(self.model).filter(self.model.id == obj_id).values(**kwargs).returning(self.model)
        obj: Result = await self.session.execute(query)
        return obj.scalar_one()

    async def delete_one_by_id(self, obj_id: int) -> None:
        query = delete(self.model).filter(self.model.id == obj_id)
        await self.session.execute(query)

    async def delete_by_query(self, **kwargs) -> None:
        query = delete(self.model).filter_by(**kwargs)
        await self.session.execute(query)
        await self.session.commit()

    async def delete_all(self) -> None:
        query = delete(self.model)
        await self.session.execute(query)
        await self.session.commit()
