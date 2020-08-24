# Python script for requesting data from DMIs open API

> make sure to have placed a `key.txt` file in the root folder. 

Copy and paste the key into the text file, such that it is the first line and the only content:
```txt
ol1ju542-23g3-jgks-4l7j-bcn4i8dje092
```

A key can be acquired [at DMIs webpage for free data.](https://confluence.govcloud.dk/pages/viewpage.action?pageId=26476690) <br>
[Meteorological station IDs can be located here](https://confluence.govcloud.dk/pages/viewpage.action?pageId=26476619). <br>
[Parameter IDs can be located here.](https://confluence.govcloud.dk/pages/viewpage.action?pageId=26476616).

## Getting started

To get an overview of what arguments exist, type `help`:
```cmd
python dmir.py --help
```

The following example requests temperature data from a defined period from station 06126 (Arslev). The data is limited to 24 entries and by default exported as a CSV file with name `mydataname`.
```cmd
python dmir.py --station 06126 --type temp_mean_past1h --from 2018/4/1 --to 2018/4/2 --limit 24 --fname mydataname
```

## Dependencies

The following modules must be installed:

* requests 
* pandas

```cmd
> pip install %package%
```
