from ansible.module_utils.basic import AnsibleModule
import subprocess
import os


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
		mutually_exclusive=[
			["input_path", "input"],
		],
		required_one_of=[
			["input_path", "input"],
		],
		supports_check_mode=False,
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
