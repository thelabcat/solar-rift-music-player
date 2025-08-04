echo "Building exe"
pyinstaller -F --add-data *.mp3:.  solar_rift_music_player.py
echo "Cleaning up exe build residue"
rm -rf build
rm *.spec
