import logging
import os
import ssl
import traceback
import warnings
import dotenv

from elasticsearch import AsyncElasticsearch, Elasticsearch

# from elasticsearch.connection import create_ssl_context
dotenv.load_dotenv()
warnings.filterwarnings("ignore")
loges = logging.getLogger("elasticsearch")


class GetDatabase:
    def __init__(
        self,
    ):
        self.config = dict({})
        # self.ssl_enabled = os.environ["DATABASE_SSL_ENABLED"]
        # self.ca_certs = os.environ["DATABASE_CA_FILE"]
        # self.check_hostname = os.environ["DATABASE_CHECK_HOSTNAME"]
        # self.ssl_certificate = os.environ["DATABASE_SSL_CERTIFICATE"]
        # self.password_auth = os.environ["DATABASE_PASSWORD_AUTHENTICATION"]
        # self.username = os.environ["DATABASE_USERNAME"]
        # self.password = os.environ["DATABASE_PASSWORD"]
        self.port = os.environ["DATABASE_PORT"]
        self.host = os.environ["DATABASE_HOST"]

    # def build_context(
    #     self,
    # ):
    #     if self.ssl_enabled:
    #         if not os.path.exists(self.ca_certs):
    #             loges.warning("Please add ca certs for secure Elasticsearch connection")
    #         if self.ca_certs != "":
    #             context = create_ssl_context(cafile=self.ca_certs)
    #         else:
    #             context = create_ssl_context()
    #         if self.check_hostname == "true":
    #             context.check_hostname = True
    #         elif self.check_hostname == "false":
    #             context.check_hostname = False
    #         if self.ssl_certificate == "required":
    #             context.verify_mode = ssl.CERT_REQUIRED
    #         elif self.ssl_certificate == "optional":
    #             context.verify_mode = ssl.CERT_OPTIONAL
    #         else:
    #             context.verify_mode = ssl.CERT_NONE
    #         self.config = {
    #             "scheme": os.environ["DATABASE_SCHEME"],
    #             "ssl_context": context,
    #         }

    def build_config(
        self,
    ):
        self.config = {
            "scheme": "http",
            #             "ssl_context": context,
        }
        # if self.password_auth:
        #     self.config["http_auth"] = (self.username, self.password)

    def get_sync(
        self,
    ):
        # self.build_context()
        # self.build_config()
        if len(self.config):
            loges.info(
                f"eshost:{self.host}, esport: {self.port}, esconfig: {self.config}"
            )
            return Elasticsearch(
                [{"host": self.host, "port": self.port}], **self.config
            )
        else:
            loges.info(
                f"eshost:{self.host}, esport: {self.port}, esconfig: {self.config}"
            )
            return Elasticsearch(
                [{"host": self.host, "port": int(self.port), "scheme": "http"}]
            )

    def get_async(
        self,
    ):
        try:
            # self.build_context()
            # self.build_config()
            if len(self.config):
                loges.info(
                    f"eshost:{self.host}, esport: {self.port}, esconfig: {self.config}"
                )
                return AsyncElasticsearch(
                    [{"host": self.host, "port": self.port}], **self.config
                )
            else:
                loges.info(
                    f"eshost:{self.host}, esport: {self.port}, esconfig: {self.config}"
                )
                return AsyncElasticsearch([{"host": self.host, "port": self.port}])
        except Exception:
            loges.error(
                f"ERROR: Cannot connect to Elasticsearch during startup {traceback.format_exc()}"
            )
            return False


database = GetDatabase()
es = database.get_async()
sync_es = database.get_sync()
print("database connection established successfully")
