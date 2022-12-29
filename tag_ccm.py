import json
from block import Block
from rule import TransferRule, GenerativeRule
from collections import defaultdict
from typing import Dict, List

# Example of tags
# TAGS = {
#     "age": ["0-10", "10-20", "20-30", "30-40", "40-50", "50-60", "60-70", "70-80", "80-90", "90-100"],
#     "gender": ["M", "F"]
# }

class TagCCM:

    def __init__(
        self,
        blocks: List[Block],
        transfer_rules: List[TransferRule],
        generative_rules: List[GenerativeRule],
        TAGS: Dict[str, str]
    ) -> None:
        self.TAGS = TAGS
        self.block_pool = {}
        self.block_filter = {tag: defaultdict(set) for tag in TAGS}
        self.transfer_rule = transfer_rules
        self.generative_rule = generative_rules

        for block in blocks:
            self.new_block(block)
    
    def filter(self, condition: Dict[str, str]):
        # filter by condition is needed because:
        # - need to apply to subset of blocks by condition: e.g. net migration
        # - need to contribute to multiple blocks by condition: e.g. new born
        result = set(self.block_pool.keys())
        for tag, value in condition.items():
            result = result.intersection(self.block_filter[tag][value])
        return [self.block_pool[k] for k in result]

    def new_block(self, block: "Block"):
        self.block_pool[Block.serialize(block)] = block
        for tag, value in block.block_tags.items():
            self.block_filter[tag][value].add(Block.serialize(block))

    def permutate_blocks_by_filter(self, condition: Dict[str, str]):
        # use BFS to permutate all blocks given a condition
        result = [{}]
        for t, values in self.TAGS.items():
            if t in condition:
                values = [condition[t]]
            new_result = []
            for block in result:
                for v in values:
                    new_result.append({**block, t: v})
            result = new_result
        return [json.dumps(b, sort_keys=True) for b in result]
    
    def contribute(self, condition: Dict[str, str], population: int):
        to_blocks = self.permutate_blocks_by_filter(condition)
        for b in to_blocks:
            if b not in self.block_pool:
                self.new_block(Block.deserialize(b, self.TAGS))
            self.block_pool[b].next += population // len(to_blocks)

    def _step(self):
        # transfer rules
        for rule in self.transfer_rule:
            for block in self.filter(rule.apply_to):
                contribute_to, population = rule.apply(block)
                if contribute_to is None:
                    continue
                self.contribute(contribute_to, population)
        # generative rules
        for rule in self.generative_rule:
            contributions = rule.apply(self.TAGS)
            for contribute_to, population in contributions:
                self.contribute(contribute_to, population)
        
        for block in self.block_pool.values():
            block.current, block.next = max(0, block.next), 0

    def step(self, times=1):
        for _ in range(times):
            self._step()

    def print_blocks(self):
        for block in self.block_pool.values():
            print(block)
