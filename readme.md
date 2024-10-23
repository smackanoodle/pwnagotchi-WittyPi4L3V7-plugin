# Plugin to use with Pwnagotchi and the WittyPi4L3V7 hat.
# Battery Curves and case are for a 500mAh battery, https://www.adafruit.com/product/1578

## This plugin DOES require using the official [Witty Pi 4 Software](https://github.com/uugear/Witty-Pi-4) install. 
## YOU MUST INCREASE THE WITTY'S POWER CUT DELAY TO ATLEAST 15 SECONDS TO ENSURE PROPER INTEGRATED SHUTDOWN

## Install guide:

```bash
# Go to the home directory
cd ~

# Install the Witty Pi 4 Software
wget https://www.uugear.com/repo/WittyPi4/install.sh
sudo sh install.sh

# Download the plugin and modified plugin file
git clone https://github.com/smackanoodle/pwnagotchi-WittyPi4L3V7-plugin/witty-plugin.git

# Make the installed-plugins directory if it doesn't already exist
sudo mkdir -p /usr/local/share/pwnagotchi/installed-plugins/

# Installs the user-plugin
sudo ln -s ~/witty-plugin/wittypi4l3v7.py /usr/local/share/pwnagotchi/installed-plugins/wittypi4l3v7.py

# Update the utilities file in Witty software
sudo cp ~/pwnagotchi-witty-plugin/utilities.sh ~/wittypi/utilities.sh

```


In /etc/pwnagotchi/config.toml add:
```toml
main.custom_plugins = "/usr/local/share/pwnagotchi/installed-plugins/"
main.plugins.wittypi4l3v7.enabled = true
```



WittyPi4L3V7 web settings are accessible at http://10.0.0.2:8000/wittypi4/

Huge thanks to the pwnagotchi pisugar2 plugin for providing me with a starting point for my plugin