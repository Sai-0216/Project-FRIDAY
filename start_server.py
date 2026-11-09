"""Start the FRIDAY Core multi-device server."""
from network.server import app
import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
