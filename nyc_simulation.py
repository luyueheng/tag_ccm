import json
from typing import Tuple, Dict
from rule import TransferRule
from tag_ccm import TagCCM
from block import Block

import numpy as np

TAGS = {
    'age': [
        '0-4',
        '5-9',
        '10-14',
        '15-19',
        '20-24',
        '25-29',
        '30-34',
        '35-39',
        '40-44',
        '45-49',
        '50-54',
        '55-59',
        '60-64',
        '65-69',
        '70-74',
        '75-79',
        '80-84',
        '85-89',
        '90+',
    ],
    'gender': ['M', 'F']
}

def get_next_age(age: str) -> str:
    i = int(age.split('-')[0])
    return '{}-{}'.format(i+5, i+9) if i != 85 else '90+'

class NYCFertilityRule(TransferRule):

    required_tags = set(['age', 'gender'])

    firtility_rate = {
        '15-19': 213.636,
        '20-24': 465.702,
        '25-29': 442.975,
        '30-34': 430.578,
        '35-39': 242.561,
        '40-44': 69.008,
        '45-49': 4.958,
    }

    @classmethod
    def apply(cls, block: Block) -> Tuple[Dict[str, str], int]:
        age, gender = block.block_tags['age'], block.block_tags['gender']
        if gender == 'M' or age not in cls.firtility_rate:
            return None, None
        new_born = int(block.current / 1000 * cls.firtility_rate[age])
        return {'age': '0-4'}, new_born

class NYCMortalityRule(TransferRule):

    required_tags = set(['age'])

    survival_rate = {
        '0-4': 0.997,
        '5-9': 1.000,
        '10-14': 1.000,
        '15-19': 1.000,
        '20-24': 0.998,
        '25-29': 0.997,
        '30-34': 0.996,
        '35-39': 0.993,
        '40-44': 0.989,
        '45-49': 0.986,
        '50-54': 0.979,
        '55-59': 0.971,
        '60-64': 0.952,
        '65-69': 0.928,
        '70-74': 0.891,
        '75-79': 0.836,
        '80-84': 0.765,
        '85-89': 0.666,
        # '90+': 0.426
    }

    @classmethod
    def apply(cls, block: Block) -> Tuple[Dict[str, str], int]:
        age = block.block_tags['age']
        if age == '90+':
            return None, None
        contribution = int(block.current * cls.survival_rate[age])
        return {**block.block_tags, 'age': get_next_age(age)}, contribution

class NYCNetMigrationRule(TransferRule):

    required_tags = set(['age'])

    # netmigration rate over 20 years
    net_migration_rate = {
        '0-4': -129.805,
        '5-9': -24.512,
        '10-14': 24.233,
        '15-19': 20.334,
        '20-24': 137.325,
        '25-29': 193.871,
        '30-34': -3.064,
        '35-39': -57.660,
        '40-44': -5.013,
        '45-49': -36.211,
        '50-54': 33.983,
        '55-59': -79.108,
        '60-64': -32.311,
        '65-69': -67.409,
        '70-74': -102.506,
        '75-79': -47.910,
        '80-84': -123.955,
        '85-89': -157.103,
        '90+': -38.161
    }

    @classmethod
    def apply(cls, block: Block) -> Tuple[Dict[str, str], int]:
        age = block.block_tags['age']
        contribution = block.current / 1000 * cls.net_migration_rate[age] / 4
        return block.block_tags, contribution

def main():
    # simulation start from 2000
    male_population_by_age = [
        276635,
        286155,
        270582,
        265285,
        285353,
        326702,
        335119,
        322637,
        289976,
        250093,
        220318,
        165458,
        139938,
        112153,
        95920,
        73139,
        44146,
        34595 // 2,
        34595 // 2
    ]
    female_population_by_age = [
        264243,
        274960,
        260234,
        255356,
        304478,
        353957,
        352243,
        338264,
        312403,
        281025,
        260949,
        203647,
        174411,
        147014,
        139707,
        120082,
        83993,
        87108 / 2,
        87108 / 2,
    ]
    blocks = [
        Block({'gender': 'M', 'age': TAGS['age'][i]}, male_population_by_age[i])
        for i in range(len(male_population_by_age))
    ] + [
        Block({'gender': 'F', 'age': TAGS['age'][i]}, female_population_by_age[i])
        for i in range(len(female_population_by_age))
    ]

    T = TagCCM(blocks, [NYCFertilityRule, NYCMortalityRule, NYCNetMigrationRule], [], TAGS)

    result_male = [[p] for p in male_population_by_age]
    result_female = [[p] for p in female_population_by_age]
    for _ in range(6):  # until 2030
        T.step()
        for i, age in enumerate(TAGS['age']):
            result_male[i].append(T.block_pool[json.dumps({'gender': 'M', 'age': age}, sort_keys=True)].current)
            result_female[i].append(T.block_pool[json.dumps({'gender': 'F', 'age': age}, sort_keys=True)].current)
    
    print('Male:')
    for r in result_male:
        print(r)
    print(np.array(result_male).sum(axis=0))
    print('Female:')
    for r in result_female:
        print(r)
    print(np.array(result_female).sum(axis=0))

if __name__ == '__main__':
    main()
