from ansible.module_utils.basic import AnsibleModule
import subprocess
import os


DOCUMENTATION = r"""
---
module: butane
short_description: Wrapper around the CoreOS Butane CLI tool
description:
  - This module allows running Butane to generate Ignition configs from Butane files.
  - Supports passing input from a file or inline content.
options:
  input_path:
    description:
      - Path to the Butane input file.
    type: str
  input:
    description:
      - Raw Butane configuration content to pass via stdin.
    type: str
  bin:
    description:
      - Path to the Butane binary or binary name if in PATH.
    type: str
    default: butane
  check:
    description:
      - Validate config without generating output.
    type: bool
    default: false
  files_dir:
    description:
      - Directory containing files to embed.
    type: str
  output:
    description:
      - Output file path to write the result.
    type: str
  pretty:
    description:
      - Output formatted JSON.
    type: bool
    default: true
  raw:
    description:
      - Output raw Ignition without MachineConfig wrapping.
    type: bool
    default: false
  strict:
    description:
      - Fail on warnings.
    type: bool
    default: true
author:
  - vic1707
"""

EXAMPLES = r"""
- name: Generate ignition config from Butane input file
  butane:
    input_path: "./example.bu"
    output: "./example.ign"

- name: Validate Butane config from inline content
  butane:
    input: |
      variant: fcos
      version: 1.4.0
      systemd:
        units:
          - name: example.service
            enabled: true
    check: true
"""

RETURN = r"""
output_file_path:
  description: Path to the generated Ignition file if output was specified.
  type: str
  returned: when output is defined
command_output:
  description: Butane command output if no output file was specified.
  type: str
  returned: when output is not defined
"""


def main():
	module = AnsibleModule(
		argument_spec={
			"input_path": {
				"type": "str",
				"default": None,
				"required": False,
			},
			"input": {
				"type": "str",
				"default": None,
				"required": False,
			},
			"bin": {
				"type": "str",
				"default": "butane",
				"required": False,
			},
			"check": {
				"type": "bool",
				"default": False,
				"required": False,
			},
			"files_dir": {
				"type": "str",
				"default": None,
				"required": False,
			},
			"output": {
				"type": "str",
				"default": None,
				"required": False,
			},
			"pretty": {
				"type": "bool",
				"default": True,
				"required": False,
			},
			"raw": {
				"type": "bool",
				"default": False,
				"required": False,
			},
			"strict": {
				"type": "bool",
				"default": True,
				"required": False,
			},
		},
		# Done manually, receiving null strill triggers the error
		# mutually_exclusive=[
		# 	["input_path", "input"],
		# ],
		required_one_of=[
			["input_path", "input"],
		],
		supports_check_mode=False,
	)

	if module.params["input"] and module.params["input_path"]:
		return module.fail_json(
			msg="parameters are mutually exclusive: input_path|input"
		)

	## Canonicalize butane binary path
	if not os.path.isfile(module.params["bin"]):
		module.params["bin"] = module.get_bin_path(module.params["bin"], required=True)
	module.debug(module.params)

	## Build `butane` command to run
	stdin = None
	cmd = [module.params["bin"]]

	## Basic settings
	if module.params["check"]:
		cmd.append("--check")
	if module.params["files_dir"] is not None:
		cmd.extend(["--files-dir", module.params["files_dir"]])
	if module.params["pretty"]:
		cmd.append("--pretty")
	if module.params["raw"]:
		cmd.append("--raw")
	if module.params["strict"]:
		cmd.append("--strict")

	## butane input file logic
	if module.params["input"]:  ## pass raw string via stdin
		stdin = module.params["input"]
	if module.params["input_path"]:  ## input path as bare argument
		if not os.path.isfile(module.params["input_path"]):
			return module.fail_json(
				msg=f"Input: '{module.params['input_path']}' file not found."
			)
		cmd.append(module.params["input_path"])

	## butane output to a file
	if module.params["output"]:
		cmd.extend(["--output", module.params["output"]])

	try:
		butane_stdout = subprocess.run(
			cmd, input=stdin, check=True, text=True, capture_output=True
		).stdout
	except subprocess.CalledProcessError as err:
		return module.fail_json(msg="Butane command failed", stderr=err.stderr)

	## if output was given, set task output to output's path, else set output to stdout of the butane command
	if module.params["output"]:
		module.exit_json(
			changed=False,
			msg="Butane command executed",
			output_file_path=module.params["output"],
		)
	else:
		module.exit_json(
			changed=False, msg="Butane command executed", command_output=butane_stdout
		)


if __name__ == "__main__":
	main()
