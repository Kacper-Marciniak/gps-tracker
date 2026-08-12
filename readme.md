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

Same for `gps-tracker-vis.service`:
1. Set .env file with:
	```
	GPS_TRACKER_USERNAME=user

	GPS_TRACKER_PASSWORD=password
	
	GPS_TRACKER_KEY=secret-key
	```
2. Edit `deploy/systemd/gps-tracker-vis.service` and adjust:
	- `User`
	- `WorkingDirectory`
	- `ExecStart`
2. Install the service:
	- `sudo cp deploy/systemd/gps-tracker-vis.service /etc/systemd/system/gps-tracker-vis.service`
	- `sudo systemctl daemon-reload`
3. Enable boot start:
	- `sudo systemctl enable gps-tracker-vis`
4. Start now:
	- `sudo systemctl start gps-tracker-vis`

Useful commands:
- `sudo systemctl status gps-tracker-server`
- `sudo systemctl restart gps-tracker-server`
- `sudo systemctl stop gps-tracker-server`
- `sudo journalctl -u gps-tracker-server -f`