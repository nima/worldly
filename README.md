# worldly

```
╰─⠠⠵ make
. .venv/bin/activate && PYTHONSTARTUP=repl.py ipython
Python 3.9.9 (main, Nov 21 2021, 03:23:42) 
Type 'copyright', 'credits' or 'license' for more information
IPython 8.1.0 -- An enhanced Interactive Python. Type '?' for help.

To play a round:
>>> worldly.play.ask(*worldly.play.aRound())


In [1]: worldly.play.ask(*worldly.play.aRound())
Ruled by a Socialistic Republic government? (3 answers)? Lao
Wrong (hint: LD=4)
With an average elevation between 100 and 1,000 meters? (3 answers)? Cuba
Correct!
Out[1]: True

In [2]: 
```

Entity of Interest:
- Event
- People (The Kurds)
- Person

Locators:
- Region:
  - Country / Nation State
  - City / City State
  - Province, Oblast, State

- Time
 - Millenium
 - Century

Clues:
- <DeltaYears> years ago, HERE, <Person>:"Mao" did <Action>:"Killed 30M people"
- An <Event>:"Assasination" HERE, <DeltaYears> from now, will signal the birth of <Event>:"TheColdWar"
- In a land <Distance> miles away from HERE, the <People> are <Action>:"waging a war" on the native population of <Region>

# Anatomy of an Event
```python
What: str

People: str
Person: str
Who: Union[People, Person]

Year: int
Century: int
Millennium: int
When: Tuple[Year, Century, Millennium]

Province: str
City: str
Country: str
Continent: str
Region: str
Where: Union[Union[Province, City, Country, Continent], Region]

What: List[Description]

Id = Tuple[When, Where]
Description: Tuple[
    List[Who], List[When], List[Where], List[What]
]
Event = Tuple[Id, Description]
```

# Question Selection
```python
secret = random.choice(events)
axis = random.choice([secret.Who, secret.When, secret.Where])
clues = [
    clue for clue in clues if any(
        [
            clue.when in (
                secret.when,
                secret.what,
                secret.why,
            ),
            clue.where in (
                secret.where,
                secret.what,
                secret.why,
            ),
        ]
    )
]
```

- Select a secret category
- Select a secret from the secret bank
- Generate a list of clues that intersect with the secret in one axis
