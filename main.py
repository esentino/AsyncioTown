from asyncio import Queue, create_task, run, sleep, Task
from pprint import pprint
from random import choice, randint, random
from typing import Tuple, List, Dict

from town import Asset, Material

materials_stock = {
    Material.FOOD: 0,
    Material.WOOD: 0,
    Material.STONE: 0,
    Material.IRON: 0,
}

assets_stats = {
    Asset.WORKER: 1,
    Asset.HOUSE: 1,
    Asset.FARM: 0,
    Asset.WOODWORK: 0,
    Asset.QUARRY: 0,
    Asset.MINE: 0,
}

async def compute_material_count(base_count: int, material: Material, assets: Dict[Asset, int])->int:
    material_assets_bonus = {
        Material.FOOD: [Asset.FARM],
        Material.WOOD: [Asset.WOODWORK],
        Material.STONE: [Asset.QUARRY],
        Material.IRON: [Asset.MINE],
    }
    bonus_assets = material_assets_bonus.get(material, [])
    total = base_count
    for asset in bonus_assets:
        total += assets.get(asset, 0)
    return total

async def find_material() -> Tuple[Material, int]:
    
    await_time = random()*4
    await sleep(await_time)
    found_material = choice(list(Material))
    material_count = randint(1,10)
    return found_material, material_count

async def worker(worker_id: int, queue: Queue)->None:
    print("Worker #{} start working".format(worker_id))
    while True:
        material, count = await find_material()
        print('Worker #{} find {} x {}'.format(worker_id, material, count))
        queue.put_nowait((material,count))

async def buy_worker_if_possible(materials: Dict[Material, int], assets: Dict[Asset, int]):
    house_capacity = 2
    food_needed = assets[Asset.WORKER] * 10
    house_capacity = assets[Asset.HOUSE] * house_capacity
    if materials[Material.FOOD] > food_needed and house_capacity > assets[Asset.WORKER]:
        materials[Material.FOOD] -= food_needed
        assets[Asset.WORKER] += 1
        print('Town buy new worker')

async def buy_house_if_possible(materials: Dict[Material, int], assets: Dict[Asset, int]):
    stone_needed = assets[Asset.HOUSE] * 10
    wood_needed = assets[Asset.HOUSE]*5
    if materials[Material.STONE] > stone_needed and materials[Material.WOOD]>wood_needed:
        materials[Material.STONE] -= stone_needed
        materials[Material.WOOD] -= wood_needed
        assets[Asset.HOUSE] += 1
        print('Town build new house')

async def spin_up_worker_if_needed(assets: Dict[Asset, int], tasks: List[Task], queue: Queue)->None:
    if len(tasks)< assets[Asset.WORKER]:
        task = create_task(worker(len(tasks)+1, queue))
        tasks.append(task)

async def take_assets_from_worker(materials: Dict[Material, int], assets: Dict[Asset, int], queue: Queue)->None:
    material, count = await queue.get()
    total_count = await compute_material_count(count, material, assets)
    print("Added {} X {} (+{})".format(material, count, total_count-count))
    materials[material] += total_count

async def game(materials: Dict[Material, int], assets: Dict[Asset, int])->None:
    tasks: List[Task] = []
    queue: Queue = Queue()
    while True:
        await spin_up_worker_if_needed(assets, tasks, queue)
        await take_assets_from_worker(materials, assets, queue)
        #pprint((materials, assets), compact=True)
        await buy_worker_if_possible(materials, assets)
        await buy_house_if_possible(materials, assets)
    
if __name__ == '__main__':
    run(game(materials_stock, assets_stats))
