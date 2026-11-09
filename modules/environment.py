"""
Project FRIDAY
Environment Interpreter
Phase 18.6.3
"""

from modules.device_state import device_state


class Environment:

    # ========================================
    # THRESHOLDS
    # ========================================

    CPU_HIGH = 80
    CPU_CRITICAL = 95

    RAM_HIGH = 80
    RAM_CRITICAL = 95

    DISK_HIGH = 80
    DISK_CRITICAL = 95

    BATTERY_LOW = 20
    BATTERY_CRITICAL = 10

    # ========================================
    # INTERPRET STATE
    # ========================================

    def interpret(self, state=None):
        """
        Convert raw DeviceState information into
        human-readable environmental conditions.
        """

        if state is None:
            state = device_state.snapshot()

        conditions = []

        # ----------------------------------------
        # CPU
        # ----------------------------------------

        cpu = state.get(
            "cpu_percent"
        )

        if cpu is not None:

            if cpu >= self.CPU_CRITICAL:

                conditions.append(
                    "CPU usage is critical."
                )

            elif cpu >= self.CPU_HIGH:

                conditions.append(
                    "CPU usage is high."
                )

            else:

                conditions.append(
                    "CPU usage is normal."
                )

        # ----------------------------------------
        # RAM
        # ----------------------------------------

        ram = state.get(
            "ram_percent"
        )

        if ram is not None:

            if ram >= self.RAM_CRITICAL:

                conditions.append(
                    "RAM usage is critical."
                )

            elif ram >= self.RAM_HIGH:

                conditions.append(
                    "RAM usage is high."
                )

            else:

                conditions.append(
                    "RAM usage is normal."
                )

        # ----------------------------------------
        # DISK
        # ----------------------------------------

        disk = state.get(
            "disk_percent"
        )

        if disk is not None:

            if disk >= self.DISK_CRITICAL:

                conditions.append(
                    "Disk usage is critical."
                )

            elif disk >= self.DISK_HIGH:

                conditions.append(
                    "Disk usage is high."
                )

            else:

                conditions.append(
                    "Disk usage is normal."
                )

        # ----------------------------------------
        # BATTERY
        # ----------------------------------------

        battery = state.get(
            "battery"
        )

        if battery is not None:

            battery_percent = battery.get(
                "percent"
            )

            charging = battery.get(
                "charging"
            )

            if battery_percent is not None:

                if (
                    battery_percent
                    <= self.BATTERY_CRITICAL
                ):

                    conditions.append(
                        "Battery level is critical."
                    )

                elif (
                    battery_percent
                    <= self.BATTERY_LOW
                ):

                    conditions.append(
                        "Battery level is low."
                    )

                elif charging:

                    conditions.append(
                        "Battery is charging."
                    )

                else:

                    conditions.append(
                        "Battery level is normal."
                    )

        # ----------------------------------------
        # WIFI
        # ----------------------------------------

        wifi = state.get(
            "wifi_status"
        )

        if wifi == "connected":

            conditions.append(
                "Wi-Fi is connected."
            )

        elif wifi == "disconnected":

            conditions.append(
                "Wi-Fi is disconnected."
            )

        elif wifi == "disabled":

            conditions.append(
                "Wi-Fi is disabled."
            )

        else:

            conditions.append(
                "Wi-Fi status is unknown."
            )

        # ----------------------------------------
        # RUNNING APPLICATIONS
        # ----------------------------------------

        running_apps = state.get(
            "running_apps",
            []
        )

        if running_apps:

            conditions.append(
                "Running applications: "
                + ", ".join(
                    running_apps
                )
                + "."
            )

        else:

            conditions.append(
                "No supported applications "
                "are currently running."
            )

        return conditions
    
    # ========================================
    # WORKLOAD CONTEXT
    # ========================================

    def workload_context(self, state=None):
        """
        Classify the current workload based on
        supported applications that are running.

        This describes context only.
        It does not claim that an application
        caused a resource condition.
        """

        if state is None:
            state = device_state.snapshot()

        running_apps = {
            str(app).lower()
            for app in state.get(
                "running_apps",
                []
            )
        }

        workload_types = []

        # ----------------------------------------
        # DEVELOPMENT
        # ----------------------------------------

        if "vscode" in running_apps:

            workload_types.append(
                "development"
            )

        # ----------------------------------------
        # BROWSER
        # ----------------------------------------

        if "chrome" in running_apps:

            workload_types.append(
                "browser"
            )

        # ----------------------------------------
        # MEDIA
        # ----------------------------------------

        if "spotify" in running_apps:

            workload_types.append(
                "media"
            )

        # ----------------------------------------
        # GENERAL
        # ----------------------------------------

        if not workload_types:

            workload_types.append(
                "general"
            )

        # ----------------------------------------
        # PRIMARY WORKLOAD
        # ----------------------------------------

        if "development" in workload_types:

            primary = "development"

        elif "browser" in workload_types:

            primary = "browser"

        elif "media" in workload_types:

            primary = "media"

        else:

            primary = "general"

        return {
            "primary": primary,
            "types": sorted(
                workload_types
            ),
            "applications": sorted(
                running_apps
            ),
        }

    # ========================================
    # STATUS DETAILS
    # ========================================

    def status_details(self, state=None):
        """
        Return the overall status together with
        the conditions responsible for it.

        Correlated conditions are also included
        in the final assessment.
        """

        if state is None:
            state = device_state.snapshot()

        status = "NORMAL"
        reasons = []

        # ----------------------------------------
        # CPU
        # ----------------------------------------

        cpu = state.get(
            "cpu_percent"
        )

        if cpu is not None:

            if cpu >= self.CPU_CRITICAL:

                status = "CRITICAL"

                reasons.append(
                    f"CPU usage is critical ({cpu}%)."
                )

            elif cpu >= self.CPU_HIGH:

                if status != "CRITICAL":
                    status = "WARNING"

                reasons.append(
                    f"CPU usage is high ({cpu}%)."
                )

        # ----------------------------------------
        # RAM
        # ----------------------------------------

        ram = state.get(
            "ram_percent"
        )

        if ram is not None:

            if ram >= self.RAM_CRITICAL:

                status = "CRITICAL"

                reasons.append(
                    f"RAM usage is critical ({ram}%)."
                )

            elif ram >= self.RAM_HIGH:

                if status != "CRITICAL":
                    status = "WARNING"

                reasons.append(
                    f"RAM usage is high ({ram}%)."
                )

        # ----------------------------------------
        # DISK
        # ----------------------------------------

        disk = state.get(
            "disk_percent"
        )

        if disk is not None:

            if disk >= self.DISK_CRITICAL:

                status = "CRITICAL"

                reasons.append(
                    f"Disk usage is critical ({disk}%)."
                )

            elif disk >= self.DISK_HIGH:

                if status != "CRITICAL":
                    status = "WARNING"

                reasons.append(
                    f"Disk usage is high ({disk}%)."
                )

        # ----------------------------------------
        # BATTERY
        # ----------------------------------------

        battery = state.get(
            "battery"
        )

        if battery is not None:

            battery_percent = battery.get(
                "percent"
            )

            if battery_percent is not None:

                if (
                    battery_percent
                    <= self.BATTERY_CRITICAL
                ):

                    status = "CRITICAL"

                    reasons.append(
                        f"Battery level is critical "
                        f"({battery_percent}%)."
                    )

                elif (
                    battery_percent
                    <= self.BATTERY_LOW
                ):

                    if status != "CRITICAL":
                        status = "WARNING"

                    reasons.append(
                        f"Battery level is low "
                        f"({battery_percent}%)."
                    )

        # ----------------------------------------
        # WIFI
        # ----------------------------------------

        wifi = state.get(
            "wifi_status"
        )

        if wifi == "disconnected":

            if status != "CRITICAL":
                status = "WARNING"

            reasons.append(
                "Wi-Fi is disconnected."
            )

        elif wifi == "disabled":

            if status != "CRITICAL":
                status = "WARNING"

            reasons.append(
                "Wi-Fi is disabled."
            )

        elif wifi == "unknown":

            reasons.append(
                "Wi-Fi status is unknown."
            )

        # ----------------------------------------
        # CORRELATED CONDITIONS
        # ----------------------------------------

        correlations = self.correlations(
            state
        )

        correlated_types = {
            finding.get("type")
            for finding in correlations
        }

        # ----------------------------------------
        # Remove redundant CPU/RAM reasons
        # ----------------------------------------

        if (
            "RESOURCE_PRESSURE_CRITICAL"
            in correlated_types
        ):

            reasons = [
                reason
                for reason in reasons
                if not reason.startswith(
                    "CPU usage is critical"
                )
                and not reason.startswith(
                    "RAM usage is critical"
                )
            ]

        elif (
            "RESOURCE_PRESSURE"
            in correlated_types
        ):

            reasons = [
                reason
                for reason in reasons
                if not reason.startswith(
                    "CPU usage is high"
                )
                and not reason.startswith(
                    "RAM usage is high"
                )
            ]

        # ----------------------------------------
        # Add correlated findings
        # ----------------------------------------

        for finding in correlations:

            severity = finding.get(
                "severity"
            )

            message = finding.get(
                "message"
            )

            if severity == "CRITICAL":

                status = "CRITICAL"

            elif (
                severity == "WARNING"
                and status != "CRITICAL"
            ):

                status = "WARNING"

            if message:

                reasons.append(
                    message
                )

        return {
            "status": status,
            "reasons": reasons,
        }

    # ========================================
    # CORRELATED CONDITIONS
    # ========================================

    def correlations(self, state=None):
        """
        Detect meaningful combinations of environmental
        conditions.

        This does not replace threshold analysis.
        It adds higher-level interpretation.
        """

        if state is None:
            state = device_state.snapshot()

        findings = []

        cpu = state.get(
            "cpu_percent"
        )

        ram = state.get(
            "ram_percent"
        )

        disk = state.get(
            "disk_percent"
        )

        battery = state.get(
            "battery"
        )

        wifi = state.get(
            "wifi_status"
        )

        # ----------------------------------------
        # CPU + RAM PRESSURE
        # ----------------------------------------

        if (
            cpu is not None
            and ram is not None
            and cpu >= self.CPU_HIGH
            and ram >= self.RAM_HIGH
        ):

            # ------------------------------------
            # CRITICAL RESOURCE PRESSURE
            # ------------------------------------

            if (
                cpu >= self.CPU_CRITICAL
                and ram >= self.RAM_CRITICAL
            ):

                findings.append(
                    {
                        "type": (
                            "RESOURCE_PRESSURE_CRITICAL"
                        ),
                        "severity": "CRITICAL",
                        "message": (
                            "CPU and RAM usage are "
                            "both critically high."
                        ),
                    }
                )

            # ------------------------------------
            # NORMAL HIGH RESOURCE PRESSURE
            # ------------------------------------

            else:

                findings.append(
                    {
                        "type": (
                            "RESOURCE_PRESSURE"
                        ),
                        "severity": "WARNING",
                        "message": (
                            "CPU and RAM usage are "
                            "both high."
                        ),
                    }
                )

        # ----------------------------------------
        # LOW BATTERY + NOT CHARGING
        # ----------------------------------------

        if battery is not None:

            battery_percent = battery.get(
                "percent"
            )

            charging = battery.get(
                "charging",
                False
            )

            if (
                battery_percent is not None
                and battery_percent
                <= self.BATTERY_LOW
                and not charging
            ):

                findings.append(
                    {
                        "type": "BATTERY_DISCHARGE",
                        "severity": "WARNING",
                        "message": (
                            "Battery is low and the "
                            "device is not charging."
                        ),
                    }
                )

        # ----------------------------------------
        # CRITICAL BATTERY + NOT CHARGING
        # ----------------------------------------

        if battery is not None:

            battery_percent = battery.get(
                "percent"
            )

            charging = battery.get(
                "charging",
                False
            )

            if (
                battery_percent is not None
                and battery_percent
                <= self.BATTERY_CRITICAL
                and not charging
            ):

                findings.append(
                    {
                        "type": "BATTERY_CRITICAL",
                        "severity": "CRITICAL",
                        "message": (
                            "Battery is critically "
                            "low and the device is "
                            "not charging."
                        ),
                    }
                )

        # ----------------------------------------
        # DISK + RAM PRESSURE
        # ----------------------------------------

        if (
            disk is not None
            and ram is not None
            and disk >= self.DISK_HIGH
            and ram >= self.RAM_HIGH
        ):

            findings.append(
                {
                    "type": (
                        "STORAGE_MEMORY_PRESSURE"
                    ),
                    "severity": "WARNING",
                    "message": (
                        "Disk and RAM usage are "
                        "both high."
                    ),
                }
            )

        # ----------------------------------------
        # WIFI UNAVAILABLE
        # ----------------------------------------

        if wifi in (
            "disconnected",
            "disabled"
        ):

            findings.append(
                {
                    "type": "NETWORK_UNAVAILABLE",
                    "severity": "WARNING",
                    "message": (
                        "Wi-Fi is unavailable."
                    ),
                }
            )

        return findings

    # ========================================
    # OVERALL STATUS
    # ========================================

    def status(self, state=None):
        """
        Return the overall environmental status.

        NORMAL   -> No significant issues.
        WARNING  -> One or more elevated conditions.
        CRITICAL -> One or more critical conditions.
        """

        if state is None:
            state = device_state.snapshot()

        details = self.status_details(
            state
        )

        return details.get(
            "status",
            "NORMAL"
        )


# ========================================
# ENVIRONMENT INSTANCE
# ========================================

environment = Environment()