from enum import Enum

class lotto_rank(Enum):
    FIRST=(2_000_000_000, "1등!")
    SECOND=(30_000_000, "2등!")
    THIRD=(1_500_000, "3등!")
    FOURTH=(5_000, "4등!")
    FIFTH=(1_000, "5등!")
    MISS = (0, "꽝!")
    
    @staticmethod
    def value_of(match_count: int) -> 'lotto_rank':
        if match_count==6:
            return lotto_rank.FIRST
        if match_count==5:
            return lotto_rank.SECOND
        if match_count==4:
            return lotto_rank.THIRD
        if match_count==3:
            return lotto_rank.FOURTH
        if match_count==2:
            return lotto_rank.FIFTH
        return lotto_rank.MISS
    
    @property
    def prize_amount(self) -> int:
        return self.value[0]
    
    @property
    def description(self) -> str:
        return self.value[1]