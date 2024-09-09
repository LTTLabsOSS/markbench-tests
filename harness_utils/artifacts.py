"""Provides ArtifactManager class for capturing artifacts from test runs."""
import os
import mss
import yaml
from dataclasses import dataclass
from enum import Enum, unique
from shutil import copy
from pathlib import Path
from collections.abc import Callable


@unique
class ArtifactType(Enum):
    """
    Describes different types of artifacts to be saved from test runs.
    """

    IMAGE_CONFIG = "image_config"
    """
    Meant to describe images displaying an applications settings.
    For games this might be a screenshot of the in-game settings menu.
    """

    IMAGE_RESULTS = "image_results"
    """
    Meant to describe images displaying results of a benchmark.
    For games with built in benchmarks, this might be a screenshot of an in-game benchmark results screen.
    """

    TEXT_CONFIG = "text_config"
    """
    Meant to describe text-based files which contain application settings.
    For games this might be a .ini or .cfg file containing graphics settings.
    """

    TEXT_RESULTS = "text_results"
    """
    Meant to describe text-based files which contain results of a benchmark.
    For games with built in benchmarks, this might be a .txt or .xml file containing results from an in-game benchmark.
    """


_IMAGE_ARTIFACT_TYPES = (ArtifactType.IMAGE_CONFIG, ArtifactType.IMAGE_RESULTS)


@dataclass
class Artifact:
    """
    Describes an artifact captured by the ArtifactManager.
    """
    filename: str
    type: ArtifactType
    description: str

    def as_dict(self) -> dict:
        """
        Returns the Artifact object as a dictionary. Converts its type to a string value.
        """
        d = self.__dict__.copy()
        d["type"] = d["type"].value
        return d


class ArtifactManager:
    """
    Used to manage artifacts captured during a test run, either by coping files or taking screenshots.
    The manager maintains a list of artifacts it has captured and can produce a manifest file listing them.
    """
    def __init__(self, output_path: str | os.PathLike) -> None:
        self.output_path = Path(output_path)
        self.artifacts: list[Artifact] = []

        self.output_path.mkdir(parents=True, exist_ok=True)

    def copy_file(self, src: str | os.PathLike, artifact_type: ArtifactType, description=""):
        """
        Copies a file from `src` to the manager's `output_path` and adds a new Artifact to the manager's artifacts list.

        The newly created artifact's `type` and `description` fields are set to the given
        `artifact_type` and `description` arguments respectively while the artifact's `filename`
        is set to the basename of `src`.
        
        Raises a `ValueError` if `src` points to a directory instead of a file.
        """
        src_path = Path(src)
        if src_path.is_dir():
            raise ValueError("src should point to a file, not a directory")
        filename = src_path.name
        try:
            copy(src, self.output_path / filename)
            artifact = Artifact(filename, artifact_type, description)
            self.artifacts.append(artifact)
        except OSError as e:
            raise e

    def take_screenshot(
            self,
            filename: str,
            artifact_type: ArtifactType,
            description="",
            screenshot_override: Callable[[str | os.PathLike], None] | None = None):
        """
        Takes a screenshot and saves it to the manager's `output_path` with the given `filename`
        and adds a new Artifact to the manager's artifact list.

        The newly created artifact's `filename`, `type` and `description` fields are set to the
        given `filename`, `artifact_type` and `description` arguments respectively.

        Raises a `ValueError` if `artifact_type` is not one of the `ArtifactType` values which represents an image. 
        """
        if artifact_type not in _IMAGE_ARTIFACT_TYPES:
            raise ValueError("artifact_type should be a type that represents an image artifact")

        if screenshot_override is None:
            with mss.mss() as sct:
                sct.shot(output=str(self.output_path / filename))
        else:
            screenshot_override(self.output_path / filename)
        artifact = Artifact(filename, artifact_type, description)
        self.artifacts.append(artifact)

    def create_manifest(self):
        """
        Creates a file `artifacts.yaml` which lists the artifacts in the manager's `artifacts` list.
        The file is created at the location specified by the manager's `output_path`.
        """
        with open(self.output_path / "artifacts.yaml", encoding="utf-8", mode="w") as f:
            yaml.safe_dump([a.as_dict() for a in self.artifacts], f, sort_keys=False)
