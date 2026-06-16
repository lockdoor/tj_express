import uvicorn
from tj_express.config import HOST, PORT

def main():
    # Launch uvicorn programmatically, loading the app from tj_express.main
    uvicorn.run("tj_express.main:app", host=HOST, port=PORT, reload=True)

if __name__ == "__main__":
    main()