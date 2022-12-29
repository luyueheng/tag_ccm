from block import Block
from typing import Dict, Tuple, List

def get_next_age(age):
    if age.isnumeric():
        return str(int(age)+1)
    highend = int(age.split('-')[1])
    return '{}-{}'.format(highend, highend + 10)

def get_age_range(age):
    if age.isnumeric():
        i = int(age)
        return '{}-{}'.format(i-i%10, i-i%10+10)
    return age

class TransferRule:

    required_tags = set()
    apply_to = {}

    @classmethod
    def apply(cls, block: Block) -> Tuple[Dict[str, str], int]:
        raise NotImplementedError()

    @classmethod
    def check_tags(cls, block: Block):
        return (cls.required_tags - set(block.block_tags.keys())) == set()

class GenerativeRule:

    required_tags = set()

    @classmethod
    def apply(cls, tags: Dict[str, str]) -> List[Tuple[Dict[str, str], int]]:
        raise NotImplementedError()

class MortalityRule(TransferRule):

    required_tags = set(['age'])

    # source: https://ourworldindata.org/grapher/death-rate-by-age-group-in-england-and-wales
    mortality_rate_by_age_group = {
        '0-10': 0.0042, 
        '10-20': 0.0003, 
        '20-30': 0.0008, 
        '30-40': 0.0015, 
        '40-50': 0.0034, 
        '50-60': 0.0079, 
        '60-70': 0.0196, 
        '70-80': 0.0534, 
        '80-90': 0.1075
    }

    @classmethod
    def apply(cls, block: Block) -> Tuple[Dict[str, str], int]:
        if not cls.check_tags(block):
            return None, None
        age = block.block_tags['age']
        if age == '90-100' or (age.isnumeric() and int(age) >= 90):
            return None, None
        contribution = int(block.current * (1.0 - cls.mortality_rate_by_age_group[get_age_range(age)]))
        return {**block.block_tags, 'age': get_next_age(age)}, contribution

class BirthRule(TransferRule):

    required_tags = set(['age', 'gender'])

    # source: https://www.statista.com/statistics/445305/live-births-by-age-of-mother-england-wales/
    birth_rate_by_age_group = {
        '10-20': 0.0112, 
        '20-30': 0.1367, 
        '30-40': 0.1666, 
        '40-50': 0.0165,
    }

    @classmethod
    def apply(cls, block: Block) -> Tuple[Dict[str, str], int]:
        if not cls.check_tags(block):
            return None, None
        age, gender = block.block_tags['age'], block.block_tags['gender']
        age_range = get_age_range(age)
        if gender == 'M' or age_range not in cls.birth_rate_by_age_group:
            return None, None
        contribution = int(block.current * cls.birth_rate_by_age_group[age_range])
        return {'age': '0' if age.isnumeric() else '0-10'}, contribution

class BirthWithRaceRule(TransferRule):

    required_tags = set(['age', 'gender', 'race'])

    # source: https://www.statista.com/statistics/445305/live-births-by-age-of-mother-england-wales/
    base_birth_rate_by_age_group = {
        '10-20': 0.0112, 
        '20-30': 0.1367, 
        '30-40': 0.1666, 
        '40-50': 0.0165,
    }

    # Mocked data
    race_factor = {
        'race1': 1.2,
        'race2': 0.8,
        'race3': 1.0,
    }

    @classmethod
    def apply(cls, block: Block) -> Tuple[Dict[str, str], int]:
        if not cls.check_tags(block):
            return None, None
        age, gender, race = block.block_tags['age'], block.block_tags['gender'], block.block_tags['race']
        age_range = get_age_range(age)
        if gender == 'M' or age_range not in cls.base_birth_rate_by_age_group:
            return None, None
        contribution = int(block.current * cls.base_birth_rate_by_age_group[age_range] * cls.race_factor[race])
        return {'race': race, 'age': '0' if age.isnumeric() else '0-10'}, contribution

class NetMigrationRule(GenerativeRule):
    required_tags = set(['race', 'age'])

    # Mocked data
    base_net_migration_by_age_group = {
        '0-10': 100,
        '10-20': 200,
        '20-30': 300,
        '30-40': 400,
        '40-50': 300,
        '50-60': 300,
        '60-70': 100,
        '70-80': 10,
        '80-90': 0,
        '90-100': 0,
    }

    # Mocked data
    race_factor = {
        'race1': 2.0,
        'race2': 0.5,
        'race3': 1.0,
    }

    @classmethod
    def apply(cls, tags: Dict[str, str]) -> List[Tuple[Dict[str, str], int]]:
        if (cls.required_tags - set(tags.keys())) != set():
            return []
        return [
            (
                {'age': age, 'race': race},
                int(cls.base_net_migration_by_age_group[get_age_range(age)] * cls.race_factor[race])
            )
            for age in tags['age'] for race in cls.race_factor
        ]