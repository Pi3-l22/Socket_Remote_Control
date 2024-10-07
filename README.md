# Socket Remote Connect

A Python-based remote control program using sockets.

English | [简体中文](README_CN.md)

## Features

- Remote command execution
- Remote file upload
- Remote file download
- Capture remote host screenshots
- Retrieve and decrypt WeChat data
  - Uses [pywxdump](https://github.com/xaoyaoo/PyWxDump) project
  - Server must be running on Windows

## Requirements

See [requirements.txt](requirements.txt) for a list of required Python packages.

## Usage

1. Set up the server:
   - Edit `server.py` and configure the `port` variable if needed.
   - Run `server.py` on your control machine:
     ```
     python server.py
     ```

2. Set up the client:
   - Edit `client.py` and set the `ip` variable to your server's IP address.
   - Run `client.py` on the target machine:
     ```
     python client.py
     ```

3. Once connected, you can use various commands on the server console:
   - Execute shell commands
   - `get <filename>`: Download a file from the client
   - `put <filename>`: Upload a file to the client
   - `screen`: Capture a screenshot of the client's screen
   - `wxinfo`: Get WeChat information from the client
   - `wxchat`: Retrieve and decrypt WeChat data from the client
   - `flask`: Start a Flask server to view chat records (after retrieving WeChat data)
   - `exit`: Close the connection

## Implementation Details

This project uses Python's `socket` library to establish a reverse connection, where the client attempts to connect to the server, creating a TCP connection between the server and client. The server can send commands to the client, which are then executed on the client machine. File transfers are implemented using a custom protocol that sends file metadata before the actual file content.

For WeChat data retrieval and decryption, the project leverages the `pywxdump` library. The decrypted data is compressed and sent back to the server for analysis.

The screenshot functionality uses the `PIL` library to capture the client's screen and send it back to the server.

## Derivative

Based on this program, I also wrote a simple program called `peppa_pig.py`, which is derived from an example program in the [Python - 100 Days from Novice to Master](https://github.com/Pi3-l22/Python-Learn) project. In this project, I use it to hide the execution of `client.py`. You can package `peppa_pig.py` and `client.py` into an exe file using the [pyinstaller](https://pyinstaller.org/en/stable/) tool and name it something inconspicuous. This way, when the program is executed, it won't raise suspicion from the other party. The screen will only show a peppa_pig drawing program, while `client.py` runs in the background, achieving a Trojan horse functionality.

Using a similar idea, you can hide the control program in any application, such as games, cloud storage, etc.

## Note

This tool and its derivatives are for educational purposes only. Ensure you have permission before using it on any system you do not own.

Using this tool to conduct network attacks on others is illegal. Do not use it for illegal purposes!

The author is not responsible for any serious consequences resulting from illegal operations using this project!

## To-Do

- [X] Optimize interaction after remote host reverse shell
- [ ] Monitor mouse position
- [ ] Monitor keyboard input
- [ ] Control host screen operations

## License

[MIT License](LICENSE)