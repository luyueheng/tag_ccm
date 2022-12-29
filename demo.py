import sys
import json
from tag_ccm import TagCCM
from rule import *

DEFAULT_POPULATION = 10000

def demo1():
    TAGS = {
        "age": ["0-10", "10-20", "20-30", "30-40", "40-50", "50-60", "60-70", "70-80", "80-90", "90-100"],
        "gender": ["M", "F"]
    }
    initial_block_tags = [
        '{"age": "10-20", "gender": "M"}',
        '{"age": "10-20", "gender": "F"}',
        '{"age": "20-30", "gender": "M"}',
        '{"age": "20-30", "gender": "F"}',
        '{"age": "30-40", "gender": "M"}',
        '{"age": "30-40", "gender": "F"}',
        '{"age": "40-50", "gender": "M"}',
        '{"age": "40-50", "gender": "F"}',
        '{"age": "50-60", "gender": "M"}',
        '{"age": "50-60", "gender": "F"}',
        '{"age": "60-70", "gender": "M"}',
        '{"age": "60-70", "gender": "F"}',
        '{"age": "70-80", "gender": "M"}',
        '{"age": "70-80", "gender": "F"}',
        '{"age": "80-90", "gender": "M"}',
        '{"age": "80-90", "gender": "F"}',
        '{"age": "90-100", "gender": "M"}',
        '{"age": "90-100", "gender": "F"}'
    ]
    blocks = [Block(json.loads(tags_json), DEFAULT_POPULATION) for tags_json in initial_block_tags]
    T = TagCCM(blocks, [MortalityRule, BirthRule], [], TAGS)

    print('initial state:')
    T.print_blocks()

    T.step()
    print('step 1 * 10 years:')
    T.print_blocks()

    T.step(10)
    print('step 10 * 10 years:')
    T.print_blocks()

def demo2():
    TAGS = {
        "age": ["0-10", "10-20", "20-30", "30-40", "40-50", "50-60", "60-70", "70-80", "80-90", "90-100"],
        "gender": ["M", "F"],
        "race": ["race1", "race2", "race3"]
    }
    initial_block_tags = [
        '{"age": "0-10", "gender": "M", "race": "race1"}',
        '{"age": "0-10", "gender": "F", "race": "race1"}',
        '{"age": "10-20", "gender": "M", "race": "race1"}',
        '{"age": "10-20", "gender": "F", "race": "race1"}',
        '{"age": "20-30", "gender": "M", "race": "race1"}',
        '{"age": "20-30", "gender": "F", "race": "race1"}',
        '{"age": "30-40", "gender": "M", "race": "race1"}',
        '{"age": "30-40", "gender": "F", "race": "race1"}',
        '{"age": "0-10", "gender": "M", "race": "race2"}',
        '{"age": "0-10", "gender": "F", "race": "race2"}',
        '{"age": "10-20", "gender": "M", "race": "race2"}',
        '{"age": "10-20", "gender": "F", "race": "race2"}',
        '{"age": "20-30", "gender": "M", "race": "race2"}',
        '{"age": "20-30", "gender": "F", "race": "race2"}',
        '{"age": "30-40", "gender": "M", "race": "race2"}',
        '{"age": "30-40", "gender": "F", "race": "race2"}',
        '{"age": "0-10", "gender": "M", "race": "race3"}',
        '{"age": "0-10", "gender": "F", "race": "race3"}',
        '{"age": "10-20", "gender": "M", "race": "race3"}',
        '{"age": "10-20", "gender": "F", "race": "race3"}',
        '{"age": "20-30", "gender": "M", "race": "race3"}',
        '{"age": "20-30", "gender": "F", "race": "race3"}',
        '{"age": "30-40", "gender": "M", "race": "race3"}',
        '{"age": "30-40", "gender": "F", "race": "race3"}',
    ]
    blocks = [Block(json.loads(tags_json), DEFAULT_POPULATION) for tags_json in initial_block_tags]
    T = TagCCM(blocks, [MortalityRule, BirthWithRaceRule], [NetMigrationRule], TAGS)

    print('initial state:')
    T.print_blocks()

    T.step()
    print('step 1 * 10 years:')
    T.print_blocks()

    T.step(10)
    print('step 10 * 10 years:')
    T.print_blocks()

def demo3():
    TAGS = {
        'age': [str(i) for i in range(100)],
        'gender': ['M', 'F'],
        'race': ['race1', 'race2', 'race3']
    }
    initial_block_tags = [
        {'age': str(i), 'gender': g, 'race': r}
        for i in range(10, 40) for g in TAGS['gender'] for r in TAGS['race']
    ]
    blocks = [Block(tags, DEFAULT_POPULATION) for tags in initial_block_tags]
    T = TagCCM(blocks, [MortalityRule, BirthRule], [NetMigrationRule], TAGS)
    
    def print_by_tag():
        for g in TAGS['gender']:
            print(g)
            for r in TAGS['race']:
                sum, n = 0, 0
                for a in TAGS['age']:
                    key = json.dumps({'age': a, 'gender': g, 'race': r}, sort_keys=True)
                    sum += T.block_pool[key].current if key in T.block_pool else 0
                    n += 1
                    if n == 10:
                        print(sum, end=', ')
                        sum, n = 0, 0
                print()
    
    print('initial state:')
    print_by_tag()

    T.step()
    print('step 1 years:')
    print_by_tag()

    T.step(10)
    print('step 10 years:')
    print_by_tag()

demos = [None, demo1, demo2, demo3]

if __name__ == '__main__':
    idx = int(sys.argv[1])
    demos[idx]()
