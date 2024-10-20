# SDS011 dust sensor data logger

```sh
git clone git@github.com:Tymek/SDS011.git
python SDS011
```
```
Options:
  -i, --interval <minutes>  Set the query interval in minutes (default: 1)
  -p, --port <serial_port>  Set the serial port for the sensor (default: /dev/ttyUSB0)
  -h, --help                Show help message and exit
```
You may need to allow the user to access the serial port.

Labels are based on the _European Air Quality Index_ ([EAQI](https://airindex.eea.europa.eu)) scale.

![example output](https://github.com/user-attachments/assets/47c72176-5ae2-466a-ad5d-1775573dcb9e)
