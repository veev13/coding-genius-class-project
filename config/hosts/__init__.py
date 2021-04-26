import platform


class hosts:
    if not platform.system() == "Windows":
        recommand_server_service = "http://recommand-api-server-service:15003"
        stock_server_service = "http://stock-api-server-service:15002/stocks"
        users_server_service = "http://stock-api-server-service:15002/users"
        login_server_service = "http://login-api-server-service:15001"
        kafka_bootstrap_server_service = "kafka:29092"
    else:
        recommand_server_service = "http://localhost:15003"
        stock_server_service = "http://localhost:15002/stocks"
        users_server_service = "http://localhost:15002/users"
        login_server_service = "http://localhost:15001"
        kafka_bootstrap_server_service = "http://kafka:29092"
