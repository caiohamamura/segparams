#! /usr/bin/env python

"""
Very simple demo in which organisms try to minimise
the output value of a function
"""

from pygene.gene import FloatGene
from pygene.organism import Organism, MendelOrganism
from pygene.population import Population
from rbsb import rbsb
from subprocess import call
from sys import exit
from sys import argv
from segbaatz import SegBaatz
from numpy import round as npround
from os import access, F_OK, environ
global arr, n
arr = [[None]]
try:
    n=int(argv[5])
except:
    n=1
print n
def usage():
    print "python segparams.py input_raster reference_shape [output_shape] [fitnesslog_file] [populationlog_file]"
    exit()

def getdir(path):
    i=0
    if path.find('/',i) != -1 :
        while path.find('/', i) != -1:
            i = path.find('/', i)+1
            out = path[0:i]
    else:
        while path.find('\\', i) != -1:
            i = path.find('\\', i)+1
            out = path[0:i]
    return out

if len(argv) < 3:
    usage()
global ref, seg, img, logpath
img=argv[1]
ref=argv[2]
try:
    seg=argv[3]
except:
    seg=getdir(ref)+"result.shp"
    
if access(img, F_OK) and access(ref, F_OK):
    pass
else:
    print "Path for image or reference segments not available"
    usage()
seg2=seg[:-4]
home = environ.get("USERPROFILE")
logpath=home+"/logbaatz.txt"
poplog=home+"/poplog.txt"

class comp(FloatGene):
    """
    Gene which represents the numbers used in our organism
    """
    # genes get randomly generated within this range
    randMin = 0.0
    randMax = 1.0
    
    # probability of mutation
    mutProb = 0.4
    
    # degree of mutation
    mutAmt = 0.3

class color(FloatGene):
    """
    Gene which represents the numbers used in our organism
    """
    # genes get randomly generated within this range
    randMin = 0.2
    randMax = 1.0
    
    # probability of mutation
    mutProb = 0.4
    
    # degree of mutation
    mutAmt = 0.3

class weights(FloatGene):
    """
    Gene which represents the numbers used in our organism
    """
    # genes get randomly generated within this range
    randMin = 0.0
    randMax = 1.0
    
    # probability of mutation
    mutProb = 0.4
    
    # degree of mutation
    mutAmt = 0.3

class weights1(FloatGene):
    """
    Gene which represents the numbers used in our organism
    """
    # genes get randomly generated within this range
    randMin = 0.5
    randMax = 1.0
    
    # probability of mutation
    mutProb = 0.4
    
    # degree of mutation
    mutAmt = 0.3

class scale(FloatGene):
    """
    Gene which represents the numbers used in our organism
    """
    # genes get randomly generated within this range
    randMin = 15
    randMax = 40
    
    # probability of mutation
    mutProb = 0.4
    mutAmt = 1
    
    # degree of mutation

class Params(MendelOrganism):
    """
    Implements the organism which tries
    to converge a function
    """
    genome = {'s':scale, 'w1':weights1, 'w2':weights, 'w3':weights, 'c':comp, 'col':color}
    
    def fitness(self):
        """
        Implements the 'fitness function' for this species.
        Organisms try to evolve to minimise this function's value
        """
        global arr, ref, seg, img, n
        fit = None
        w1,w2,w3,c,col,s=self['w1'],self['w2'],self['w3'],self['c'],self['col'], self['s']
        for i in arr:
            if i[1:7] == [w1,w2,w3,c,col,s]:
                fit = i[0]
                break;
        if not fit:
            try:
                SegBaatz(img, seg2+str(n), str(s), str(c),str(col),str(w1),str(w2),str(w3))
                fit = rbsb(ref,seg2+str(n)+".shp")
            except:
                print "scale: %s, compactness: %s, color: %s, weights: %s %s %s" % (str(s), str(c), str(col), str(w1),str(w2), str(w3))
                writepop()
                exit()
            arr.insert(0,[fit, w1,w2,w3,c,col,s])
            print "%s %s %s %s %s %s %s\n" % (s,c, col,w1,w2,w3,fit)
            writelog("Individuo %s:\n%s %s %s %s %s %s %s\n" % (n, s,c, col,w1,w2,w3,fit))
            n+=1
        return fit
    def __repr__(self):
        return "<Fitness=%f scale=%s compactness=%s color=%s weigths=%s,%s,%s>" % (
            self.fitness(), self['s'], self['c'], self['col'], self['w1'], self['w2'], self['w3'])

def writepop():
    xmlfile = open(poplog, "a")
    for j in range(0,len(pop)):
        xmlfile.write(str(pop[int(j)].genes).replace(': ', '*').replace('<', '').replace(':', '(').replace('>',')').replace('*', ': ')+'\n')
    xmlfile.write('\n')
    xmlfile.write(str(arr)+'\n')
    xmlfile.write('\n\n')
    xmlfile.close()

def writelog(what):
    file = open(logpath, 'a')
    file.write(what)
    file.close()
# create an empty population
try:
    popfile = open(argv[3], 'r')
    pop = Population(species=Params, init=0, incest=3)
    i = popfile.readline()[:-1]
    while len(i) > 1:
        org = Params()
        org.genes = eval(i)
        pop.add(org)
        i = popfile.readline()[:-1]
    i = popfile.readline()[:-1]
    if len(i)>1:
        arr = eval(i)
    print "ok"
except:
    pop = Population(species=Params, init=8, incest=3)

# now a func to run the population

    
def main():
    global logpath, arr, n
    try:
        out=int(argv[4])
    except:
        out = 0
    numChild=6
    popCull=5
    i=0
    if n > 1:
        i=((n+1-8)/popCull)
    else:
        i=0
        writelog("--------------------------"+str(out)+"--------------------------\nSCALE COMPACTNESS COLOR W1 W2 W3 FITNESS\n")
    best = None
    try:
        while True:
            writelog("==================\n==  Geracao: %s  ==\n==================\n" % i)
            # execute a generation
            if i == 0:
                pass
            else:
                pop.gen(popCull,numChild/2)
            # get the fittest member
            best2 = pop.best()
            if best != None:
                if best2.fitness() == best[0].fitness():
                    pass
                else:
                    best = [best2,str(i)]
            else:
                best = [best2,str(i)]
            # and dump it out
            print str(best2) + "\n Na geracao " + str(i) 
            writelog("----MELHOR----\n" + str(best[0].fitness()) + " na geracao " + str(best[1]) + "\n")
            i+=1
            if i > 10:
                out+=1
                writepop()
                writelog("\n\n")
                call(["C:/Windows/system32/shutdown.exe",'-f', '-s', '-t', '00'])
                exit()

    except KeyboardInterrupt:
        writepop()
        writelog("\n\n")
        pass


if __name__ == '__main__':
    main()
