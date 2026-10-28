# Copyright (C) 2026 Microsoft

"""Unit tests for AzureBlobStorage error handling."""

import logging
from unittest import mock

from graphrag_storage.azure_blob_storage import AzureBlobStorage


async def test_set_logs_error_with_key_when_upload_fails(caplog):
    with mock.patch(
        "graphrag_storage.azure_blob_storage.BlobServiceClient"
    ) as blob_service_client:
        service = blob_service_client.from_connection_string.return_value
        container_client = service.get_container_client.return_value
        blob_client = container_client.get_blob_client.return_value
        blob_client.upload_blob.side_effect = RuntimeError("upload failed")

        storage = AzureBlobStorage(
            container_name="testcontainer",
            connection_string="UseDevelopmentStorage=true",
            base_dir="output",
        )

        with caplog.at_level(logging.ERROR):
            await storage.set("graph.parquet", b"data")

    blob_client.upload_blob.assert_called_once_with(b"data", overwrite=True)
    records = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert len(records) == 1
    assert records[0].getMessage() == "Error setting key output/graph.parquet"
    assert records[0].exc_info is not None
    assert "upload failed" in caplog.text
