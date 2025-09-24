import os

import inspect_ai
import inspect_ai.agent
import inspect_ai.dataset
import inspect_ai.scorer
import inspect_ai.solver
import inspect_ai.tool
import inspect_ai.util
from inspect_ai import task

SETUP_SCRIPT = """
import os
import pathlib

pathlib.Path("/root/keyword.txt").write_text(os.environ["SECRET"])
"""


@inspect_ai.solver.solver
def setup_solver() -> inspect_ai.solver.Solver:
    async def solve(
        state: inspect_ai.solver.TaskState,
        generate: inspect_ai.solver.Generate  # pyright: ignore[reportUnusedParameter]
    ) -> inspect_ai.solver.TaskState:
        result = await inspect_ai.util.sandbox().exec(
            ["python", "-c", SETUP_SCRIPT],
            env={"SECRET": os.environ["SECRET"]},
        )
        assert result.success, result.stderr
        return state

    return solve


@task
def env_test() -> inspect_ai.Task:
    return inspect_ai.Task(
        dataset=[
            inspect_ai.dataset.Sample(
                input="Find and submit the word in /root/keyword.txt.",
                target=os.environ["SECRET"],
            ),
        ],
        sandbox="docker",
        setup=setup_solver(),
        scorer=inspect_ai.scorer.includes(),
        solver=inspect_ai.agent.react(tools=[inspect_ai.tool.bash()]),
    )
