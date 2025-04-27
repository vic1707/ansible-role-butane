# Ansible Role: vic1707.butane

[![Ansible Galaxy](https://img.shields.io/badge/galaxy-vic1707.butane-blue.svg)](https://galaxy.ansible.com/vic1707/butane)

An Ansible role to easily run the [Butane](https://coreos.github.io/butane/) CLI tool from CoreOS' Ignition suite.

This role wraps the `butane` CLI to convert Butane configs into Ignition configs, either from a file or raw input.

---

## Requirements

-   Ansible 2.9+ (tested up to 11.5.0)
-   `butane` CLI installed on the target system (or available at a specified path)

---

## Role Variables

| Variable     | Default  | Description                                                                                                                           |
| ------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `input_path` | `null`   | Path to a Butane file. Incompatible with `input`.                                                                                     |
| `input`      | `null`   | Inline raw Butane config as a string. Incompatible with `input_path`.                                                                 |
| `bin`        | `butane` | Path to the `butane` binary. Defaults to looking it up as a local file then in `$PATH`.                                               |
| `check`      | `false`  | Run `butane` with `--check` to validate the input without producing output.                                                           |
| `files_dir`  | `null`   | Directory to embed local files into the Butane config (`--files-dir`).                                                                |
| `output`     | `null`   | Write output to a file instead of stdout (`--output`).                                                                                |
| `pretty`     | `true`   | Format output as pretty JSON.                                                                                                         |
| `raw`        | `false`  | If true, ignores the `metadata` key. See: [https://coreos.github.io/butane/upgrading-openshift/#machineconfig-metadata-fields](docs). |
| `strict`     | `true`   | Fail on warnings during conversion.                                                                                                   |

---

## Usage Examples

**Example using a file:**

```yaml
- name: Convert Butane file
	vic1707.butane:
      input_path: /path/to/config.bu
      output: /path/to/config.ign
```

**Example using inline input:**

```yml
- name: Convert raw Butane input
  vic1707.butane:
      output: /path/to/config.ign ## Can be omitted
      input: |
          variant: fcos
          version: 1.4.0
          storage:
            files:
              - path: /etc/example
                contents:
                  inline: Hello World
```

---

## License

[WTFPL](./LICENSE)
