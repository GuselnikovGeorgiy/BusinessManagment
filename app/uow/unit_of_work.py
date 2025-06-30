import functools
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, NoReturn, Optional, Callable, Awaitable

from app.database import async_session_maker
from app.repositories.company import CompanyRepository
from app.repositories.department import DepartmentRepository
from app.repositories.invite import InviteRepository
from app.repositories.position import PositionRepository
from app.repositories.role import RoleAssignmentRepository
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository


class AbstractUnitOfWork(ABC):

    user: UserRepository

    @abstractmethod
    def __init__(self) -> NoReturn:
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> NoReturn:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> NoReturn:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> NoReturn:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> NoReturn:
        raise NotImplementedError


class UnitOfWork(AbstractUnitOfWork):

    def __init__(self) -> None:
        self.session_factory = async_session_maker

    async def __aenter__(self) -> None:
        self.session = self.session_factory()
        self.user = UserRepository(self.session)
        self.company = CompanyRepository(self.session)
        self.position = PositionRepository(self.session)
        self.invite = InviteRepository(self.session)
        self.department = DepartmentRepository(self.session)
        self.role_assignment = RoleAssignmentRepository(self.session)
        self.task = TaskRepository(self.session)

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()


AsyncFunc = Callable[..., Awaitable[Any]]


def transaction_mode(func: AsyncFunc) -> AsyncFunc:

    @functools.wraps(func)
    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        async with self.uow:
            return await func(self, *args, **kwargs)

    return wrapper


def get_uow() -> UnitOfWork:
    return UnitOfWork()
