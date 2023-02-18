# AzCopy Python Wrapper

This package allows you to invoke [AzCopy v10](https://github.com/Azure/azure-storage-azcopy) from python.
Its structure has been inspired by the NodeJS version of Azcopy Wrapper which can be found here [NodeJS Azcopy](https://www.npmjs.com/package/@azure-tools/azcopy-node)


## Basic Usage

```
remote_location = AzRemoteSASLocation(
    storage_account="testAzureStorageAccount",
    container="testAzureContainer",
    path="testBlobPath/",
    use_wildcard=False,
    sas_token="testSasToken",
    location_type=LocationType.DEST,
)

local_location = AzLocalLocation(
    path=local_data_path,
    use_wildcard=True,
    location_type=LocationType.SRC,
)

transfer_options = AzCopyOptions(
    recursive=True,
    overwrite_existing=False,
)

az_client = AzClient(exe_to_use=DEFAULT_EXE_TO_USE, artefact_dir=ARTEFACE_DIR)

job_info = az_client.copy(
    src=local_location, dest=remote_location, transfer_options=transfer_options
)

print(f"Final Job Status = {job_info.final_job_status_msg}")
```

## Command Line Usage

For simplicty, cmd line usage has also been introducted

```
python3 upload_to_remote_location.py --azure_storage_account "" --container "" --blob "" --sas_token "" --local_data_path ""
```

### 1.0.0

- First version of this python azcopy wrapper!
- Validated against AzCopy 10.17.0.
- Only upload/download functionality
- Tested only on Ubuntu 20.04 as of now.