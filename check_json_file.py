# encoding=utf-8
import json
from loguru import logger


def read_json_cfg(config_path):
	try:
		with open(config_path) as f:
			ret = json.load(f)
	except Exception as e:
		logger.exception(e)
		print("配置文件格式错误，请检查！")
		return -1
	return ret


config_path = input('input:')
read_json_cfg(config_path)
