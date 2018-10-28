import api.access as _

def main(queen, ressourceAvailables, pheromonesList):
    _.seqstart(queen.color)
    _.info("tick")
    _.seqend()
    return _.WAIT
