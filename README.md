# web-page

## Instructions
### Clone the most recent ase
```
$ git clone https://gitlab.com/ase/ase.git
```

### Copy the modified scripts from `ase_db` to ase repo
```
	modified:   ase/db/app.py
	modified:   ase/db/row.py
	modified:   ase/db/table.py
	added:      ase/db/plotly_band.py
	modified:   ase/db/templates/row.html
```

### Go to ase repo and reinstall ase package by
```
$ python setup install
```

### Copy and unzip the jsmol.zip to the ase/db/static
To see the 3D structure, one needs to copy the jsmol file to the static folder `Installation/ase/db/static/jsmol`

### View database

```
$ ase db tp01.db -w
```
