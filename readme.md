### GPS-TRACKER SERVER

## Auto-start on boot (systemd)

Use the systemd unit at `deploy/systemd/gps-tracker-server.service`.

1. Copy project to the VM.
2. Edit `deploy/systemd/gps-tracker-server.service` and adjust:
	- `User`
	- `WorkingDirectory`
	- `ExecStart`
3. Install the service:
	- `sudo cp deploy/systemd/gps-tracker-server.service /etc/systemd/system/gps-tracker-server.service`
	- `sudo systemctl daemon-reload`
4. Enable boot start:
	- `sudo systemctl enable gps-tracker-server`
5. Start now:
	- `sudo systemctl start gps-tracker-server`

Useful commands:
- `sudo systemctl status gps-tracker-server`
- `sudo systemctl restart gps-tracker-server`
- `sudo systemctl stop gps-tracker-server`
- `sudo journalctl -u gps-tracker-server -f`