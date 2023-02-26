# AzCopy Python Wrapper

This package allows you to invoke [AzCopy v10](https://github.com/Azure/azure-storage-azcopy) from python.

Its design has been inspired by the NodeJS version of Azcopy Wrapper which can be found here [NodeJS Azcopy](https://www.npmjs.com/package/@azure-tools/azcopy-node)

# Requirements

1. Azcopy
- For Linux installation,(recommended with admin privileges) you can run 
```
# Download AzCopy
wget https://aka.ms/downloadazcopy-v10-linux
 
# Expand Archive
tar -xvf downloadazcopy-v10-linux
 
# Move AzCopy to the destination you want to store it
sudo cp ./azcopy_linux_amd64_*/azcopy /usr/bin/

# Change permissions of Azcopy
sudo chmod 777 /usr/bin/azcopy
```

- For windows installation, you can run
```
# Download and extract
Invoke-WebRequest -Uri "https://aka.ms/downloadazcopy-v10-windows" -OutFile AzCopy.zip -UseBasicParsing
Expand-Archive ./AzCopy.zip ./AzCopy -Force

# Move AzCopy
mkdir ~\AppData\Local\Programs\AZCopy
Get-ChildItem ./AzCopy/*/azcopy.exe | Move-Item -Destination ~\AppData\Local\Programs\AZCopy\

# Add AzCopy to PATH
$userenv = (Get-ItemProperty -Path 'HKCU:\Environment' -Name Path).path
$newPath = "$userenv;%USERPROFILE%\AppData\Local\Programs\AZCopy;"
New-ItemProperty -Path 'HKCU:\Environment' -Name Path -Value $newPath -Force

# Clean the kitchen
del -Force AzCopy.zip
del -Force -Recurse .\AzCopy\
```

- For detailed installation steps, you can refer the following links
1. [AzCopy official Documentation](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10)
2. [AzCopy Installation Scripts Option 1](https://www.thomasmaurer.ch/2019/05/how-to-install-azcopy-for-azure-storage/)
3. [AzCopy Installation Scripts Option 2](https://adamtheautomator.com/azcopy-download/)


## Basic Usage

### 1. Upload Directory to Remote Location

```
local_location = AzLocalLocation(
    path="./test_data/",
    use_wildcard=True,
)

remote_location = AzRemoteSASLocation(
    storage_account=storage_account,
    container=container,
    path="test4",
    sas_token=sas_token,
)

transfer_options = AzCopyOptions(
    overwrite_existing=True,
    recursive=True,
    exclude_path=f"test2.jpg;test_data_4;test_data_3/test3.jpg",
)

az_client = AzClient()

job_info = az_client.upload_data_to_remote_location(
    src=local_location, dest=remote_location, transfer_options=transfer_options
)

print(job_info.__dict__)
```


### 2. Download a remote file to local path

```
remote_location = AzRemoteSASLocation(
    storage_account=storage_account,
    container=container,
    path="test1.jpg",
    sas_token=sas_token,
)

local_location = AzLocalLocation(
    path="./test_data/test4.jpg",
)

transfer_options = AzCopyOptions(
    overwrite_existing=True,
)

az_client = AzClient()

job_info = az_client.download_data_to_local_location(
    src=remote_location, dest=local_location, transfer_options=transfer_options
)

print(job_info.__dict__)
```

### 3. Transfer files from one container to container

```
remote_location_src = AzRemoteSASLocation(
    storage_account=storage_account1,
    container=container1,
    path="test1/",
    sas_token=sas_token_cont1,
    use_wildcard=True,
)

remote_location_dest = AzRemoteSASLocation(
    storage_account=storage_account2,
    container=container2,
    path="test_dest5/",
    sas_token=sas_token_cont2,
)

transfer_options = AzCopyOptions(
    overwrite_existing=True,
    recursive=True,
    put_md5=True,
)

az_client = AzClient()

job_info = az_client.copy_remote_data_from_container_to_container(
    src=remote_location_src, dest=remote_location_dest, transfer_options=transfer_options
)

print(job_info.__dict__)
```

### 4. Sync a local directory to remote location

```
src = AzLocalLocation(
    path="./test_data/test_data3/",
)

dest = AzRemoteSASLocation(
    storage_account=storage_account,
    container=container,
    path="test7/",
    sas_token=sas_token,
)

transfer_options = AzSyncOptions(
    recursive=True,
    exclude_path="test_data_2;test_data_5"
)

az_client = AzClient()

job_info = az_client.sync_to_remote_location(
    src=src, dest=dest, transfer_options=transfer_options
)

print(job_info.__dict__)
```

For more examples, you can refer [ExamplesJupyterNotebook](examples.ipynb)

## v1.0.0

- First version of this python azcopy wrapper!
- Validated against AzCopy 10.17.0.
- Copy and Sync commands
- Tested only on Ubuntu 20.04 as of now.