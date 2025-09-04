echo "Preparing venv"
python -m venv .venv

echo "Activating venv"
source .venv/bin/activate

echo "Installing requirements"
pip install -r requirements.txt
pip install -U setuptools pyinstaller

echo "Building exe"
pyinstaller -F --add-data pre-trimmed:pre-trimmed solar_rift_music_player.py 2>&1 | tee pyinstaller_build_log.txt

echo "Cleaning up exe build residue"
rm -rf build
rm *.spec

echo "Deactivating venv"
deactivate
