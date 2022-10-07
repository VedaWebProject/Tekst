if __name__ == "__main__":

    import uvicorn

    uvicorn.run("textrig.main:app", reload=True, log_config=None)
