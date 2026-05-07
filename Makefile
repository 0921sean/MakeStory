.PHONY: daily kora health

daily:
	python hazel_nut_story/daily/hazel_nut_story.py

kora:
	python kora_valley/kora_valley_tracking.py

health:
	python healthfam/healthfam.py
