from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

from settings import CLIENT_SECRETS_CREDENTIALS_FILE

settings = {
                "client_config_backend": "service",
                "service_config": {
                    "client_json_file_path": "config/service_account.json",
                }
            }
gauth = GoogleAuth(settings=settings)
GoogleAuth.DEFAULT_SETTINGS['get_refresh_token'] = True
# Authenticate
gauth.ServiceAuth()

drive = GoogleDrive(gauth)
