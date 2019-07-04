nodes = 30

class validator:
    def __init__(self,id):
        self.id = id
        self.image = "hyperledger/sawtooth-validator:1.1"
        self.container_name ="sawtooth-validator-"+str(self.id)
        self.expose  = ["4004", "5050", "8800"]
        self.volumes = ["./Assets:/var/Assets","keys:/shared_keys"]
        self.command = []
        self.stop_signal = "SIGKILL"
        
    def to_string(self):
        text  = "\n  validator-"+str(self.id)+":\n"
        text += "    image: "+self.image+"\n"
        text += "    container_name: "+self.container_name+"\n"
        text += "    volumes:\n"
        if self.id == 0:
            text+= "      - skeys:/dynamic_keys\n"
        

        for i in self.volumes:
            text+= "      - "+i+"\n"
        text += "    expose:\n"
        for port in self.expose:
            text+= "      - "+port+"\n"
        
        if self.id == 0:
            text+="    command: !dq!bash -c !bs!!dq!!bs!\n"
            for i in range(1,nodes):
                text += "        sawadm keygen validator-"+str(i)+" && !bs!\n"
            text+= "        sawadm keygen && !bs!\n"
            text+= "        sawset genesis !bs!\n"
            text+= "          -k /etc/sawtooth/keys/validator.priv !bs!\n"
            text+= "          -o config-genesis.batch && !bs!\n"
            #Partie relative au consensus pbft
            text+= "        sawset proposal create !bs!\n"
            text+= "          -k /etc/sawtooth/keys/validator.priv !bs!\n"
            text+= "          sawtooth.consensus.algorithm.name=pbft !bs!\n"
            text+= "          sawtooth.consensus.algorithm.version=0.1 !bs!\n"
            text+= "          sawtooth.consensus.pbft.members=!bs!!bs!["
            text+= "!q!!bs!!bs!!bs!!dq!!q!$$(cat /etc/sawtooth/keys/validator.pub)!q!!bs!!bs!!bs!!dq!!q!,"
            text+= (",").join(["!q!!bs!!bs!!bs!!dq!!q!$$(cat /etc/sawtooth/keys/validator-"+str(i)+".pub)!q!!bs!!bs!!bs!!dq!!q!" for i in range(1,nodes)])
            text+= "!bs!!bs!] !bs!\n"
            text+= "          sawtooth.consensus.pbft.block_duration=100 !bs!\n"
            text+= "          sawtooth.consensus.pbft.view_change_timeout=4000 !bs!\n"
            text+= "          sawtooth.consensus.pbft.message_timeout=40 !bs!\n"
            text+= "          sawtooth.consensus.pbft.max_log_size=1000 !bs!\n"
            text+= "          -o config.batch && !bs!\n"
            # Fin partie consensus
            text+= "        sawadm genesis !bs!\n"
            text+= "          config-genesis.batch config.batch && !bs!\n"
            text+= "        cp /etc/sawtooth/keys/validator* /dynamic_keys && !bs!\n"
            text+= "        mv /etc/sawtooth/keys/validator-* /shared_keys && !bs!\n"
            text+= "        echo $$(cat /etc/sawtooth/keys/validator.pub); !bs!\n"
            text+= "        sawtooth-validator !bs!\n"
            text+= "            --endpoint tcp://validator-0:8800 !bs!\n"
            text+= "            --bind component:tcp://eth0:4004 !bs!\n"
            text+= "            --bind network:tcp://eth0:8800 !bs!\n"
            text+= "            --bind consensus:tcp://eth0:5050 !bs!\n"
            text+= "            --peering static !bs!\n"
            text+= "            --scheduler parallel !bs!\n"
            text+= "            --maximum-peer-connectivity "+str(nodes)+" !bs!\n"
            text+= "            --opentsdb-db telegraf !bs!\n"
            text+= "            --opentsdb-url http://influxdb:8086 !bs!\n"
            text+= "    !bs!!dq!!dq!\n"
        else:
            text += "    command: !dq!bash -c !bs!!dq!!bs!\n"
            text += "        while true; do if [ -e /shared_keys/validator-"+str(self.id)+".pub ]; then mv /shared_keys/validator-"+str(self.id)+".priv /etc/sawtooth/keys/validator.priv && mv /shared_keys/validator-"+str(self.id)+".pub /etc/sawtooth/keys/validator.pub; break; fi; sleep 0.5; done; !bs!\n"
            text += "        echo $$(cat /etc/sawtooth/keys/validator.pub); !bs!\n"
            text += "        sawtooth-validator !bs!\n"
            text += "            --endpoint tcp://validator-"+str(self.id)+":8800 !bs!\n"
            text += "            --bind component:tcp://eth0:4004 !bs!\n"
            text += "            --bind network:tcp://eth0:8800 !bs!\n"
            text += "            --bind consensus:tcp://eth0:5050 !bs!\n"
            text += "            --peering static !bs!\n"
            text += "            --peers "+",".join(["tcp://validator-"+str(j)+":8800" for j in range(self.id)])+"\n"
            text += "            --scheduler parallel !bs!\n"
            text += "            --maximum-peer-connectivity "+str(nodes)+" !bs!\n"
            text += "    !bs!!dq!!dq!\n"
        text+="    stop_signal: SIGKILL\n\n"
        return text
class rest_api:
    def __init__(self,id):
        self.id = id
        self.image = "hyperledger/sawtooth-rest-api:1.1"
        self.container_name = "sawtooth-rest-api-"+str(self.id)
        self.expose = ["8008"]
        self.command = []
        self.stop_signal = "SIGKILL"

    def to_string(self):
        text = "\n  rest-api-"+str(self.id)+":\n"
        text+= "    image: hyperledger/sawtooth-rest-api:1.1\n"
        text+= "    container_name: sawtooth-rest-api-default-"+str(self.id)+"\n"
        text+= "    expose:\n"
        text+= "      - 8008\n"        
        text+= "    command: |\n"
        text+= "      bash -c !dq!\n"
        text+= "        sawtooth-rest-api !bs!\n"
        text+= "          --connect tcp://validator-"+str(self.id)+":4004 !bs!\n"
        text+= "          --bind rest-api-"+str(self.id)+":8008 !bs!\n"
        if self.id == 0:
            text+= "          --opentsdb-db telegraf !bs!\n"
            text+= "          --opentsdb-url http://influxdb:8086\n\n"
        
        text+= "      !dq!\n"
        text+= "    stop_signal: SIGKILL\n\n"
        return text

class pbft:
    def __init__(self,id):
        self.id = id
        self.image = "sawtooth-pbft-engine-local"
        self.build = "    build:\n"
        self.build += "      context: ./sawtooth-pbft\n"
        self.build += "      dockerfile: ./sawtooth-pbft/Dockerfile\n"
        self.volumes = ["./sawtooth-pbft:/project/sawtooth-pbft","cargo-registry:/root/.cargo/registry","cargo-git:/root/.cargo/git"]
        self.working_dir = "/project/sawtooth-pbft/"
        self.command = "./target/debug/pbft-engine --connect tcp://validator-"+str(self.id)+":5050 -vv"
    
    def to_string(self):
        text = "\n  pbft-"+str(self.id)+":\n"
        text+= "    image: "+self.image+"\n"
        text+= self.build    
        text+= "    volumes:\n"
        for i in self.volumes:
            text+= "      - "+i+"\n"
        text+= "    working_dir: "+self.working_dir+"\n"
        text+= "    command: "+self.command+"\n"
        text+= "    stop_signal: SIGKILL\n\n"
        return text

class settings_tp:
    def __init__(self,id):
        self.id = id
        self.image = "hyperledger/sawtooth-settings-tp:1.1"
        self.container_name = "sawtooth-settings-tp-"+str(self.id)
        self.expose = ['4004']
        self.command = "settings-tp -C tcp://validator-"+str(self.id)+":4004"
        self.stop_signal = "SIGKILL"

    def to_string(self):
        text = "\n  settings-tp-"+str(self.id)+":\n"
        text+= "    image: "+self.image+"\n"
        text+= "    container_name: "+self.container_name+"\n"
        text+= "    expose:\n"
        text+= "      - 4004\n"
        text+= "    command: "+self.command+"\n"
        text+= "    stop_signal: SIGKILL\n\n"
        return text

class intkey_tp:
    def __init__(self,id):
        self.id = id
        self.image = "hyperledger/sawtooth-intkey-tp-python:1.1"
        self.container_name = "sawtooth-intkey-tp-"+str(self.id)
        self.expose = ['4004']
        self.command = "intkey-tp-python -C tcp://validator-"+str(self.id)+":4004"
        self.stop_signal = "SIGKILL"

    def to_string(self):
        text = "\n  intkey-tp-"+str(self.id)+":\n"
        text+= "    image: "+self.image+"\n"
        text+= "    container_name: "+self.container_name+"\n"
        text+= "    expose:\n"
        text+= "      - 4004\n"
        text+= "    command: "+self.command+"\n"
        text+= "    stop_signal: SIGKILL\n\n"
        return text

class assets_tp:
    def __init__(self,id):
        self.id = id
        self.image = "hyperledger/sawtooth-all:1.1"
        self.container_name = "assets-tp-"+str(self.id)
        self.volumes = ["./Assets:/var/Assets"]
        self.expose = ['4004']
        self.command = "python3 /var/Assets/Assets_tp/main.py -C tcp://validator-"+str(self.id)+":4004"
        self.stop_signal = "SIGKILL"


if __name__ == "__main__":
    
    file = open("all_in_one.yaml","w")
    for i in range(nodes):
        V = validator(i)
        R = rest_api(i)
        S = settings_tp(i)
        I = intkey_tp(i)
        P = pbft(i)
        L = [V, R, S, I, P]
        for Object in L:
            file.write(Object.to_string())

    file.close()

