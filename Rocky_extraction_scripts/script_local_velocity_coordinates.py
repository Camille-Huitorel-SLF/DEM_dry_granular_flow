import os
import sys
import json
from pathlib import Path

from typing import TYPE_CHECKING, Iterable, Optional, Tuple, Union, List, Dict
from typing_extensions import Protocol

import pandas as pd
import numpy as np


from rocky30.plugins.api.rocky_api_application import RockyApiApplication as app
from rocky30.plugins.api.ra_project import RAProject
from rocky30.plugins.api.ra_study import RAStudy


if TYPE_CHECKING:
    from rocky30.plugins.api.rocky_api_application import RockyApiApplication as api

OUTPUT_PATH = Path(os.environ["EXTRACT_OUTPUT_PATH"])


class TimeSet(Protocol):
    pass


class TimeStep(Protocol):
    second: float

    def GetTimeSet(self) -> "TimeSet":
        """Get timeset."""

    def GetTimeIndex(self, timeset: "TimeSet") -> int:
        """Get time index for the given timeset."""


Scalar = Union[int, float, str]
ColumnsGroups = Dict[str, List[Scalar]]
ScalarOrGroup = Dict[str, Union[Scalar, ColumnsGroups]]
DumpItem = Union[Scalar, ColumnsGroups, Dict[int, ScalarOrGroup]]
DataDump = Dict[str, DumpItem]


class RockyDumper:
    def __init__(self) -> None:
        self.timesteps: Dict[int, ScalarOrGroup] = {}

    def log_dataframe(
        self,
        dataframe_name: str,
        dataframe: pd.DataFrame,
        timestep: Optional["TimeStep"] = None,
    ):
        self._store(dataframe_name, timestep, dataframe.to_dict(orient="list"))

    def log_scalar(
        self,
        name: str,
        value: Union[float, int],
        timestep: Optional["TimeStep"] = None,
    ):
        self._store(name, timestep, value)

    @property
    def data(self) -> DataDump:
        data: DataDump = {}
        data["timesteps"] = self.timesteps
        return data

    def dump(self, dump_path: Path, index: str):
        if dump_path.is_dir():
            dump_path /= f"local_velocities_coordinates_xsize{index}.json"
        with open(dump_path, "w") as file:
            json.dump(self.data, file)

    def _store(
        self, key: str, timestep: Optional[TimeStep], value: ScalarOrGroup
    ) -> None:
        timestep_index = 0
        if timestep is not None:
            timestep_index = timestep.GetTimeIndex(timestep.GetTimeSet())
        if timestep_index not in self.timesteps:
            self.timesteps[timestep_index] = {"second": self._timestep_str(timestep)}
        self.timesteps[timestep_index][key] = value

    @staticmethod
    def _timestep_str(timestep: Optional[TimeStep]) -> str:
        if timestep is None:
            return f"{0.0:.3e}"
        return f"{timestep.second:.3e}"


def sparsed_timeset(timeset, multiplier_timestep: float = 1) -> List[TimeStep]:
    return list(timeset[::multiplier_timestep])


def timesteps_as_floats(timesteps: Iterable[TimeStep]):
    return [float("%.2f" % time_step.second) for time_step in timesteps]


def xcoordinates(user_process, timestep: int = 0):
    x_coord = []
    for particle in user_process.IterParticles(time_step=timestep):  # last time step
        x_coord.append(particle.x)
    return x_coord


def ycoordinates(user_process, timestep: int = 0):
    y_coord = []
    for particle in user_process.IterParticles(time_step=timestep):  # last time step
        y_coord.append(particle.y)
    return y_coord


def zcoordinates(user_process, timestep: int = 0):
    z_coord = []
    for particle in user_process.IterParticles(time_step=timestep):  # last time step
        z_coord.append(particle.z)
    return z_coord


def absolute_velocity(user_process, timestep: int = 0):
    velocity = user_process.GetGridFunction("Absolute Translational Velocity").GetArray(
        time_step=timestep
    )
    return velocity


def main():
    # Dumper to log data after experiment
    dumper = RockyDumper()
    # Project
    project: RAProject = api.GetProject()
    study = project.GetStudy()
    proj_path = Path(project.GetProjectFilename())
    project_name = proj_path.name.split(".rocky")[0]
    run_outfolder = OUTPUT_PATH / project_name
    os.makedirs(run_outfolder, exist_ok=True)

    timeset = study.GetTimeSet()
    timesteps_picked = sparsed_timeset(timeset, multiplier_timestep=1)
    # timesteps_float = timesteps_as_floats(timesteps_picked)

    user_processes = project.GetUserProcessCollection()
    x_positions = [20, 40, 60, 80]  # _ default
    # x_positions = [1, 20, 40, 60, 80, 100, 120, 140, 160, 180]  # 200m length
    x_magnitudes = [0.06, 0.6, 1.6]

    for x_size in x_magnitudes:
        df_vel_positions = {}
        for pos in x_positions:
            df_vel_positions[f"{pos}m"] = {}
            for t_index, timestep in enumerate(timesteps_picked):
                df_vel_positions[f"{pos}m"][str(t_index)] = {}
                name_process_cube = f"{pos}m"
                cube_process = user_processes.GetProcess(name_process_cube)
                cube_process.SetSize(x_size, 10.7, 1, unit=None)

                x = xcoordinates(cube_process, timestep)
                y = ycoordinates(cube_process, timestep)
                z = zcoordinates(cube_process, timestep)
                velocities = absolute_velocity(cube_process, timestep)
                timestep_second = f"{timestep.second:.3e}"
                df_vel_positions[f"{pos}m"][str(t_index)] = {
                    "second": timestep_second,
                    "x": x,
                    "y": y,
                    "z": z,
                    "absolute_velocity": velocities.tolist(),
                }

        # dumper.log_dataframe("Particles", df, timestep)
        filename = run_outfolder / f"local_velocities_coordinates_xsize{x_size}.json"
        with open(filename, "w") as fp:
            json.dump(df_vel_positions, fp)
    project.SaveProject()
    project.CloseProject(check_save_state=False)

    sys.exit(0)


main()
