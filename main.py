from asyncio import Queue, Task, create_task, run, sleep
from pprint import pprint
from random import choice, randint, random
from typing import Dict, List, Tuple

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
        await sleep(0)
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
    stone_needed = assets[Asset.HOUSE] * 30
    wood_needed = assets[Asset.HOUSE]*15
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
    queue.task_done()

async def buy_quarry_if_possible(materials: Dict[Material, int], assets: Dict[Asset, int])->None:
    stone_needed = (assets[Asset.QUARRY] + 1) * 10 
    worker_needed = 1
    food_needed = assets[Asset.QUARRY] * 2
    if materials[Material.STONE] > stone_needed and assets[Asset.WORKER] > worker_needed and materials[Material.FOOD] > food_needed:
        materials[Material.STONE] -= stone_needed
        materials[Material.FOOD] -= food_needed
        assets[Asset.WORKER] -= worker_needed
        assets[Asset.QUARRY] += 1
        print('Town build new quarry')

async def buy_woodwork_if_possible(materials: Dict[Material, int], assets: Dict[Asset, int])->None:
    wood_needed = (assets[Asset.WOODWORK] + 1) * 10
    food_needed = assets[Asset.WOODWORK] * 4
    stone_needed = (assets[Asset.WOODWORK] + 1) * 3
    worker_needed = 1
    enought_wood = materials[Material.WOOD] > wood_needed
    enought_food = materials[Material.FOOD] > food_needed
    enought_stone = materials[Material.STONE] > stone_needed
    enought_worker = assets[Asset.WORKER] > worker_needed 
    if all([enought_wood, enought_food, enought_stone, enought_worker]):
        materials[Material.WOOD] -= wood_needed
        materials[Material.FOOD] -= food_needed
        materials[Material.STONE] -= stone_needed
        assets[Asset.WORKER] -= worker_needed
        assets[Asset.WOODWORK] += 1
        print('Town build new quarry')

async def buy_mine_if_possible(materials: Dict[Material, int], assets: Dict[Asset, int])->None:
    iron_needed = (assets[Asset.MINE] + 1) * 10
    wood_needed = (assets[Asset.MINE] + 1) * 3
    food_needed = (assets[Asset.MINE] + 1) * 2
    worker_needed = 3
    stone_needed = (assets[Asset.MINE] + 1) * 5
    enought_food = materials[Material.FOOD] > food_needed
    enought_stone = materials[Material.STONE] > stone_needed
    enought_wood = materials[Material.WOOD] > wood_needed
    enought_worker = assets[Asset.WORKER] > worker_needed
    enought_iron = materials[Material.IRON] > iron_needed
    if all([enought_food, enought_food, enought_stone, enought_wood, enought_worker, enought_iron]):
        materials[Material.IRON] -= iron_needed
        materials[Material.WOOD] -= wood_needed
        materials[Material.FOOD] -= food_needed
        materials[Material.STONE] -= stone_needed
        assets[Asset.WORKER] -= worker_needed
        assets[Asset.MINE] += 1

async def buy_farm_if_possible(materials: Dict[Material, int], assets: Dict[Asset, int])->None:
    wood_needed = (assets[Asset.FARM] + 1) * 2
    stone_needed = (assets[Asset.FARM] + 1) * 1
    food_needed = (assets[Asset.FARM] + 1) * 1
    worker_needed = 1
    enought_food = materials[Material.FOOD] > food_needed
    enought_stone = materials[Material.STONE] > stone_needed
    enought_wood = materials[Material.WOOD] > wood_needed
    enought_worker = assets[Asset.WORKER] > worker_needed
    if all([enought_food, enought_stone, enought_wood, enought_worker]):
        materials[Material.FOOD] -= food_needed
        materials[Material.STONE] -= stone_needed
        materials[Material.WOOD] -= wood_needed
        assets[Asset.WORKER] -= worker_needed
        assets[Asset.FARM] += 1

async def spin_down_worker_if_needed(assets: Dict[Asset, int], tasks: List[Task])->None:
    while len(tasks)> assets[Asset.WORKER]:
        worker_to_stop = tasks.pop()
        worker_to_stop.cancel()
        print('Town stop worker')
        await sleep(0)

async def game(materials: Dict[Material, int], assets: Dict[Asset, int])->None:
    tasks: List[Task] = []
    queue: Queue = Queue()
    while True:
        await spin_up_worker_if_needed(assets, tasks, queue)
        await take_assets_from_worker(materials, assets, queue)
        await buy_worker_if_possible(materials, assets)
        await buy_house_if_possible(materials, assets)
        await buy_quarry_if_possible(materials, assets)
        await buy_farm_if_possible(materials, assets)
        await buy_woodwork_if_possible(materials, assets)
        await buy_mine_if_possible(materials, assets)
        await spin_down_worker_if_needed(assets, tasks)
        print((materials, assets))
if __name__ == '__main__':
    run(game(materials_stock, assets_stats))
