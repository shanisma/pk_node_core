# Flash, minify, write recipes
# Author Shanmugathas Vigneswaran
# email: shanmugathas.vigneswaran@outlook.fr

# check link for esp32 chip : https://micropython.org/download/esp32/
export FIRM_LINK=https://micropython.org/resources/firmware/esp32spiram-idf3-20191220-v1.12.bin
export PORT="COM3"
flash-mp:
	wget ${FIRM_LINK} -O esp32.bin
	esptool --chip esp32 --port ${PORT} erase_flash
	esptool --chip esp32 --port ${PORT} write_flash -z 0x1000 esp32.bin

min-sprinkler: sprinkler-firmware \
			   boot.py \
			   main_sprinkler.py \
			   settings.py \
			   ST7735.py \
			   sysfont.py \
			   utils.py
	pyminify boot.py > sprinkler-firmware/boot.py
	pyminify main_sprinkler.py > sprinkler-firmware/main.py
	pyminify settings.py > sprinkler-firmware/settings.py
	pyminify ST7735.py > sprinkler-firmware/ST7735.py
	pyminify sysfont.py > sprinkler-firmware/sysfont.py
	pyminify utils.py > sprinkler-firmware/utils.py
	pyminify sprinkler_io.py > sprinkler-firmware/sprinkler_io.py

export PORT="COM3"
put-sprinkler-firmware: sprinkler-firmware min-sprinkler
	ampy --port ${PORT} put sprinkler-firmware/settings.py
	ampy --port ${PORT} put sprinkler-firmware/ST7735.py
	ampy --port ${PORT} put sprinkler-firmware/sysfont.py
	ampy --port ${PORT} put sprinkler-firmware/utils.py
	ampy --port ${PORT} put sprinkler-firmware/sprinkler_io.py
	ampy --port ${PORT} put sprinkler-firmware/boot.py
	ampy --port ${PORT} put sprinkler-firmware/main.py

.PHONY: dev
dev:
	# minify
	pipenv run pyminify boot.py > sprinkler-firmware/boot.py
	pipenv run pyminify main_sprinkler.py > sprinkler-firmware/main.py
	pipenv run pyminify settings.py > sprinkler-firmware/settings.py
	pipenv run pyminify ST7735.py > sprinkler-firmware/ST7735.py
	pipenv run pyminify sysfont.py > sprinkler-firmware/sysfont.py
	pipenv run pyminify utils.py > sprinkler-firmware/utils.py
	pipenv run pyminify sprinkler_io.py > sprinkler-firmware/sprinkler_io.py
	# upload
	pipenv run ampy --port COM3 put sprinkler-firmware/settings.py
	pipenv run ampy --port COM3 put sprinkler-firmware/ST7735.py
	pipenv run ampy --port COM3 put sprinkler-firmware/sysfont.py
	pipenv run ampy --port COM3 put sprinkler-firmware/utils.py
	pipenv run ampy --port COM3 put sprinkler-firmware/sprinkler_io.py
	pipenv run ampy --port COM3 put sprinkler-firmware/boot.py
	pipenv run ampy --port COM3 put sprinkler-firmware/main.py
