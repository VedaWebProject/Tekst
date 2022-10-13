if __name__ == "__main__":

    import uvicorn
    from textrig.config import TextRigConfig, get_config

    _cfg: TextRigConfig = get_config()

    uvicorn.run(
        "textrig.app:app",
        reload=True,
        log_config=None,
        host=_cfg.dev_srv_host,
        port=_cfg.dev_srv_port,
    )
