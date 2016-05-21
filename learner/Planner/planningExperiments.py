__author__ = 'amir'

import Planner.pomcp.main
import Planner.mcts.main
import Planner.lrtdp.main
import Planner.lrtdp.LRTDPModule
import Diagnoser.diagnoserUtils
import HP_Random


import glob
import os
import csv
import Planning_Results

planners=[("mcts",Planner.mcts.main.main_mcts ),("lrtdp",Planner.lrtdp.main.mainModule),("HP",HP_Random.main_HP),
          ("Random",HP_Random.main_Random), ("initials", HP_Random.only_initials), ("all_tests", HP_Random.all_tests)]

def mkOneDir(dir):
    if not os.path.isdir(dir):
            os.mkdir(dir)

def runAll(instancesDir, outDir):
    for name,alg in planners:
        outD=os.path.join(outDir,name)
        mkOneDir(outD)
        for f in glob.glob(os.path.join(instancesDir,"*.txt")):
            print f
            file=os.path.join(instancesDir,f)
            outfile=os.path.join(outD,f.split("\\")[-1]+".csv")
            outData=[["Algorithm","precision", "recall", "steps"]] # header
            ei = Diagnoser.diagnoserUtils.readPlanningFile(file)
            outData=outData+[[name]+list(alg(ei.Copy()))]
            writer=csv.writer(open(outfile,"wb"))
            writer.writerows(outData)


def runAll_optimized(instancesDir, outDir):
    outData=[["planner","learn_algorithm","pBug","pValid","tests","index","precision","recall","steps" ]]
    outfile=os.path.join(outDir,"planningMED.csv")
    for f in glob.glob(os.path.join(instancesDir,"*.txt")):
        print f
        learn_alg,pBug,pValid,tests,index=Planning_Results.instance_name_to_meta(f.split("\\")[-1])
        file=os.path.join(instancesDir,f)
        ei = Diagnoser.diagnoserUtils.readPlanningFile(file)
        for name,alg in planners:
            precision,recall,steps=alg(ei.Copy())
            outData.append([name,learn_alg,pBug,pValid,tests,index,precision,recall,steps])
    writer=csv.writer(open(outfile,"wb"))
    writer.writerows(outData)



def planning_for_project(dir):
    for d in os.listdir(dir):
        if "." in d:
            continue
        if d=="weka":
            continue
        experiment_dir=os.path.join(dir,d)
        in_dir=os.path.join(experiment_dir,"planner")
        out_dir=os.path.join(experiment_dir,"new_planners")
        mkOneDir(out_dir)
        runAll(in_dir, out_dir)


def check__pomcp():
    file="C:\projs\ptry\lrtdp\\30_uniform_1.txt"
    file="C:\projs\ptry\lrtdp\\10_0.6_0.0_0.txt"
    ei=Diagnoser.diagnoserUtils.readPlanningFile(file)
    print Planner.pomcp.main.main(ei)
    print HP_Random.main_HP(ei)


def one_lrtdp(file, epsilon, out_dir, stack, trials):
    ei = Diagnoser.diagnoserUtils.readPlanningFile(file)
    instance = str(epsilon) + "_" + str(stack) + "_" + str(trials)
    instance_file = os.path.join(out_dir, instance + ".csv")

    Planner.lrtdp.LRTDPModule.setVars(ei.Copy(), epsilon, stack, trials)
    Planner.lrtdp.LRTDPModule.lrtdp()
    precision, recall, steps = Planner.lrtdp.LRTDPModule.evaluatePolicy()
    outData = [["Algorithm", "epsilon", "stack", "trials", "precision", "recall", "steps"]]  # header
    outData += [[instance, str(epsilon), str(stack), str(trials)] + list((precision, recall, steps))]
    writer = csv.writer(open(instance_file, "wb"))
    writer.writerows(outData)


def check_lrtdp(file, out_dir):
    epsilon_start, epsilon_end, epsilon_step = 0, 0.4, 0.4
    stack_start, stack_end, stack_step = 50, 100, 50
    trials_start, trials_end, trials_step = 5, 10, 5

    epsilon = epsilon_start
    while epsilon <= epsilon_end:
        stack = stack_start
        while stack <= stack_end:
            trials = trials_start
            while trials <= trials_end:
                one_lrtdp(file, epsilon, out_dir, stack, trials)
                trials += trials_step
            stack += stack_step
        epsilon +=epsilon_step

def lrtdp_multi_check(instances_dir, out_dir):
    for f in glob.glob(os.path.join(instances_dir,"*.txt")):
        print f
        file = os.path.join(instances_dir,f)
        out_instance_dir = os.path.join(out_dir, f.split("\\")[-1])
        if not  os.path.isdir(out_instance_dir):
            os.mkdir(out_instance_dir)
        check_lrtdp(file, out_instance_dir)


if __name__=="__main__":
    #check_lrtdp("","")
    lrtdp_multi_check("C:\projs\lrtdp\instances", "C:\projs\lrtdp\planners2")
    # inDir="C:\\projs\\planningTry\\in"
    # outDir="C:\\projs\\planningTry\\out"
    # runAll(inDir,outDir)

    # path=""
    # for x in ["cdt","orient","ant","poi"]:
    #     planning_for_project(os.path.join(path,x))
