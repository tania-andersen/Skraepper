# Install Skraepper
apt install python3-pip
apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate
apt-get install python3-tk
pip install -r requirements.txt
playwright install chromium
deactivate