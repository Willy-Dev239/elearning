from decouple import config as _cfg

if not _cfg("USE_SQLITE", default=False, cast=bool):
    # PyMySQL remplace mysqlclient (pas de compilation nécessaire)
    import pymysql
    pymysql.version_info = (2, 2, 1, "final", 0)
    pymysql.install_as_MySQLdb()
