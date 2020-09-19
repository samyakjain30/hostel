r = csv.reader(open('Student_Data_List.csv'))
lines = list(r)

lines[0][0]='S'

with open('Student_List.csv', 'w') as csvfile:
	filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
	filewriter.writerows(lines)

with open('Student_List.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
    	print(row)

os.remove('Student_Data_List.csv')
os.remove('Student_List.csv')