LOTTO_NUMBER_COUNT=6
MIN_LOTTO_NUMBER=1
MAX_LOTTO_NUMBER=45

import random

def generate_lotto():
    lotto=random.sample(range(MIN_LOTTO_NUMBER,MAX_LOTTO_NUMBER+1), k=LOTTO_NUMBER_COUNT)
    return sorted(lotto)