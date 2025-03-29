import json
import pymysql
from db import get_connection, TABLE_NAME
from agents import function_tool


@function_tool
async def add_information_initial(task_agent_name: str, task: str, result: str) -> None:
    """
    Add a complete entry to the task dictionary.

    Parameters:
    - task_agent_name (str): Name of the agent executing the task.
    - task (str): Description or identifier of the task.
    - result (str): The result or output of the task.

    Behavior:
    - If an identical entry (task_agent_name, task, result) already exists in the dictionary, raise ValueError.
    - Otherwise, add a new entry to the task dictionary.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"SELECT 1 FROM {TABLE_NAME} WHERE task_agent_name=%s AND task=%s AND result=%s",
                (task_agent_name, task, result)
            )
            if cursor.fetchone():
                raise ValueError("Record already exists.")

            cursor.execute(
                f"INSERT INTO {TABLE_NAME} (task_agent_name, task, result) VALUES (%s, %s, %s)",
                (task_agent_name, task, result)
            )
        conn.commit()
    finally:
        conn.close()


@function_tool
async def add_information(task_agent_name: str, task: str) -> None:
    """
    Add a new task entry to the task dictionary with an empty result field.

    Parameters:
    - task_agent_name (str): Name of the agent creating the task.
    - task (str): Task identifier or instruction.

    Behavior:
    - If a task with the same agent and name already exists, raise ValueError.
    - Otherwise, add the new task with an empty result field.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"SELECT 1 FROM {TABLE_NAME} WHERE task_agent_name=%s AND task=%s",
                (task_agent_name, task)
            )
            if cursor.fetchone():
                raise ValueError(f"Task '{task}' already exists.")

            cursor.execute(
                f"INSERT INTO {TABLE_NAME} (task_agent_name, task, result) VALUES (%s, %s, '')",
                (task_agent_name, task)
            )
        conn.commit()
    finally:
        conn.close()


@function_tool
async def get_information() -> str:
    """
    Retrieve all entries from the task dictionary.

    Returns:
    - str: A JSON-formatted string representing a list of task dictionary entries.
           Each entry includes task_agent_name, task, and result.
    """
    conn = get_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(f"SELECT task_agent_name, task, result FROM {TABLE_NAME}")
            rows = cursor.fetchall()
            return json.dumps(rows, ensure_ascii=False)
    finally:
        conn.close()


@function_tool
async def update_information(task_agent_name: str, task: str, result: str) -> None:
    """
    Update the result field for an existing entry in the task dictionary.

    Parameters:
    - task_agent_name (str): Name of the agent responsible for the task.
    - task (str): Identifier of the task to be updated.
    - result (str): The updated result or outcome.

    Behavior:
    - If no entry with the given agent and task exists, raise ValueError.
    - Otherwise, update the corresponding result field in the task dictionary.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"SELECT 1 FROM {TABLE_NAME} WHERE task_agent_name=%s AND task=%s",
                (task_agent_name, task)
            )
            if not cursor.fetchone():
                raise ValueError(f"No entry found for agent '{task_agent_name}' with task '{task}'.")

            cursor.execute(
                f"UPDATE {TABLE_NAME} SET result=%s WHERE task_agent_name=%s AND task=%s",
                (result, task_agent_name, task)
            )
        conn.commit()
    finally:
        conn.close()
