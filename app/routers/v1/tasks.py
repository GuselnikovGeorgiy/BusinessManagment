from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache

from app.auth.auth_utils import get_current_user
from app.schemas.auth import UserToken
from app.schemas.tasks import TaskCreate, TaskUpdate
from app.services.task import TaskService
from app.uow.unit_of_work import UnitOfWork, get_uow

tasks_router = APIRouter(prefix="/v1/tasks", tags=["Tasks"])


@tasks_router.post("/")
async def create_task(
    task_data: TaskCreate,
    current_user: UserToken = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    service = TaskService(uow)
    try:
        task = await service.create_task(
            title=task_data.title,
            description=task_data.description,
            author_id=current_user.user_id,
            responsible_id=task_data.responsible_id,
            observer_ids=task_data.observer_ids,
            executor_ids=task_data.executor_ids,
            deadline=task_data.deadline,
            estimated_time=task_data.estimated_time,
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@cache(expire=100)
@tasks_router.get("/{task_id}")
async def get_task(
    task_id: int,
    current_user: UserToken = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    service = TaskService(uow)
    try:
        return await service.get_task(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@tasks_router.put("/{task_id}")
async def update_task(
    task_id: int,
    updates: TaskUpdate,
    current_user: UserToken = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    service = TaskService(uow)
    try:
        return await service.update_task(task_id, updates.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@tasks_router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: UserToken = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    service = TaskService(uow)
    try:
        await service.delete_task(task_id)
        return {"detail": "Task deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
