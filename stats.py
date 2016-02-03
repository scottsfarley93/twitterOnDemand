__author__ = 'scottsfarley'
print "Running."
import numpy
import numpy.random
import matplotlib.pyplot as plt
import pandas
## input params
numIters = 100
numTrials = 100000
p = 0.01
n = 20
s = 2


expected = (n-s) * p**s # theoretical solution we came up with

allX = []
allY = []
allProbs = []

w = 0
while w < numIters: ##number of experiments requested
    x = []
    y = []
    t = 0
    total = 0
    while t < numTrials: # iterate through all requested simulations for each experiment
        # for plotting
        if t != 0:
            prob = total / float(t + 1)
            x.append(t)
            y.append(prob)
        i = 0
        trials = []
        while i < n: ## generate n number of individual bernoulli trials
            trials.append(int(numpy.random.binomial(1, p, 1)))
            i +=1
        q = 0
        while q < n-s:
            prevTrials = []
            e = q
            while e < (q + s):
                prevTrials.append(trials[e])
                e += 1
            if sum(prevTrials) == s:
                total += 1
                break
            q += 1

        t += 1
    ## for plotting
    allX.append(x)
    allY.append(y)
    allProbs.append(prob) ## this is the final result of the experiment using numTrials simulations
    print "Finished iteration #" + str(w)
    print "Iteration probability is", prob
    w += 1

prob = numpy.mean(allProbs)
sd = numpy.std(allProbs)
upperCI = prob + 2*sd
lowerCI = prob - 2*sd

print allProbs
print "Expected probability is", expected
print "Mean probability at iteration", numTrials, "is", prob
print "Lower CI (95): ", lowerCI
print "Upper CI (95): ", upperCI
if expected > lowerCI and expected < upperCI:
    print "Expected value is within simulation confidence limits."
plt.hist(allProbs)
plt.title("Histogram of probability of consecutive 100 year events\n" + str(s) + " consecutive events in " + str(n) + " years with an independent probability of " + str(p) )
plt.xlabel("Probability of consecutive events")
plt.ylabel("Probability density")
plt.show()
theMatrix = []
i = 0
theMatrix.append(allX[0])
while i < numIters:
    theMatrix.append(allY[i])
    i += 1
df = pandas.DataFrame(theMatrix)
df = df.transpose()

plt.plot(df)
plt.ylim([0, 0.015])
plt.title("Simulation of Consecutive 100 Year Flood Events\n# Simulations: " + str(numIters) + "\t# of iterations: " + str(numTrials))
plt.xlabel("Iteration")
plt.ylabel("Probability of occurrence")
plt.show()