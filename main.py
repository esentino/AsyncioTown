from asyncio import sleep, Queue, run, create_task
from enum import Enum, auto
from random import choice, random, randint
from pprint import pprint
class Material(Enum):
    FOOD = auto()
    WOOD = auto()
    STONE = auto()
    IRON = auto()

class Asset(Enum):
    WORKER = auto()
    HOUSE = auto()
    FARM = auto()
    WOODWORK = auto()
    QUARRY = auto()
    MINE = auto()   

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

async def compute_material_count(base_count: int, found_material: Material, assets: dict):

    if found_material == Material.FOOD:
        return base_count + assets[Asset.FARM]
    if found_material == Material.WOOD:
        return base_count + assets[Asset.WOODWORK]
    if found_material == Material.STONE:
        return base_count + assets[Asset.QUARRY]
    if found_material == Material.IRON:
        return base_count + assets[Asset.MINE]

async def find_material():
    
    await_time = random()*4
    await sleep(await_time)
    found_material = choice(list(Material))
    material_count = randint(1,10)
    return found_material, material_count


async def worker(worker_id, queue: Queue):
    while True:
        material, count = await find_material()
        print('Worker #{} find {} x {}'.format(worker_id, material, count))
        queue.put_nowait((material,count))

async def game(materials, assets):
    tasks = []
    queue = Queue()
    while True:
        if len(tasks)< assets[Asset.WORKER]:
            task = create_task(worker(len(tasks)+1, queue))
            tasks.append(task)
        material, count = await queue.get()
        materials[material] += await compute_material_count(count, material, assets)
        pprint(materials)
        if materials[Material.FOOD] > assets[Asset.WORKER] * 10:
            materials[Material.FOOD] -= assets[Asset.WORKER] * 10
            assets[Asset.WORKER] += 1
if __name__ == '__main__':
    run(game(materials_stock, assets_stats))