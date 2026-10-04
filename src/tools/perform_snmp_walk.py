"""MCP tool to perform SNMP walk on SevOne devices"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

# Maximum total output lines before truncation
_MAX_OUTPUT_LINES = 10_000
# Maximum characters in the final text response
_MAX_RESPONSE_CHARS = 500_000

_OUTPUT_FORMATS = [
    "DEFAULT",
    "DEFAULTWITHNUMERICINDEXES",
    "NUMERICOIDS",
    "CERTIFICATIONWALK",
    "HEXSTRING",
    "HEXWITHNUMERICOIDS",
]


class PerformSnmpWalkTool:
    """
    MCP tool to perform an SNMP walk against one or more SevOne devices.

    Calls POST /api/v3/metadata/devices/snmpwalk.
    Accepts either device names or device IDs, plus a list of OIDs.
    Returns the walk output as formatted text.
    """

    @property
    def name(self) -> str:
        return "perform_snmp_walk"

    @property
    def description(self) -> str:
        return """Perform an SNMP walk on one or more SevOne devices and return the output as text.

Provide either device names or device IDs together with the OIDs to walk.

Input options:
- device_names + oids  — walk by device name (exact match)
- device_ids   + oids  — walk by device ID (integer)

Optional:
- output_format: controls how OIDs and values are rendered.
  Values: DEFAULT (default) | DEFAULTWITHNUMERICINDEXES | NUMERICOIDS |
          CERTIFICATIONWALK | HEXSTRING | HEXWITHNUMERICOIDS

Returns plain-text SNMP walk output per device and OID.
Large responses are automatically truncated with a clear notice.

Examples:
- By name:  {"device_names": ["router1"], "oids": ["1.3.6.1.2.1.1"]}
- By ID:    {"device_ids": [123], "oids": ["1.3.6.1.2.1.2.2"]}
- Custom format: {"device_names": ["sw1"], "oids": ["1.3.6.1.2.1.1"], "output_format": "NUMERICOIDS"}
"""

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "device_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of device names to walk (exact match).",
                },
                "device_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of device IDs to walk.",
                },
                "oids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of OIDs to walk (e.g. '1.3.6.1.2.1.1' or 'sysDescr').",
                },
                "output_format": {
                    "type": "string",
                    "enum": _OUTPUT_FORMATS,
                    "default": "DEFAULT",
                    "description": (
                        "Output format for the walk results. "
                        "DEFAULT: standard output. "
                        "DEFAULTWITHNUMERICINDEXES: numeric index strings. "
                        "NUMERICOIDS: fully numeric OIDs. "
                        "CERTIFICATIONWALK: numeric OIDs without symbolic labels. "
                        "HEXSTRING: values as hex. "
                        "HEXWITHNUMERICOIDS: hex values with numeric OIDs."
                    ),
                },
            },
            "required": ["oids"],
            "oneOf": [
                {"required": ["device_names", "oids"]},
                {"required": ["device_ids", "oids"]},
            ],
        }

    async def execute(
        self,
        api_client,
        oids: List[str],
        device_names: Optional[List[str]] = None,
        device_ids: Optional[List[int]] = None,
        output_format: str = "DEFAULT",
    ) -> Dict[str, Any]:
        """
        Execute the SNMP walk operation.

        Args:
            api_client: SevOneAPIClient instance
            oids: OIDs to walk
            device_names: Device names (exact match)
            device_ids: Device IDs (integers)
            output_format: Walk output format enum value

        Returns:
            {
                "success": bool,
                "data": {"text": str, "truncated": bool, "total_lines": int},
                "message": str,
                "error": str  (only on failure)
            }
        """
        try:
            # --- Validate inputs ---
            if not device_names and not device_ids:
                return {
                    "success": False,
                    "error": "Provide either device_names or device_ids.",
                    "message": "Missing required parameter",
                }
            if not oids:
                return {
                    "success": False,
                    "error": "oids list must not be empty.",
                    "message": "Missing required parameter",
                }
            if output_format not in _OUTPUT_FORMATS:
                output_format = "DEFAULT"

            # --- Build request body ---
            devices_payload: List[Dict[str, Any]] = []

            if device_names:
                for name in device_names:
                    devices_payload.append({
                        "deviceName": {"value": name, "isFuzzy": False},
                        "oids": oids,
                    })
                logger.info(
                    f"SNMP walk by name: {device_names}, OIDs: {oids}, format: {output_format}"
                )

            if device_ids:
                for dev_id in device_ids:
                    devices_payload.append({
                        "deviceId": str(dev_id),
                        "oids": oids,
                    })
                logger.info(
                    f"SNMP walk by ID: {device_ids}, OIDs: {oids}, format: {output_format}"
                )

            request_body = {
                "devices": devices_payload,
                "outputFormat": output_format,
            }

            # --- Call API ---
            endpoint = "/api/v3/metadata/devices/snmpwalk"
            result = await api_client.post(endpoint, json_data=request_body)

            # --- Format response as text ---
            text_lines: List[str] = []
            total_lines = 0
            truncated = False

            response_devices = result.get("devices", [])
            for dev in response_devices:
                dev_id = dev.get("deviceId", "")
                dev_name = dev.get("deviceName", dev_id or "unknown")
                text_lines.append(f"=== Device: {dev_name} (ID: {dev_id}) ===")

                for walk_entry in dev.get("snmpWalk", []):
                    oid_index = walk_entry.get("oidIndex", "")
                    command = walk_entry.get("command", "")
                    status = walk_entry.get("status", True)
                    output_lines: List[str] = walk_entry.get("outputLines", [])

                    if command:
                        text_lines.append(f"  OID: {oid_index}  Command: {command}  Status: {'OK' if status else 'FAILED'}")
                    else:
                        text_lines.append(f"  OID: {oid_index}  Status: {'OK' if status else 'FAILED'}")

                    for line in output_lines:
                        if total_lines >= _MAX_OUTPUT_LINES:
                            truncated = True
                            break
                        text_lines.append(f"    {line}")
                        total_lines += 1

                    if truncated:
                        break

                if truncated:
                    text_lines.append(
                        f"\n[TRUNCATED] Output limited to {_MAX_OUTPUT_LINES} lines. "
                        "Narrow your OID list or query fewer devices to see the full output."
                    )
                    break

                text_lines.append("")  # blank line between devices

            text_output = "\n".join(text_lines)

            # Character-level safety cap
            if len(text_output) > _MAX_RESPONSE_CHARS:
                text_output = text_output[:_MAX_RESPONSE_CHARS]
                text_output += (
                    f"\n\n[TRUNCATED] Response capped at {_MAX_RESPONSE_CHARS:,} characters. "
                    "Reduce the number of devices or OIDs for a complete result."
                )
                truncated = True

            logger.info(
                f"SNMP walk complete: {len(response_devices)} device(s), "
                f"{total_lines} output lines, truncated={truncated}"
            )

            return {
                "success": True,
                "data": {
                    "text": text_output,
                    "truncated": truncated,
                    "total_lines": total_lines,
                    "device_count": len(response_devices),
                },
                "message": (
                    f"SNMP walk completed for {len(response_devices)} device(s)"
                    + (" (output truncated)" if truncated else "")
                ),
            }

        except MemoryError:
            logger.error("Out of memory while processing SNMP walk response")
            return {
                "success": False,
                "error": "Response too large to process in memory. Reduce OIDs or device count.",
                "message": "Memory error during SNMP walk",
            }
        except Exception as e:
            logger.error(f"SNMP walk failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "SNMP walk failed",
            }

# Made with Bob
