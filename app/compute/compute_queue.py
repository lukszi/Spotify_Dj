from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from typing import Callable, List, Dict, Optional


class ComputeQueue:
    queue: Dict[str, ComputeTask]
    pool: ProcessPoolExecutor

    def __init__(self):
        self.queue = {}
        self.pool = ProcessPoolExecutor()

    def queue_task(self, task: ComputeTask) -> str:
        """
        Queue a task and return the task id
        :param task: The task to be queued
        :return: The task id
        """
        task_id = self.generate_task_id()
        self.queue[task_id] = task
        return task_id

    def generate_task_id(self):
        """
        Generate a unique task id
        :return: The task id
        """
        return str(len(self.queue) + 1)

    def get_task(self, task_id: str) -> Optional[ComputeTask]:
        """
        Get a task by its id
        :param task_id: The task id
        :return: The task
        """
        if task_id not in self.queue:
            return None
        return self.queue[task_id]

    async def run_process_thread(self, task_id: str):
        pass


class ComputeTask:
    steps: List[ComputeStep]
    progress: TaskProgress


class ComputeStep:
    name: str
    description: str
    method: Callable
    arguments: Dict


class Argument:
    name: str
    previous_step_result: bool
    value: any

    def __init__(self, name: str,  value: any = None, previous_step_result: bool = False):
        self.name = name
        self.previous_step_result = previous_step_result
        self.value = value


class TaskProgress:
    status: str
