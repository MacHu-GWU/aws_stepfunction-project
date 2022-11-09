# -*- coding: utf-8 -*-

try:
    from .task import (
        LambdaTask,
        IOHandlerTask,
    )
except ImportError as e: # pragma: no cover
    raise ImportError(
        "you have to install the following libraries to use the 'Magic Task' feature: "
        "s3pathlib>=1.0.10, "
        "cottonformation>=0.0.7"
    )
