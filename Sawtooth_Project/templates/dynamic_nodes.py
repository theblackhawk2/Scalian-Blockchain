import sys
import ruamel.yaml 

# / => !s!
# \ => !bs!
# ' => !q!
# " => !dq!
# \n => !r!

CONSENSUS    = {0 : "PBFT",
                1 : "POET"}

HEADER_FILE         = "header.yaml"
VALIDATOR_GEN_FILE  = "validator_gen_file.yaml"


yaml = ruamel.yaml.YAML()
yaml.preserve_quotes = True
yaml.indent(sequence=3, offset=1)
###### Specify user params #####
nodes = int(input("[+] Combien de noeuds dans votre réseau ? : [int] "))
consensus = CONSENSUS[int(input("[+] Quel consensus choisissez vous {}".format(CONSENSUS)))]

if consensus == "PBFT":
    # Charger le header
    with open(HEADER_FILE, "r") as ymlfile:
        header = yaml.load(ymlfile)
    save = open("save.yaml","w")
    
    for i in range(nodes):
        header["services"]["validator-"+str(i)] = {"image": "hyperledger/sawtooth-validator:1.1",
                           "container_name": "sawtooth-validator-"+str(i),
                           "volumes" : ["keys:/shared_keys"],
                           "expose": [4004,5050,8800],
                           "command":"Test command",
                           "stop_signal": "SIGKILL"}    
        header["services"]["rest-api-"+str(i)] = {"image": "hyperledger/sawtooth-rest-api:1.1",
                           "container_name": "sawtooth-rest-api-"+str(i),
                           "expose": [8008],
                           "command":"Test command",
                           "stop_signal": "SIGKILL"} 
        header["services"]["settings-tp-"+str(i)] = {"image": "hyperledger/sawtooth-settings-tp:1.1",
                           "container_name": "sawtooth-settings-tp-"+str(i),
                           "expose": [4004],
                           "command":"settings-tp -C tcp://validator-"+str(i)+":4004",
                           "stop_signal": "SIGKILL"} 
        header["services"]["intkey-tp-"+str(i)] = {"image": "hyperledger/sawtooth-intkey-tp-python:1.1",
                           "container_name": "sawtooth-intkey-tp-"+str(i),
                           "expose": [4004],
                           "command":"intkey-tp-python -C tcp://validator-"+str(i)+":4004",
                           "stop_signal": "SIGKILL"} 
        header["services"]["assets-tp-"+str(i)] = {"image": "hyperledger/sawtooth-all:1.1",
                           "container_name": "sawtooth-assets-tp-"+str(i),
                           "expose": [4004],
                           "volumes" : ["./Assets:/var/Assets"],
                           "command":"python3 /var/Assets/Assets_tp/main.py -C tcp://validator-"+str(i)+":4004",
                           "stop_signal": "SIGKILL"} 
        header["services"]["pbft-"+str(i)] = {"image": "sawtooth-pbft-engine-local",
                           "build" : {"context":"./sawtooth-pbft",
                                      "dockerfile":"./sawtooth-pbft/Dockerfile"},
                           "container_name": "sawtooth-pbft-"+str(i),
                           "volumes" : ["./sawtooth-pbft:/project/sawtooth-pbft","cargo-registry:/root/.cargo/registry","cargo-git:/root/.cargo/git"],
                           "working_dir": "/project/sawtooth-pbft/",
                           "command":"./target/debug/pbft-engine --connect tcp://validator-"+str(i)+":5050 -vv",
                           "stop_signal": "SIGKILL"} 
    # Configure validator-0
    val_0_comm = """!dq!bash -c !bs!!dq!!bs!!r!"""
    for i in range(1,nodes):
        val_0_comm+= "sawadm keygen validator-"+str(i)+" && !bs!!r!"
    val_0_comm+= "sawadm keygen && !bs!!r!"
    val_0_comm+= "sawset genesis !bs!!r!"
    val_0_comm+= " -k /etc/sawtooth/keys/validator.priv !bs!!r!"
    val_0_comm+= " -o config-genesis.batch && !bs!!r!"
    # Partie relative au consensus PBFT
    val_0_comm+= " sawset proposal create !bs!!r!"
    val_0_comm+= " -k /etc/sawtooth/keys/validator.priv !bs!!r!"
    val_0_comm+= " sawtooth.consensus.algorithm.name=pbft !bs!!r!"
    val_0_comm+= " sawtooth.consensus.algorithm.version=0.1 !bs!!r!"
    val_0_comm+= " sawtooth.consensus.pbft.members=!bs!!bs!["
    val_0_comm+= "!q!!bs!!bs!!bs!!dq!!q!$$(cat /etc/sawtooth/keys/validator.pub)!q!!bs!!bs!!bs!!dq!!q!,"
    val_0_comm+= (",").join(["!q!!bs!!bs!!bs!!dq!!q!$$(cat /etc/sawtooth/keys/validator-"+str(i)+".pub)!q!!bs!!bs!!bs!!dq!!q!" for i in range(1,nodes)])
    val_0_comm+= "!bs!!bs!] !bs!!r!"
    val_0_comm+= "sawtooth.consensus.pbft.block_duration=100 !bs!!r!"
    val_0_comm+= "sawtooth.consensus.pbft.view_change_timeout=4000 !bs!!r!"
    val_0_comm+= "sawtooth.consensus.pbft.message_timeout=10 !bs!!r!"
    val_0_comm+= "sawtooth.consensus.pbft.max_log_size=1000 !bs!!r!"
    val_0_comm+= "-o config.batch && !bs!!r!"
    # Fin partie Consensus
    val_0_comm+= "sawadm genesis !bs!!r!"
    val_0_comm+= "config-genesis.batch config.batch && !bs!!r!"
    val_0_comm+= "mv /etc/sawtooth/keys/validator-* /shared_keys && !bs!!r!"
    val_0_comm+= "echo $$(cat /etc/sawtooth/keys/validator.pub); !bs!!r!"
    val_0_comm+= "sawtooth-validator !bs!!r!"
    val_0_comm+= "--endpoint tcp://validator-0:8800 !bs!!r!"
    val_0_comm+= "--bind component:tcp://eth0:4004 !bs!!r!"
    val_0_comm+= "--bind network:tcp://eth0:8800 !bs!!r!"
    val_0_comm+= "--bind consensus:tcp://eth0:5050 !bs!!r!"
    val_0_comm+= "--peering static !bs!!r!"
    val_0_comm+= "--scheduler parallel !bs!!r!"
    val_0_comm+= "--maximum-peer-connectivity 3 !bs!!r!"
    val_0_comm+= "--opentsdb-db telegraf !bs!!r!"
    val_0_comm+= "--opentsdb-url http://influxdb:8086 !bs!!r!"
    val_0_comm+= "!bs!!dq!!dq!!r!"
    header["services"]["validator-0"]["command"] = val_0_comm
    # Configure rest_api_0
    rest_0_comm = "bash -c !dq! sawtooth-rest-api !bs!!r!"
    rest_0_comm += "--connect tcp://validator-0:4004 !bs!!r!"
    rest_0_comm += "--bind rest-api-0:8008 !bs!!r!"
    rest_0_comm += "--opentsdb-db telegraf !bs!!r!"
    rest_0_comm += "--opentsdb-url http://influxdb:8086 !dq!!r!"
    header["services"]["rest-api-0"]["command"] = rest_0_comm
    # Configuration des API Rest et Validateurs
    for i in range(1,nodes):
        valid_com = "!dq! bash -c !bs!!dq! !bs!!r!"
        valid_com += "while true; do if [ -e /shared_keys/validator-"+str(i)+".pub ]; then mv /shared_keys/validator-"+str(i)+".priv /etc/sawtooth/keys/validator.priv && mv /shared_keys/validator-"+str(i)+".pub /etc/sawtooth/keys/validator.pub; break; fi; sleep 0.5; done; !bs!!r!"
        valid_com += "echo $$(cat /etc/sawtooth/keys/validator.pub); !bs!!r!"
        valid_com += "sawtooth-validator !bs!!r!"
        valid_com += "--endpoint tcp://validator-"+str(i)+":8800 !bs!!r!"
        valid_com += "--bind component:tcp://eth0:4004 !bs!!r!"
        valid_com += "--bind network:tcp://eth0:8800 !bs!!r!"
        valid_com += "--bind consensus:tcp://eth0:5050 !bs!!r!"
        valid_com += "--peering static !bs!!r!"
        valid_com += "--peers "+",".join(["tcp://validator-"+str(j)+":8800" for j in range(i)])+"!r!"
        valid_com += "--scheduler parallel !bs!!r!"
        valid_com += "--maximum-peer-connectivity "+str(nodes)+" !bs!!r!"
        valid_com += "!bs!!dq!!dq! !r!"
        
        rest_com =  "bash -c !dq!"
        rest_com += "sawtooth-rest-api !bs!"
        rest_com += "--connect tcp://validator-"+str(i)+":4004 !bs!"
        rest_com += "--bind rest-api-"+str(i)+":8008"
        rest_com += "!dq!"

        header["services"]["rest-api-"+str(i)]["command"] = rest_com
        header["services"]["validator-"+str(i)]["command"] = valid_com
    yaml.dump(header,save)
elif consensus == "" :
    pass
else:
    print("[-] Choisissez un choix parmi les 2 consensus choisis ...")
###### 
