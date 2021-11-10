#!/bin/sh
#!/bin/bash

sudo apt-get update

echo "korean font download"
sudo apt-get install fonts-nanum*
echo "#############\n\nmove font files from sudo cp /usr/share/fonts/truetype/nanum/Nanum* into your matplotlib path ex) /usr/anaconda3/lib/python3.7/site-packages/matplotlib/mpl-data/fonts/ttf/ \n\n############"

echo "necessary package download"
pip install -r requirements.txt




