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
	modified:   ase/db/core.py
	added:      ase/db/plotly_band.py
	modified:   ase/db/templates/*.html
	added:      ase/db/static/logo.* 

```

### Go to ase repo and reinstall ase package by
```
$ python setup.py install
```

### Copy and unzip the jsmol.zip to the ase/db/static
To see the 3D structure, one needs to copy the jsmol file (`ase_db/static/jsmol.zip`)
to the static folder (`Installation_of_ase/ase/db/static/jsmol`)

An example is given as follows,
```
cp -r ase/db/static/jsmol/* /anaconda3/lib/python3.6/site-packages/ase-3.20.0b1-py3.6.egg/ase/db/static/jsmol
```
### View database

```
$ ase db tp02.db -w
```
Then open browser with the url of http://0.0.0.0:5000/ 
