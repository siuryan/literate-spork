from app import models, db

f = open( 'classes.csv', 'r' )

content = f.readlines()

for line in content:
    line = line.split(',')
    c = models.SchoolClass(name = line[0],
                           period = int(line[1]),
                           teacher = line[2].strip())
    db.session.add(c)
    
db.session.commit()
