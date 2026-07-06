import csv
import json
majors = {
	"TS": "Travel and Service Business Entrepreneurship",
	"CS": "Computer Science",
	"CH": "Chemistry",
	"IR": "Intl Relations and Global Affairs",
	"IB": "International Business",
	"MC": "Media and Communication",
	"IL": "Intercultural Studies and Language",
	"CT": "Creative Technology",
	"MK": "Marketing",
	"AM": "Applied Mathematics",
	"FT": "Food Science and Technology",
	"BE": "Business Economic",
	"BS": "Biological Science",
	"FN": "Finance",
	"CE": "Computer Engineering",
	"CD": "Communication Design"
}
majorslk = {v: k for k, v in majors.items()}

major_relevance = {
  "TS": ["TS", "IB", "MK", "MC", "IL", "BE"],
  "CS": ["CS", "CE", "CT", "AM", "CD", "MC"],
  "CH": ["CH", "BS", "FT", "AM"],
  "IR": ["IR", "IL", "IB", "MC", "BE"],
  "IB": ["IB", "BE", "MK", "FN", "IR", "TS"],
  "MC": ["MC", "CD", "CT", "MK", "IL", "IB"],
  "IL": ["IL", "IR", "MC", "TS", "IB"],
  "CT": ["CT", "CD", "CS", "CE", "MC"],
  "MK": ["MK", "IB", "MC", "BE", "TS"],
  "AM": ["AM", "CS", "CE", "CH", "BS"],
  "FT": ["FT", "CH", "BS"],
  "BE": ["BE", "IB", "FN", "MK", "IR"],
  "BS": ["BS", "CH", "FT", "AM"],
  "FN": ["FN", "BE", "IB", "MK"],
  "CE": ["CE", "CS", "CT", "AM"],
  "CD": ["CD", "CT", "MC", "CS"]
}

major_relevancecmm = {
	"TS": ["TS", "IB", "MK", "MC", "IL", "BE", "CS", "CH", "IR", "CT", "AM", "FT", "BS", "FN", "CE", "CD"],
	"CS": ["CS", "CE", "CT", "AM", "CD", "MC", "TS", "CH", "IR", "IB", "IL", "MK", "FT", "BE", "BS", "FN"],
	"CH": ["CH", "BS", "FT", "AM", "TS", "CS", "IR", "IB", "MC", "IL", "CT", "MK", "BE", "FN", "CE", "CD"],
	"IR": ["IR", "IL", "IB", "MC", "BE", "TS", "CS", "CH", "CT", "MK", "AM", "FT", "BS", "FN", "CE", "CD"],
	"IB": ["IB", "BE", "MK", "FN", "IR", "TS", "CS", "CH", "MC", "IL", "CT", "AM", "FT", "BS", "CE", "CD"],
	"MC": ["MC", "CD", "CT", "MK", "IL", "IB", "TS", "CS", "CH", "IR", "AM", "FT", "BE", "BS", "FN", "CE"],
	"IL": ["IL", "IR", "MC", "TS", "IB", "CS", "CH", "CT", "MK", "AM", "FT", "BE", "BS", "FN", "CE", "CD"],
	"CT": ["CT", "CD", "CS", "CE", "MC", "TS", "CH", "IR", "IB", "IL", "MK", "AM", "FT", "BE", "BS", "FN"],
	"MK": ["MK", "IB", "MC", "BE", "TS", "CS", "CH", "IR", "IL", "CT", "AM", "FT", "BS", "FN", "CE", "CD"],
	"AM": ["AM", "CS", "CE", "CH", "BS", "TS", "IR", "IB", "MC", "IL", "CT", "MK", "FT", "BE", "FN", "CD"],
	"FT": ["FT", "CH", "BS", "TS", "CS", "IR", "IB", "MC", "IL", "CT", "MK", "AM", "BE", "FN", "CE", "CD"],
	"BE": ["BE", "IB", "FN", "MK", "IR", "TS", "CS", "CH", "MC", "IL", "CT", "AM", "FT", "BS", "CE", "CD"],
	"BS": ["BS", "CH", "FT", "AM", "TS", "CS", "IR", "IB", "MC", "IL", "CT", "MK", "BE", "FN", "CE", "CD"],
	"FN": ["FN", "BE", "IB", "MK", "TS", "CS", "CH", "IR", "MC", "IL", "CT", "AM", "FT", "BS", "CE", "CD"],
	"CE": ["CE", "CS", "CT", "AM", "TS", "CH", "IR", "IB", "MC", "IL", "MK", "FT", "BE", "BS", "FN", "CD"],
	"CD": ["CD", "CT", "MC", "CS", "TS", "CH", "IR", "IB", "IL", "MK", "AM", "FT", "BE", "BS", "FN", "CE"]
}

for i,v in major_relevance.items():
	print(majors[i])
	n = 1
	for k in v:
		print(f" {n:2d})",majors[k])
		n+=1

def sdumps(d):
	items = []
	pad = "\t"
	for k, v in d.items():
		items.append(f'{pad}{json.dumps(str(k))}:{json.dumps(v)}')
	return "{\n" + ",\n".join(items) + "\n}"

#						 0		 1			2		   3		  4		5			 6				7
tableheader = ["name", "nick", "major", "email", "id", "tel", "instagram", "ncount"] 

with open("excess.csv", encoding="utf-8") as f:
	nlist = list(csv.reader(f))
with open("cmm.csv", encoding="utf-8") as f:
	plist = list(csv.reader(f))


def ltojson(l):
	result = {}
	for row in l:
		if not row:
			continue
		key = row[4]
		value = [v for i,v in enumerate(row) if i != 4]
		value[3] = value[3].lower().strip()
		value[1] = value[1].strip()
		value[2] = value[2].strip()
		value[4] = value[4].strip()
		value[5] = value[5].strip()
		if int(key) < 6880000:
			value[6] = int(value[6])
		result[key] = value
	return result

open("userdata.json", "w", encoding="utf-8").write(sdumps(ltojson(nlist) | ltojson(plist)))

# validation
def validate(l):
	seen = set()
	c = 0
	for i in l:
		output = i[4]
		wrong = 0
		if i[4] in seen:
			output += " Duplicated ID"
			wrong = 1
		if not i[3].strip().lower().endswith("@student.mahidol.edu"):
			output += " Invalid Email"
			wrong = 1
		if wrong:
			print(output)
		c+=wrong
		seen.add(i[4])
	return c

if validate(plist) != 0 or validate(nlist) != 0:
	print("data validation failed")
	exit(1)
print("data validation passed // loaded into memory :", id(plist), id(nlist))

nmajor = {}

for i,v in majors.items():
	#print(v)
	nmajor[i]=[]

for i in nlist:
	nmajor[majorslk[i[2]]].append(i)

# balanced distribution algorithm, work in passes
# each pass gives everyone 1 of a matching major n'code (or closest major possible)
pairlist = {}


for i in range(6):
	satisfied = True
	for p in plist:
		stid = int(p[4])
		major = p[2]
		intake = int(p[7])
		majorcode = majorslk[major]
		takinglist = pairlist.get(stid) or []
		remaining = len(takinglist) - intake
		if remaining == 0:
			continue
		satisfied = False
		for closest in major_relevancecmm[majorcode]:
			if len(nmajor[closest]) == 0:
				continue
			n = nmajor[closest].pop(0)
			takinglist.append(int(n[4]))
			break
		pairlist[stid] = takinglist

print(sdumps(pairlist))
print("Satisfied :",satisfied)
open("secrethugpair.json", "w", encoding="utf-8").write(sdumps(pairlist))

excess = ""

for i,v in nmajor.items():
	while v:
		k = v.pop(0)
		excess+=",".join(k)+"\n"

open("excess2.csv", "w", encoding="utf-8").write(excess)
