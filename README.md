# Visual Cripto mobile app
This project is intended to test a new way of authentication based
on visual cryptography and is the first part of the authentication model. 
Includes an interface for selecting a .png file, and inserting the selected 
image into the outline of the encrypted image on the camera frames.
### Installation

Install python packages:

```
$ pip install -r requirements.txt
```

and install buildozer: 

```
$ git clone https://github.com/kivy/buildozer.git
$ cd buildozer
$ sudo python setup.py install
```

### Create .apk file for android
```
$ buildozer init
$ buildozer android debug deploy run
```

