def get_connection(hostname: str, username: str, password: str, port: int) -> object:
    from pysros.management import connect
    from pysros.exceptions import ModelProcessingError
    import sys
    try:
        connection_object = connect(host=hostname,
                                    port=port,
                                    username=username,
                                    password=password,
                                    hostkey_verify=False)
    except RuntimeError as e1:
        print("Failed to connect.  Error:", e1)
        sys.exit(-1)
    except ModelProcessingError as e2:
        print("Failed to create model-driven schema.  Error:", e2)
        sys.exit(-2)
    return connection_object