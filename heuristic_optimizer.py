from agent import Agent
import math 
from random import *
VEC_LEN = 4
NUM_PLAYS = 50 #How many times of playing to determine fitness score 
NUM_GENES = 50 #How many "genes" total in the pool
NUM_REPLACE = 20 # In every generation, how many are replaced? 
SELECTION_POOL = 10 #In order to breed, SELECTION_POOL number of genes are pulled out of the gene pool, with the best 2 out of SELECTION_POOL being bred.
agent = Agent(width = 4, height = 6, delay = 0)
gene_pool = []

def pyth_length(v):
    return math.sqrt(sum([a*a for a in v]))

def normalize(v):
    l = pyth_length(v)
    return [float(a)/l for a in v]

def fitness(weights):
    agent.edit_weights(weights)
    res = [agent.play() for i in range(NUM_PLAYS)]
    return sum(res)

#generates a random vector on the unit circle/sphere/hypercircle/etc.
def gen_random(len):
    ret = [random()-0.5 for i in range(len)]
    return normalize(ret)

def breed(genefitness_a, genefitness_b):
    gene_a,fitness_a = genefitness_a
    gene_b,fitness_b = genefitness_b
    gene_a = [fitness_a*i for i in gene_a]
    gene_b = [fitness_b*i for i in gene_b]
    res = [sum(i) for i in zip(gene_a,gene_b)]
    return normalize(res)

def mutate(v):
    if(random() > 0.3):
        return normalize(v) #in most cases, we don't want to mutate
    new = v[:]
    victim_idx = randint(0,len(v)-1)
    amt = new[victim_idx] * uniform(0.95,1.05)
    new[victim_idx] = amt 
    return normalize(new) 

def perturb(v): #this function is like mutate, but changes the vector a little more...
    return normalize([uniform(0.5,2)*i for i in v])

# def sort_by_fitness(l):
#     l.sort(key=lambda x: x[1])


if __name__ == '__main__':
    handcrafted_gene = normalize([10, -20, 100, -0.5]) # Corresponds to 10*score -20*holes + 100*block fit -0.5*bumpiness
    print "BASELINE: fitness of the handcrafted gene is {}".format(fitness(handcrafted_gene))


    #The following starting gene pool is a random gene pool with one copy of our handcrafted gene inserted.
    starting_genes = [gen_random(VEC_LEN) for i in range(NUM_GENES-1)] + [handcrafted_gene]

    #The following starting gene pool is heavily based off the handcrafted gene, but perturbed in some way.
    #starting_genes = [perturb(handcrafted_gene) for i in range(NUM_GENES-1)]



    starting_fitness = [fitness(vec) for vec in starting_genes]
    gene_pool = zip(starting_genes, starting_fitness)

    while True:
        #generate new genes 
        new_genes = []
        for i in range(NUM_REPLACE):
            pool = sample(gene_pool, SELECTION_POOL)
            pool.sort(key=lambda x: x[1])
            mated = mutate(breed(pool[-1], pool[-2]))
            offspring_fitness = fitness(mated)
            new_genes.append((mated,offspring_fitness))

        #Now get rid of the bad genes 
        gene_pool.sort(key=lambda x: x[1])
        gene_pool = gene_pool[NUM_REPLACE:]
        gene_pool = gene_pool + new_genes
        gene_pool.sort(key=lambda x: x[1])
        print gene_pool[-1]
        print gene_pool[-2]
        print gene_pool[-3]