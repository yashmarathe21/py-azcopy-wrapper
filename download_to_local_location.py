import argparse

from utils.constants import DEFAULT_EXE_TO_USE, ARTEFACE_DIR

from azcopy_wrapper.azcopy_client import AzClient
from azcopy_wrapper.azcopy_utilities import (
    AzRemoteSASLocation,
    AzLocalLocation,
    AzCopyOptions,
    LocationType,
)

# Create the parser and add arguments
parser = argparse.ArgumentParser()
parser.add_argument("--azure_storage_account", help="Azure Storage Account")
parser.add_argument(
    "--container",
    required=True,
    help="Container to which the data needs to be uploaded",
)
parser.add_argument(
    "--blob",
    required=True,
    help="Blob to which the data needs to be uploaded",
)
parser.add_argument(
    "--sas_token",
    required=True,
    help="SAS token with Write Access to the container",
)
parser.add_argument(
    "--local_data_path",
    required=True,
    help="Local path from which data needs to be uploaded",
)

args = parser.parse_args()

if __name__ == "__main__":
    remote_location = AzRemoteSASLocation(
        storage_account=args.azure_storage_account,
        container=args.container,
        path=args.blob,
        use_wildcard=False,
        sas_token=args.sas_token,
        location_type=LocationType.DEST,
    )

    local_location = AzLocalLocation(
        path=args.local_data_path,
        use_wildcard=True,
        location_type=LocationType.SRC,
    )

    transfer_options = AzCopyOptions(
        recursive=True,
        overwrite_existing=False,
    )

    az_client = AzClient(exe_to_use=DEFAULT_EXE_TO_USE, artefact_dir=ARTEFACE_DIR)

    job_info = az_client.copy(
        src=remote_location, dest=local_location, transfer_options=transfer_options
    )

    print(f"Final Job Status = {job_info.final_job_status_msg}")
