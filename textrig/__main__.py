if __name__ == "__main__":

    import uvicorn
    from textrig.config import TextRigConfig, get_config

    _cfg: TextRigConfig = get_config()

    if _cfg.dev_mode:
        uvicorn.run(
            "textrig.main:app",
            reload=True,
            log_config=None,
            host=_cfg.dev_srv_host,
            port=_cfg.dev_srv_port,
        )
    else:
        print("Set environment variable DEV_MODE=true to run development server")
