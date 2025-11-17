from hmac import new
from multiprocessing import Process,Manager,Value
import random,time,copy
import pandas as pd

new_caught_rate = 0.01
old_caught_rate = 0.1

def worker(virusPool,antigens,mutations,nutritions,white_cell,orginal_virus,started):
    i = 0
    while i < 10000:
        if virusPool.empty():
            if started.value == False:
                started.value = True
                virusPool.put(copy.deepcopy(orginal_virus))
            continue
        virus = virusPool.get()
        if random.random() < 0.5:
            virus['nutrition_take'] -= 1
            nutritions.value += 1
            virusPool.put(virus)
            continue

        for _ in range(20):
            if nutritions.value < 2:
                continue

            new_sequence = ''.join([s if random.choices(mutations,weights = [0.1,0.1,0.1,0.1,0.6],k=1)[0] == None else random.choice(mutations[:-1]) for s in list(virus['sequence'])])

            survive_chance = random.random()
           
            if new_sequence not in antigens and survive_chance <new_caught_rate:
                if white_cell.value >5:
                    white_cell.value -=1
                    antigens.append(new_sequence)
                    time.sleep(0.2)
                    white_cell.value +=1
            elif new_sequence in antigens and survive_chance < old_caught_rate:
                if white_cell.value >5:
                    white_cell.value -=1
                    time.sleep(0.1)
                    white_cell.value +=1
                continue
            else:
                with nutritions.get_lock():
                    if nutritions.value >=20:
                        nutritions.value -= 20
                        virus_nutrition = 20
                    else:
                        virus_nutrition = nutritions.value
                        nutritions.value = 0

                new_virus = {'sequence':new_sequence,'nutrition_take':virus_nutrition}
                virusPool.put(new_virus)
        virus_nutrition += virus['nutrition_take']
        print(f"body has {virusPool.qsize()} viruses")
        i += 1
                

def main():
    virusPool = Manager().Queue()
    antigens = Manager().list()
    orginal_virus =  {'sequence':"aabbcdd",'nutrition_take':20}
    mutations = ['a','b','c','d',None]
    nutritions = Value('i',100000)
    white_cell = Value('i',50)
    started = Value('b',False)

    pool = []
    for _ in range(100):
        p = Process(target=worker, args=(virusPool,antigens,mutations,nutritions,white_cell,orginal_virus,started))
        time.sleep(0)
        p.start()
        pool.append(p)

    for p in pool:
        p.join()


    survived_virus = []
    while not virusPool.empty():
        survived_virus.append(virusPool.get())
    
    virus_grid = pd.DataFrame(survived_virus)
    virus_grid.to_csv('macro_test_output.csv',index=False)

if __name__ == '__main__':
    main()