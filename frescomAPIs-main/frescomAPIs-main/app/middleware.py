import time
from typing import Awaitable, Callable

from fastapi import Request, Response

from app.logger import logger


async def log_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """
    A middleware function to log incoming requests.

    Args:
        request (Request): The incoming request object.
        call_next (Callable[[Request], Awaitable[Response]]): A callback to call the next middleware in the chain.

    Returns:
        Response: The response object from the next middleware in the chain.
    """

    # Start the timer
    start = time.time()

    # Call the next middleware in the chain
    response = await call_next(request)

    # Calculate the process time
    process_time = time.time() - start

    # Prepare the log dictionary
    log_dict = {
        "method": request.method,
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "headers": dict(request.headers),
        "process_time": process_time,
    }
    logger.info(
        f"Request: {request.method} Path: {request.url.path} Query: {request.query_params} Process Time: {process_time}",
        extra=log_dict,
    )

    # logger.info(f"Response: {response.status_code}")
    return response
