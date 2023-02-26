from typing import List, Optional

from azcopy_wrapper.sas_token_validation import is_sas_token_session_expired


class LocationType:
    """
    This type is used to specify the location
    type of the object created for transfer
    for the AzCopy command
    """

    SRC = "source"
    DEST = "destination"


class AzRemoteSASLocation:
    """
    Class to create Azure Remote Location with SAS Token
    Returns the remote location url string with the information
    specified while creating the object
    """

    storage_account: str
    container: str
    path: str
    use_wildcard: bool
    sas_token: str
    location_type: Optional[str]

    def __init__(
        self,
        storage_account: str = "",
        container: str = "",
        path: str = "",
        use_wildcard: bool = False,
        sas_token: str = "",
        location_type: str = None,
    ) -> None:
        if len(sas_token) > 0:
            sas_token_expiry_flag = is_sas_token_session_expired(token=sas_token)

            if sas_token_expiry_flag == True:
                raise Exception("SAS token is expired")

        self.storage_account = storage_account
        self.container = container
        self.sas_token = sas_token
        self.use_wildcard = use_wildcard
        self.path = path
        self.location_type = location_type

    def get_resource_uri(self) -> str:
        return f"https://{self.storage_account}.blob.core.windows.net/{self.container}/"

    def __str__(self) -> str:
        """
        Creates the remote location url with sas token to be used for the final location
        """
        if len(self.sas_token) > 0:
            sas_token_expiry_flag = is_sas_token_session_expired(token=self.sas_token)

            if sas_token_expiry_flag == True:
                raise Exception("SAS token is expired")

        resource_uri = self.get_resource_uri()

        wildcard = ""
        if self.use_wildcard == True:
            wildcard = "*"

        return resource_uri + self.path + wildcard + "?" + self.sas_token


class AzLocalLocation:
    """
    Class to create Local Path for data transfer using Azcopy
    """

    path: str
    use_wildcard: bool
    location_type: Optional[str]

    def __init__(
        self,
        path: str = "",
        use_wildcard: bool = False,
        location_type: str = None,
    ) -> None:
        self.path = path
        self.use_wildcard = use_wildcard
        self.location_type = location_type

    def __str__(self) -> str:
        wildcard = ""
        if self.use_wildcard == True:
            wildcard = "*"

        return self.path + wildcard


class AzCopyOptions:
    """
    Class to give specific options for data transfer using Azcopy
    """

    overwrite_existing: bool
    recursive: bool
    put_md5: bool
    exclude_path: str

    def __init__(
        self,
        overwrite_existing: bool = False,
        recursive: bool = False,
        put_md5: bool = False,
        exclude_path: str = "",
    ) -> None:
        self.overwrite_existing = overwrite_existing
        self.recursive = recursive
        self.put_md5 = put_md5
        self.exclude_path = exclude_path

    def get_options_list(self) -> List[str]:
        transfer_options = []

        # Look into subdirectories recursively when transferring
        if self.recursive:
            transfer_options.append("--recursive")

        # Overwrite the conflicting files and blobs at the destination if this flag is set to true. (default true)
        if not self.overwrite_existing:
            transfer_options.append("--overwrite")
            transfer_options.append("false")

        # Create an MD5 hash of each file, and save the hash as the Content-MD5 property
        # of the destination blob or file.
        # Only available for uploading
        if self.put_md5:
            transfer_options.append("--put-md5")

        # Exclude these paths when copying.
        if len(self.exclude_path) > 0:
            transfer_options.append("--exclude-path")
            transfer_options.append(self.exclude_path)

        return transfer_options


class AzSyncOptions:
    """
    Class to give specific options for data transfer using Azcopy
    """

    recursive: bool
    put_md5: bool
    exclude_path: str

    def __init__(
        self,
        recursive: bool = False,
        put_md5: bool = False,
        exclude_path: str = "",
    ) -> None:
        self.recursive = recursive
        self.put_md5 = put_md5
        self.exclude_path = exclude_path

    def get_options_list(self) -> List[str]:
        transfer_options = []

        # Look into subdirectories recursively when transferring
        if self.recursive:
            transfer_options.append("--recursive")

        # Create an MD5 hash of each file, and save the hash as the Content-MD5 property
        # of the destination blob or file.
        if self.put_md5:
            transfer_options.append("--put-md5")

        if len(self.exclude_path) > 0:
            transfer_options.append("--exclude-path")
            transfer_options.append(self.exclude_path)

        return transfer_options


class AzCopyJobInfo:
    """
    Created the job info of the Azcopy job executed by the user
    """

    percent_complete: float
    error_msg: str
    number_of_file_transfers: int
    number_of_folder_property_transfers: int
    total_number_of_transfers: int
    number_of_transfers_completed: int
    number_of_transfers_failed: int
    number_of_transfers_skipped: int
    total_bytes_transferred: int
    final_job_status_msg: str
    completed: bool

    def __init__(
        self,
        percent_complete: float = float(0),
        error_msg: str = "",
        final_job_status_msg: str = "",
        number_of_file_transfers: int = 0,
        number_of_folder_property_transfers: int = 0,
        total_number_of_transfers: int = 0,
        number_of_transfers_completed: int = 0,
        number_of_transfers_failed: int = 0,
        number_of_transfers_skipped: int = 0,
        total_bytes_transferred: int = 0,
        completed: bool = False,
    ) -> None:
        # NOTE: Sometimes, azcopy doesn't return value as 100%
        # even if the entire data is transferred.
        # This might be because if the transfer is completed in between
        # the value sent by azcopy, then azcopy fails to send the final
        # percent value and directly sends the job summary
        self.percent_complete = percent_complete
        self.error_msg = error_msg
        self.final_job_status_msg = final_job_status_msg
        self.number_of_file_transfers = number_of_file_transfers
        self.number_of_folder_property_transfers = number_of_folder_property_transfers
        self.total_number_of_transfers = total_number_of_transfers
        self.number_of_transfers_completed = number_of_transfers_completed
        self.number_of_transfers_failed = number_of_transfers_failed
        self.number_of_transfers_skipped = number_of_transfers_skipped
        self.total_bytes_transferred = total_bytes_transferred
        self.completed = completed


class AzSyncJobInfo:
    """
    Created the job info of the Azcopy job executed by the user
    """

    percent_complete: float
    error_msg: str
    files_scanned_at_source: int
    files_scanned_at_destination: int
    # elapsed_time_minutes: float
    number_of_copy_transfers_for_files: int
    number_of_copy_transfers_for_folder_properties: int
    number_of_folder_property_transfers: int
    total_number_of_copy_transfers: int
    number_of_copy_transfers_completed: int
    number_of_copy_transfers_failed: int
    number_of_deletions_at_destination: int
    total_number_of_bytes_transferred: int
    total_number_of_bytes_enumerated: int
    final_job_status_msg: str
    completed: bool

    def __init__(
        self,
        percent_complete: float = float(0),
        error_msg: str = "",
        files_scanned_at_source: int = 0,
        files_scanned_at_destination: int = 0,
        # elapsed_time_minutes: float = float(0),
        number_of_copy_transfers_for_files: int = 0,
        number_of_copy_transfers_for_folder_properties: int = 0,
        number_of_folder_property_transfers: int = 0,
        total_number_of_copy_transfers: int = 0,
        number_of_copy_transfers_completed: int = 0,
        number_of_copy_transfers_failed: int = 0,
        number_of_deletions_at_destination: int = 0,
        total_number_of_bytes_transferred: int = 0,
        total_number_of_bytes_enumerated: int = 0,
        final_job_status_msg: str = "",
        completed: bool = False,
    ) -> None:
        # NOTE: Sometimes, azcopy doesn't return value as 100%
        # even if the entire data is transferred.
        # This might be because if the transfer is completed in between
        # the value sent by azcopy, then azcopy fails to send the final
        # percent value and directly sends the job summary
        self.percent_complete = percent_complete
        self.error_msg = error_msg
        self.final_job_status_msg = final_job_status_msg
        self.files_scanned_at_source = files_scanned_at_source
        self.files_scanned_at_destination = files_scanned_at_destination
        # self.elapsed_time_minutes = elapsed_time_minutes
        self.number_of_copy_transfers_for_files = number_of_copy_transfers_for_files
        self.number_of_copy_transfers_for_folder_properties = (
            number_of_copy_transfers_for_folder_properties
        )
        self.number_of_folder_property_transfers = number_of_folder_property_transfers
        self.total_number_of_copy_transfers = total_number_of_copy_transfers
        self.number_of_copy_transfers_completed = number_of_copy_transfers_completed
        self.number_of_copy_transfers_failed = number_of_copy_transfers_failed
        self.number_of_deletions_at_destination = number_of_deletions_at_destination
        self.total_number_of_bytes_transferred = total_number_of_bytes_transferred
        self.total_number_of_bytes_enumerated = total_number_of_bytes_enumerated
        self.completed = completed
