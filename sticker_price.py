# Testing file for sticker_price helper function

def sticker_price():
    
    # Placeholders for variables
    bvpsGrowthRate = .18
    analystGrowthRate = .174
    currentEPS = 10.29
    avgPE = 24.27

    growthRate = min(analystGrowthRate, bvpsGrowthRate)
    print(growthRate)

    futureEPS = currentEPS * ((1 + growthRate)**10)
    print(futureEPS)

    defaultPE = growthRate * 200
    print(defaultPE)

    estPE = min(avgPE, defaultPE)
    print(estPE)

    futureMarket = futureEPS * min(avgPE, defaultPE)
    print(futureMarket)

    sticker = futureMarket / 4
    print(sticker)

    safe = sticker / 2
    print(safe)

sticker_price()