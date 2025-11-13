LOTTO_NUMBER_COUNT=6
MIN_LOTTO_NUMBER=1
MAX_LOTTO_NUMBER=45

class lotto:
    
    def __init__(self, numbers: list[int]):
        if len(numbers)!=LOTTO_NUMBER_COUNT:
            raise ValueError("[ERROR]: 로또 번호는 6개여야 합니다!")
        if len(set(numbers))!=LOTTO_NUMBER_COUNT:
            raise ValueError("[ERROR]: 로또 번호는 중복될 수 없습니다!")
        if any(n<MIN_LOTTO_NUMBER or n>MAX_LOTTO_NUMBER for n in numbers):
            raise ValueError("[ERROR]: 로또 번호는 1~45 사이여야 합니다!")
        
        self.numbers=sorted(numbers)
    
    @property
    def get_numbers(self) -> tuple[int]:
        return tuple(self.numbers)