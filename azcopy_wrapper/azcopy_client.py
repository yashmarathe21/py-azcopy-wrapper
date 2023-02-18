from typing import Generator, List, Optional, Union
from azcopy_wrapper.azcopy_utilities import (
    AzJobInfo,
    AzCopyOptions,
    AzLocalLocation,
    AzRemoteSASLocation,
)


class AzClient:
    """
    Azcopy client to execute commands for the user
    If azcopy is already installed in the system,
    then the client will directly use that exe
    For ex. If the azcopy binary file exists in
    /usr/local/bin/, then client will by default
    use that file.
    But if the usr wants to use another specific file
    which is stored in some other location,
    then they will have to specify it while creating
    the AzClient object
    """

    exe_to_use: str
    artefact_dir: Optional[str]

    def __init__(
        self, exe_to_use: str = "azcopy", artefact_dir: Optional[str] = None
    ) -> None:
        self.exe_to_use = exe_to_use
        self.artefact_dir = artefact_dir

    def execute_command(self, cmd: List[str]) -> Generator[str, None, None]:
        """
        Executes a command while simultaneously
        sending output.
        """
        import subprocess
        import os

        # Set env variables for command
        new_env = os.environ.copy()
        if self.artefact_dir is not None:
            if not os.path.exists(self.artefact_dir):
                os.makedirs(self.artefact_dir)
            new_env["AZCOPY_JOB_PLAN_LOCATION"] = os.path.join(
                self.artefact_dir, "jobs"
            )
            new_env["AZCOPY_LOG_LOCATION"] = os.path.join(self.artefact_dir, "logs")

        popen = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=new_env,
        )

        if popen.stdout is not None:
            for stdout_line in iter(popen.stdout.readline, ""):
                yield stdout_line

            popen.stdout.close()
            return_code = popen.wait()

            if return_code:
                raise subprocess.CalledProcessError(return_code, cmd)

    def check_token(self, token: str) -> str:
        """
        Checks if the SAS token is expired
        """
        import datetime
        from urllib.parse import parse_qs

        parsed = parse_qs(token.lstrip("?"))

        # se is the query parameter for SessionExpiry field
        session_expiry = parsed.get("se")

        if session_expiry is None:
            return "Cannot find session expiry date in the SAS Token"

        session_expiry_string = session_expiry[0]

        session_expiry_timestamp = datetime.datetime.strptime(
            str(session_expiry_string), "%Y-%m-%dT%H:%M:%SZ"
        )

        if datetime.datetime.now() > session_expiry_timestamp:
            return "SAS Token is expired"
        else:
            return ""

    def get_property_value(self, key: str, job_summary: str) -> int:
        """
        Extracts a property value from Azcopy Job Summary
        """
        import re

        try:
            property_key_match = re.search(r"{}: \d+\n".format(key), job_summary)

            if property_key_match is not None:

                property_key_text = property_key_match.group()
                property_value_match = re.search(r"\d+", property_key_text)

                # If the property key text exists in the job summary,
                # the gets the property value
                if property_value_match is not None:
                    property_value = int(property_value_match.group())
                else:
                    property_value = 0
            else:
                property_value = 0
        except Exception as e:
            property_value = 0

        return property_value

    def get_summary_info(self, job_info: AzJobInfo, summary: str) -> AzJobInfo:
        """
        Extract all properties of Job Info from the Azcopy job summary
        """

        properties_required = [
            "Number of File Transfers",
            "Number of Folder Property Transfers",
            "Number of File Transfers",
            "Total Number of Transfers",
            "Number of Transfers Completed",
            "Number of Transfers Failed",
            "Number of Transfers Skipped",
        ]

        for property_key in properties_required:

            # Converting the property key string to attribute form
            property_attribute = property_key.lower().replace(" ", "_")
            property_value = self.get_property_value(property_key, summary)

            # Set the attribute in job_info object
            setattr(job_info, property_attribute, property_value)

        job_info.total_bytes_transferred = self.get_property_value(
            "TotalBytesTransferred", summary
        )

        return job_info

    def copy(
        self,
        src: Union[AzRemoteSASLocation, AzLocalLocation],
        dest: Union[AzRemoteSASLocation, AzLocalLocation],
        transfer_options: AzCopyOptions,
    ) -> AzJobInfo:
        """
        Copies that data from source to destionation
        with the transfer options specified
        """
        import re

        # Both source and destination should have different
        # location types for proper usage of wildcards
        if src.location_type == dest.location_type:
            raise Exception("Both src and dest are of the same location type")

        # Generating the command to be used for subprocess
        cmd = [
            self.exe_to_use,
            "cp",
            str(src),
            str(dest),
        ] + transfer_options.get_options_list()

        # Creating AzJobInfo object to store the job info
        job_info = AzJobInfo()

        try:

            summary = ""
            # A boolean flag to be set as True when
            # azcopy starts sending summary information
            unlock_summary = False

            for output_line in self.execute_command(cmd):
                print(output_line, end="")

                # Extracting the percent complete information from the
                # current output line and updating it in the job_info
                if "%" in output_line:

                    percent_expression = r"(?P<percent_complete>\d+\.\d+) %,"
                    transfer_match = re.match(percent_expression, output_line)

                    if transfer_match is not None:
                        transfer_info = transfer_match.groupdict()

                        job_info.percent_complete = float(
                            transfer_info["percent_complete"]
                        )

                # If azcopy has started sending summary then
                # appending it to summary text
                if unlock_summary:
                    summary += output_line

                # Job summary starts with line ->
                # Job {job_id} summary
                if output_line.startswith("Job") and "summary" in output_line:
                    unlock_summary = True

                if "AuthenticationFailed" in output_line:
                    job_info.error_msg = output_line

                if "Final Job Status:" in output_line:
                    job_info.final_job_status_msg = output_line.split(":")[-1].strip()

        except Exception as e:
            # Checking if the error is because of the sas token

            if type(dest) == AzRemoteSASLocation:
                token = str(dest.sas_token)
            elif type(src) == AzRemoteSASLocation:
                token = str(src.sas_token)
            else:
                token = ""

            token_status_check = self.check_token(token)

            if len(token_status_check) > 1:
                job_info.error_msg = token_status_check
            else:
                job_info.error_msg = str(e)

            job_info.completed = False

        # Get the final job summary info
        job_info = self.get_summary_info(job_info, summary)

        # Since we aren't going to use overwrite flag,
        # the status should always be Completed.
        # and number of skipped files should always be 0
        # so file trasfers should be equal to total transfers required
        # For all the other scenarios, the job completed staus
        # flag will be marked as false
        if (
            job_info.final_job_status_msg == "Completed"
            or job_info.final_job_status_msg == "CompletedWithSkipped"
        ):
            job_info.completed = True
        elif job_info.number_of_transfers_failed > 0:
            job_info.error_msg += "; Tranfers failed = {}".format(
                job_info.number_of_transfers_failed
            )
            job_info.completed = False
            raise Exception(job_info.error_msg)
        else:
            job_info.error_msg += "; Error while transferring data"
            job_info.completed = False
            raise Exception(job_info.error_msg)

        return job_info
