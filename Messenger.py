import requests
import confi
import logging

user = confi.user
password = confi.password
key = confi.key

def log_details():
    logging.basicConfig(
        filename="Automation.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %p",
        #force=True
    )
    return logging.getLogger()




def text(message, number):
    logger = log_details()
    resp = requests.post('https://textbelt.com/text', {
        'phone': number,
        'message': message,
        'key': key,
    })
    print(resp.json())
    logger.info(resp.json())
    resp.close()
