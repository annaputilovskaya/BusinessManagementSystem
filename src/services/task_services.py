from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, Task, Comment
from src.schemas.task_schemas import TaskCreate, TaskModify, TaskUpdate, CommentCreate


async def add_task(
        task_in: TaskCreate,
        session: AsyncSession,
        user: User
) -> Task:
    """
    Add a new task to the database.

    Args:
        task_in (TaskCreate): The input details of the task to be created.
        session (AsyncSession): The database session for executing the operation.
        user (User): The user associated with the task creation.

    Returns:
        Task: The created Task object.

    Raises:
        HTTPException: If the user does not have the necessary permissions
            to access the teams, a 403 Forbidden error is raised.
    """

    if user and user.is_manager:
        if task_in.user_id:
            executor = await session.scalar(select(User).where(User.id == task_in.user_id, User.team_id == user.team_id))
            if executor:
                new_task = Task(
                    name=task_in.name,
                    description=task_in.description,
                    deadline=task_in.deadline,
                    team_id=user.team_id,
                    user_id=executor.id                )
            else:
                new_task = Task(
                    name=task_in.name,
                    description=task_in.description,
                    deadline=task_in.deadline,
                    team_id=user.team_id
                )
        else:
            new_task = Task(
                name=task_in.name,
                description=task_in.description,
                deadline=task_in.deadline,
                team_id=user.team_id,
            )
        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)
        return new_task
    else:
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Not enough permissions for the action."}
        )


async def get_all_tasks(
        session: AsyncSession,
        user: User
) -> list[Task]:
    """
    Retrieve all tasks associated with a specific user.

    Args:
        session (AsyncSession): The database session to be used for querying.
        user (User): The user for whom tasks are to be retrieved.

    Returns:
        list[Task]: A list of Task objects associated with the specified user.

    Raises:
        HTTPException: If the user does not have the necessary permissions
            to access the teams, a 403 Forbidden error is raised.
    """
    if user:
        if user.is_manager:
            tasks = await session.scalars(select(Task).where(Task.team_id == user.team_id))
        else:
            tasks = await session.scalars(select(Task).where(Task.user_id == user.id))
        return list(tasks)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Not enough permissions for the action."}
        )


async  def get_task_by_id(
        task_id: int,
        session: AsyncSession,
        user: User
) -> Task:
    """
    Retrieve a task from the database by ID.

    Args:
        task_id (int): The ID of the task to retrieve.
        session (AsyncSession): The database session to be used for querying.
        user (User): The user for whom tasks are to be retrieved.

    Returns:
        Task: A Task object associated with the specified task ID.

    Raises:
        HTTPException:
        - If the user is not an active verified user, a 403 Forbidden error is raised.
        - If the user does not have the necessary permissions to access the task,
            or task with such ID does not exist in the database,
            a 404 Not found error is raised.

    """
    if user:
        if user.is_manager:
            task = await session.scalar(select(Task).where(Task.id == task_id, Task.team_id == user.team_id))
        else:
            task = await session.scalar(select(Task).where(Task.id == task_id, Task.user_id == user.id))

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "No tasks found."}
            )
        return task
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Not enough permissions for the action."}
        )


async def change_task(
        task_in: TaskModify,
        task: Task,
        session: AsyncSession,
        user: User
) -> Task:

    """
    Modify an existing task based on the provided input.

    Updates a task's attributes using the values
    provided in the `task_in` parameter.

    Args:
        task_in (TaskModify): An object containing the new values
            for the task attributes.
        task (Task): The task object to be modified.
        session (AsyncSession): The database session used for committing the changes.
        user (User): The user requesting the modification, used for
            authorization checks.

    Returns:
        Task: The updated task object after the changes have been applied.
    """
    task_dict = task_in.model_dump(exclude_unset=True)
    if task_in.user_id:
        executor = await session.scalar(select(User).where(User.id == task_in.user_id, User.team_id == user.team_id))
        if not executor:
            del task_dict["user_id"]
    for name, value in task_dict.items():
        setattr(task, name, value)
    await session.commit()
    await session.refresh(task)
    return task


async def progress_task(
        task_in: TaskUpdate,
        task: Task,
) -> Task:

    """
    Updates the progress of a given task.

    Takes a task update input and a current task instance,
    processes the update, and returns the updated task.

    Args:
        task_in (TaskUpdate): An object containing the details of the task update,
            such as status changes.
        task (Task): The current task instance that is to be updated.

    Returns:
        Task: The updated task instance after applying the progress update.
    """
    task.status = task_in.status
    return task


def create_comment(
        comment_in: CommentCreate,
        task_id: int,
        user: User
) -> Comment:

    """
    Creates a new comment for a specified task.

    Args:
        comment_in (CommentCreate): An object containing the text of the comment.
        task_id (int): The ID of the task for which the comment is being created.
        user (User): The user who is creating the comment.

    Returns:
        Comment: The newly created comment associated with the specified task.
    """
    new_comment = Comment(text=comment_in.text, task_id=task_id, user_id=user.id)
    return new_comment
