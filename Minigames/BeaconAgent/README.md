
## Beacon Agent
#### Description

A map with 1 Marine and 1 Beacon. Rewards are earned by moving the marine to the
beacon. Whenever the Marine earns a reward for reaching the Beacon, the Beacon
is teleported to a random location (at least 5 units away from Marine).

#### Initial State

*   1 Marine at random location (unselected)
*   1 Beacon at random location (at least 4 units away from Marine)

#### Rewards

*   Marine reaches Beacon: +1

#### End Condition

*   Time elapsed 120 seconds


#### Algortithms
*   IDS and Bellmanford, to select algo to run please go to [Params.py](Params.py) and choose true, for the type of search selected.
