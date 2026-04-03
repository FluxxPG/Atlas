from app.core.config import settings
from app.core.runtime import configure_runtime

configure_runtime()

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development",
    )
