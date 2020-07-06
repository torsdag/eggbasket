eggbasket
=========

Man in the middle license proxy. Written for giggles and allows you to setup a proxy counting license check outs per user / host and exporting them through prometheus. Currently only works with RLM license servers but should / could be made to work with other license servers that keep an active connection for each checkout. The idea falls to pieces if you have multiple licenses being served from the same license server.

Could be pretty neat to have a "generic" layer to control who can checkout licenses based on user / hostname allowing for limits based on departments etc..


prometheus metrics
=======
```
# HELP active_licenses_total active license count
# TYPE active_licenses_total counter
active_licenses_total{license="nuke"} 2.0
active_licenses_total{license="arnold"} 0.0
# HELP active_licenses active license count
# TYPE active_licenses gauge
active_licenses{active_licenses="active",host="172.xxx.xxx.32",license="nuke",port="43703",user="erhe"} 1.0
active_licenses{active_licenses="active",host="172.xxx.xxx.37",license="nuke",port="43703",user="erhe"} 1.0
```

install
=======

```
git clone git@github.com:torsdag/eggbasket.git
cd eggbasket
pip install -r requirements.txt
python setup.py install 

```

running
=======

```
python -m eggbasket -c config.json [ -p 8000 ] [ -v ]
```

Arguments:
- -c, --config: json config file, see below for an example ( required )
- -p, --port: prometheus exporter port ( default: 8000)
- -v, --verbose: verbose logging

example config
==============
```
{
    "licenses":
    [
        {
            "plugin": "RLM",
            "settings":{
                "name": "nuke",
                "port": 4101,
                "port_isv": 43703,
                "hostname": "foundry.domain.com"
            }
        },
        {
            "plugin": "RLM",
            "settings":{
                "name": "arnold",
                "port": 5059,
                "port_isv": 47980,
                "hostname": "arnold.domain.com"
            }
        }
    ]
}
```
