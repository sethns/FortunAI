import matplotlib.pyplot as plt
from typing import List


MIKE="Partrick Brady"
ROHIT="Dragan Zivkovic"
VIRAT="Michael McNamara"

CLIENT_LIST: List[str] = [MIKE, ROHIT, VIRAT]

def show_portfolio(client):
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels = 'SCB', 'HSBC', 'Barclays', 'GS', 'Morgan Stanley', 'DBS'
    sizes = [15, 10, 25, 20, 10, 20]
    rupee = [1500, 1000, 2500, 2000, 1000, 2000]
    explode = (0, 0.1, 0, 0,0,0)  # only "explode" the 2nd slice (i.e. 'Hogs')
    if(client==VIRAT):
        labels = 'SCB', 'HSBC', 'Barclays', 'UBS', 'JPMC'
        sizes = [20, 20, 20, 20, 20]
        explode = (0, 0, 0, 0, 0.1)
    elif(client==ROHIT):
        labels = 'UBS', 'Barclays', 'HSBC', 'DBS', 'SCB'
        sizes = [25, 15, 25, 20, 15]
        explode = (0, 0, 0, 0.1, 0)
    else:
        labels = 'SCB', 'HSBC', 'Barclays', 'GS', 'Morgan Stanley', 'DBS'
        sizes = [15, 10, 25, 20, 10, 20]
        explode = (0, 0.1, 0, 0, 0, 0)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    return fig1