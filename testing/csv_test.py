import csv

with open ('links.csv', 'w', newline='') as links:
    writer = csv.writer(links, delimiter='\n')
    writer.writerow(['Eric']*5)
    