"""Reader module for Ragrank"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from ragrank.bridge.pydantic import BaseModel, Field
from ragrank.dataset import DataNode, Dataset
from ragrank.utils.common import eval_cell

DATANODE_TYPE = Dict[str, List[str] | str]
DATASET_TYPE = Dict[str, List[str] | List[List[str]]]
RAGRANK_DICT_TYPE = DATANODE_TYPE | DATASET_TYPE


def from_dict(
    data: RAGRANK_DICT_TYPE,
    *,
    return_as_dataset: bool = False,
    column_map: ColumnMap | None = None,
) -> Dataset | DataNode:
    """
    Create a Dataset or DataNode object from a dictionary representation.

    Args:
        data (Union[DATANODE_TYPE, DATASET_TYPE]): The dictionary containing
            the data representation.
        return_as_dataset (bool, optional): If True, return as Dataset object,
            otherwise return as DataNode. Defaults to False.
        column_map (ColumnMap, optional): Column mapping.
            Defaults to ColumnMap().

    Returns:
        Union[Dataset, DataNode]: Either a Dataset or DataNode object.

    Raises:
        ValueError: If the column specified in column_map
            is not present in the data.
    """
    if column_map is None:
        column_map = ColumnMap()

    for item in column_map:
        value = item[1]
        if value not in data:
            raise ValueError(
                f"The column {value} not in the data"
            ) from ValueError
    data = {
        key: data[value] for key, value in column_map
    }  # mapping col

    if any(isinstance(i, str) for i in data.values()):
        if return_as_dataset:
            return Dataset(**{i: [data[i]] for i in data})
        return DataNode(**data)
    return Dataset(**data)


def from_dataframe(
    data: pd.DataFrame,
    *,
    return_as_dataset: bool = False,
    column_map: ColumnMap | None = None,
) -> Dataset | DataNode:
    """
    Create a Dataset or DataNode object from a Pandas DataFrame.

    Args:
        data (pd.DataFrame): The DataFrame containing the data.
        return_as_dataset (bool, optional): If True, return as Dataset object,
            otherwise return as DataNode. Defaults to False.
        column_map (ColumnMap, optional): Column mapping.
            Defaults to ColumnMap().

    Returns:
        Union[Dataset, DataNode]: Either a Dataset or DataNode object.
    """
    if column_map is None:
        column_map = ColumnMap()

    modified_data = data.map(eval_cell)
    dict_data = {
        key: list(value_dict.values())
        for key, value_dict in modified_data.to_dict().items()
    }
    return from_dict(
        data=dict_data,
        return_as_dataset=return_as_dataset,
        column_map=column_map,
    )


def from_csv(
    path: str | Path,
    *,
    column_map: ColumnMap | None = None,
    **kwargs: Any,  # noqa: ANN401
) -> Dataset | DataNode:
    """
    Create a Dataset or DataNode object from a CSV file.

    Args:
        path (Union[str, Path]): The path to the CSV file.
        column_map (ColumnMap, optional): Column mapping.
            Defaults to ColumnMap().
        **kwargs: Keyword arguments to pass to pandas read_csv function.

    Returns:
        Union[Dataset, DataNode]: Either a Dataset or DataNode object.
    """
    if column_map is None:
        column_map = ColumnMap()

    df: pd.DataFrame = pd.read_csv(filepath_or_buffer=path, **kwargs)
    return from_dataframe(data=df, column_map=column_map)


class ColumnMap(BaseModel):
    """
    Represents a mapping of column names to their
        corresponding names in a dataset.

    Attributes:
        question (str): The name of the column containing questions.
        context (str): The name of the column containing contexts.
        response (str): The name of the column containing responses.
    """

    question: str = Field(
        default="question",
        description="The name of the column containing questions",
    )
    context: str = Field(
        default="context",
        description="The name of the column containing contexts",
    )
    response: str = Field(
        default="response",
        description="The name of the column containing responses",
    )
