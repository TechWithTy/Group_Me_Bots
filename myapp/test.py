import os
from dotenv import load_dotenv

load_dotenv()

zb_promo = os.environ.get('ZB_PROMO')
twin_nem = os.environ.get('TWIN_NEM')
print(zb_promo)