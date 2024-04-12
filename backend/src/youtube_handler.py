import googleapiclient.discovery
from secrets_handler import SecretsHandler

api_service_name = "youtube"
api_version = "v3"

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=SecretsHandler.get_youtube_key()
)