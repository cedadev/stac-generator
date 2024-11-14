# encoding: utf-8
"""
Elasticsearch
-------------

An output backend which outputs the content generated to a STAC FastAPI
using the Transaction endpoint extension

**Plugin name:** ``stac_fastapi``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``api_url``
      - ``str``
      - ``REQUIRED`` root url of STAC API
    * - ``verify``
      - ``bool``
      - Path to a yaml file which defines the mapping for the index

Example Configuration:
    .. code-block:: yaml

        outputs:
            - name: stac_fastapi
              api_url: https://localhost
"""
__author__ = "Richard Smith"
__date__ = "01 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
from urllib.parse import urljoin

from httpx import Client
from httpx_auth import OAuth2ClientCredentials
from pydantic import BaseModel, Field

from stac_generator.core.output import Output

LOGGER = logging.getLogger(__name__)


class STACAuthentication(BaseModel):
    """STAC authentication model."""

    token_url: str = Field(
        description="Token URL for authentication server.",
    )
    client_id: str = Field(
        description="Client id.",
    )
    client_secret: str = Field(
        description="Client secret.",
    )


class STACFastAPIConf(BaseModel):
    """STAC FastAPI config model."""

    api_url: str = Field(
        description="URL for API.",
    )
    authentication: STACAuthentication = Field(
        default=None,
        description="Authentication for STAC API.",
    )
    verify: bool = Field(
        default=False,
        description="API certificate verifcation.",
    )


class STACFastAPIOutput(Output):
    """
    Connects to an elasticsearch instance and exports the
    documents to elasticsearch.

    """

    conf_class = STACFastAPIConf

    def item(self, data: dict, client: Client, auth: OAuth2ClientCredentials | None) -> None:
        collections = data["collection"]

        if isinstance(data["collection"], str):
            collections = [collections]

        for collection in collections:
            collection = data["collection"] = collection.lower()

            response = client.post(
                urljoin(self.conf.api_url, f"collections/{collection}/items"),
                json=data,
                auth=auth,
            )

            if response.status_code == 404:
                response_json = response.json()

                if response_json["description"] == f"Collection {collection} does not exist":
                    collection_data = {
                        "type": "Collection",
                        "id": collection,
                        "description": collection,
                        "stac_version": "0.1.0",
                        "stac_extensions": [],
                        "license": data.get("license", "No License"),
                        "extent": {
                            "spatial": {"bbox": [[-180, -90, 180, 90]]},
                            "temporal": {
                                "interval": [["1992-01-01T00:00:00Z", "2015-12-31T00:00:00Z"]]
                            },
                        },
                        "links": [
                            {
                                "rel": "self",
                                "type": "application/geo+json",
                                "href": f"https://api.stac.ceda.ac.uk/collections/{collection}",
                            },
                            {
                                "rel": "parent",
                                "type": "application/json",
                                "href": "https://api.stac.ceda.ac.uk/",
                            },
                            {
                                "rel": "queryables",
                                "type": "application/json",
                                "href": f"https://api.stac.ceda.ac.uk/collections/{collection}/queryables",
                            },
                            {
                                "rel": "items",
                                "type": "application/geo+json",
                                "href": f"https://api.stac.ceda.ac.uk/collections/cmip6/{collection}",
                            },
                            {
                                "rel": "root",
                                "type": "application/json",
                                "href": "https://api.stac.ceda.ac.uk/",
                            },
                        ],
                    }

                    response = client.post(
                        urljoin(self.conf.api_url, "collections"),
                        json=collection_data,
                        auth=auth,
                    )

                    response = client.post(
                        urljoin(self.conf.api_url, f"collections/{collection}/items"),
                        json=data,
                        auth=auth,
                    )

            if response.status_code == 409:
                response_json = response.json()

                if (
                    response_json["description"]
                    == f"Item {data['id']} in collection {collection} already exists"
                ):
                    response = client.put(
                        urljoin(self.conf.api_url, f"collections/{collection}/items/{data['id']}"),
                        json=data,
                        auth=auth,
                    )

                    if response.status_code != 200:
                        LOGGER.warning(
                            "FastAPI Output Item update failed with status code: %s and response text: %s",
                            response.status_code,
                            response.text,
                        )

            elif response.status_code != 200:
                LOGGER.warning(
                    "FastAPI Output failed to post to STAC Fastapi items endpoint returned status code: %s and response text: %s request data: %s",
                    response.status_code,
                    response.text,
                    data,
                )

    def collection(self, data: dict, client: Client, auth: OAuth2ClientCredentials | None) -> None:
        response = client.post(urljoin(self.conf.api_url, "collections"), json=data, auth=auth)

        if response.status_code == 409:
            response_json = response.json()

            if response_json["description"] == f"Collection {data['id']} already exists":
                response = client.put(
                    urljoin(self.conf.api_url, "collections"),
                    # urljoin(self.api_url, f"collections/{data['id']}"),
                    json=data,
                    auth=auth,
                )

                if response.status_code != 200:
                    LOGGER.warning(
                        "FastAPI Output Collection update failed with status code: %s and response text: %s",
                        response.status_code,
                        response.text,
                    )

        elif response.status_code != 200:
            LOGGER.warning(
                "FastAPI Output failed to post to STAC Fastapi collections endpoint returned status code: %s and response text: %s request data: %s",
                response.status_code,
                response.text,
                data,
            )

    def export(self, data: dict, **kwargs) -> None:
        client = Client(
            verify=self.conf.verify,
            timeout=180,
        )

        if self.conf.authentication:
            auth = OAuth2ClientCredentials(
                self.conf.authentication.token_url,
                client_id=self.conf.authentication.client_id,
                client_secret=self.conf.authentication.client_secret,
            )

        else:
            auth = None

        if kwargs["GENERATOR_TYPE"] == "item":
            self.item(data, client, auth)

        elif kwargs["GENERATOR_TYPE"] == "collection":
            self.collection(data, client, auth)
