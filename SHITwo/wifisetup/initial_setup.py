import os
import sys
import setup_lib


if os.getuid():
    sys.exit('You need root access to install!')


os.system('clear')
print()
print()
print("###################################")
print("##### Intial Setup  #####")
print("###################################")
print()
print()
entered_ssid = input("Enter SSID: ")
wpa_enabled_choice = 'Y'
wpa_entered_key = input("Enter password for connecting to this network, \nMust be at least 8 characters otherwise error will be thrown ) [default: NO PASSWORD]:")
auto_config_choice = input("Would you like to enable \nauto-reconfiguration mode [y/N]?: ")
auto_config_delay = input("Enter delay time for switching mode (300 default)")

server_port_choice = input("Enter server_port_choice. Enter 80 here. If you are unable to open 10.0.0.1 then run the program again and select another port number i.e. 8080 but run 10.0.0.1/8080 this time. (80 default)")
ssl_enabled_choice = 'N'
os.system('clear')
print()
print()
install_ans = input("Are you ready to commit changes to the system? [y/N]: ")

if(install_ans.lower() == 'y'):
	setup_lib.install_prereqs()
	setup_lib.copy_configs(wpa_enabled_choice)
	setup_lib.update_main_config_file(entered_ssid, auto_config_choice, auto_config_delay, ssl_enabled_choice, server_port_choice, wpa_enabled_choice, wpa_entered_key)
else:
	print("##############################################")
	print("Installation cancelled...")
	print("##############################################")
	sys.exit()

os.system('clear')
print()
print()
print("#####################################")
print("##### Setup Complete  #####")
print("#####################################")
print()
print()
print("Initial setup is complete. A reboot is required to start in WiFi configuration mode...")
reboot_ans = input("Would you like to do that now? [y/N]: ")

if reboot_ans.lower() == 'y':
	os.system('reboot')
