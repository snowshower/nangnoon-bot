from .lotto import lotto
from .lotto_rank import lotto_rank
from collections import defaultdict

class lotto_result_calculator:
    
    @staticmethod
    def lotto_result_calculator(winning_lotto: lotto, my_lotto: lotto) -> lotto_rank:
        winning_numbers=set(winning_lotto.numbers)
        my_numbers=set(my_lotto.numbers)
        match_count=len(winning_numbers & my_numbers)
        
        return lotto_rank.value_of(match_count)
    
    @staticmethod
    def calculate_all_results(winning_lotto: lotto, my_lottos: list[lotto]) -> dict[lotto_rank, int]:
        
        results=defaultdict(int)
        
        for lotto in my_lottos:
            rank=lotto_result_calculator.lotto_result_calculator(winning_lotto, lotto)
            results[rank]+=1
        
        return dict(results)