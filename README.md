# automatic_label_printer
Automating label printing tasks for incoming orders using Raspberry Pi and Brother QL printer...

File "config_example.py" is just example of configuration file. This file has to be edited and renamed to "config.py".

Main script is called "trhknih_api.py". It checks for new orders using e-shop's API and then prints labels needed for shipping orders etc.
The main script is periodicaly run by cron.

It is designed to be used with [brother_ql_web software](https://github.com/pklaus/brother_ql_web) made by [Philipp Klaus](https://github.com/pklaus).

Detailed information can be found [here](https://evenparity.net/automatic-label-printer-with-raspberry-pi/).
