from gurobipy import *

# Todo:
# 1. Modify wahlpflicht and anwendungsfach based on your curriculum modules
# 2. Input your grades
# 3. (Install Gurobipy)
# 4. Run the program

# Q & A
# Q: Why are the PSP and SPP  not listed?
# A: Because their grades are not used for the calculation of the final grade (PO § 10 (5)), so please don't add them.

modules, credits, grades, weight, excludable = multidict({
    "Progra": [8, 0, 1, True],
    "Dsal": [8, 0, 1, True],
    "SWT": [6, 0, 1, True],
    "debis": [6, 0, 1, True],
    "ti": [6, 0, 1, True],
    "bus": [6, 0, 1, True],
    "datkom": [6, 0, 1, True],
    "fosap": [6, 0, 1, True],
    "buk": [7, 0, 1, True],
    "malo": [7, 0, 1, True],
    "DS": [6, 0, 1, True],
    "Afi": [8, 0, 1, True],
    "LA": [6, 0, 1, True],
    "Stocha": [6, 0, 1, True],
    "prosem": [3, 0, 1, True],
    "Seminar": [5, 0, 1, True],
    "BachelorArbeit": [15, 0, 1.5, False],
    "wahlpflicht1": [6, 0, 1, True],
    "wahlpflicht2": [6, 0, 1, True],
    "wahlpflicht3": [6, 0, 1, True],
    "wahlpflicht4": [6, 0, 1, True],
    "Anwendungsfach1": [8, 0, 1, True],
    "Anwendungsfach2": [6, 0, 1, True],
    "Anwendungsfach3": [4, 0, 1, True],
    "Anwendungsfach4": [4, 0, 1, True],
})

# Conflicts: Per PO you are only allowed to remove on module grade per module area
conflicts = [("Progra","Dsal","SWT","debis"),("ti","bus","datkom"),("fosap","buk","malo"),("DS","Afi","LA","Stocha"),("Anwendungsfach1","Anwendungsfach2","Anwendungsfach3","Anwendungsfach4")]

def solve(modul, credits, note, gewichtung, streichbar):
    model = Model("Streichrechner ")

    model.modelSense = GRB.MINIMIZE

    # variable x
    x = {}
    for m in modul:
        x[m] = model.addVar(name="exlude_%s" % (m), vtype=GRB.BINARY)

    model.update()

    for m in modul:
        if not streichbar[m]:
            model.addConstr(x[m] == 0, name="module not excludable"+str(m))
    model.addConstr(quicksum(x[m] * credits[m] for m in modul) <= 30, name="max 30 credits excludable")
    for conflict in conflicts:
        model.addConstr(quicksum(x[m] for m in conflict) <= 1, name="max 1 per conflict excludable")

    model.setObjective(quicksum((1-x[m]) * credits[m] * gewichtung[m] * note[m] for m in modul))
    model.optimize()

    # print solution
    if model.status == GRB.OPTIMAL:
        print('\n objective: %g\n' % model.ObjVal)
        total_credits = 0
        for m in modul:
            if x[m].x >= 1:
                print('Exclude %s' % (m))
            else:
                total_credits += credits[m] * gewichtung[m]
        print("Final grade:"+str(model.ObjVal/total_credits))

    return model

solve(modules, credits, grades, weight, excludable)