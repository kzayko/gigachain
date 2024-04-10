"""Utilities for loading configurations from langchain_core-hub."""

import warnings
from typing import Any


def try_load_from_hub(
    *args: Any,
    **kwargs: Any,
) -> Any:
    warnings.warn(
        "Loading from the deprecated github-based Hub is no longer supported. "
        "Please use the new LangChain Hub at https://smith.langchain.com/hub instead."
    )
    # return None, which indicates that we shouldn't load from old hub
    # and might just be a filepath for e.g. load_chain
    return None
