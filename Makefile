
flash-mp:


min-sprinkler: sprinkler-firmware \
			   boot.py \
			   main_sprinklers_mqtt.py \
			   settings.py \
			   ST7735.py \
			   sysfont.py \
			   utils.py
	pyminify boot.py > sprinkler-firmware/boot.py
	pyminify main_sprinklers_mqtt.py > sprinkler-firmware/main.py
	pyminify settings.py > sprinkler-firmware/settings.py
	pyminify ST7735.py > sprinkler-firmware/ST7735.py
	pyminify sysfont.py > sprinkler-firmware/sysfont.py
	pyminify utils.py > sprinkler-firmware/utils.py


put-sprinkler-firmware: sprinkler-firmware
	 ampy --port COM3 put sprinkler-firmware/boot.py
	 ampy --port COM3 put sprinkler-firmware/main.py
	 ampy --port COM3 put sprinkler-firmware/settings.py
	 ampy --port COM3 put sprinkler-firmware/ST7735.py
	 ampy --port COM3 put sprinkler-firmware/sysfont.py
	 ampy --port COM3 put sprinkler-firmware/utils.py
