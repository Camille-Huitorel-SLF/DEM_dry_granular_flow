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

    def dump(self, dump_path: Path):
        if dump_path.is_dir():
            dump_path /= "impact_wall_horizontal_force.json"
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


def horizontal_impact_force(user_process, timestep: int = 0):
    force_x = user_process.GetGridFunction("Force : Nodal : X").GetArray(
        time_step=timestep
    )
    return force_x


def get_coord_nodal_y(user_process, timestep: int = 0):
    nodal_y = user_process.GetGridFunction("Coordinate : Nodal : Y").GetArray(
        time_step=timestep
    )
    return nodal_y


def get_surface_nodal(user_process, timestep: int = 0):
    nodal_area = user_process.GetGridFunction("Area : Nodal").GetArray(
        time_step=timestep
    )
    return nodal_area


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

    geometry_collection = study.GetGeometryCollection()
    impact_wall = geometry_collection.GetGeometry("impact_wall")

    for timestep in timesteps_picked:
        horizontal_force = horizontal_impact_force(impact_wall, timestep=timestep)
        dumper.log_dataframe(
            "Nodal Horizontal Force", pd.DataFrame(horizontal_force), timestep
        )
        # nodal_area = get_surface_nodal(impact_wall, timestep=timestep)
        # dumper.log_dataframe("Nodal Surface", pd.DataFrame(nodal_area), timestep)
        y_nod_coord = get_coord_nodal_y(impact_wall, timestep)
        dumper.log_dataframe("Nodal Coordinate Y", pd.DataFrame(y_nod_coord), timestep)
    dumper.dump(run_outfolder)
    project.SaveProject()
    project.CloseProject(check_save_state=False)

    sys.exit(0)


main()
