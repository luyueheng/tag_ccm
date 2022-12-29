import json
from typing import Dict

class Block:
    
    def __init__(self, block_tags: Dict[str, str], current: int) -> None:
        self.block_tags = block_tags
        self.current = current
        self.next = 0

    def __repr__(self) -> str:
        return "({}, {}, {})".format(Block.serialize(self), self.current, self.next)

    @classmethod
    def serialize(cls, block: "Block"):
        return json.dumps(block.block_tags, sort_keys=True)

    @classmethod
    def deserialize(cls, block_str: str, TAGS: Dict[str, str]):
        block_tags = json.loads(block_str)
        if len(block_tags) != len(TAGS):
            raise Exception("Number of values does not match number of tags")
        return Block(block_tags, 0)
