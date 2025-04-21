import configparser



#Read config.ini file
config_obj = configparser.ConfigParser()
# Path to configfile
config_obj.read(r"C:\configfile.ini")
userinfo = config_obj["user_info"]


#set your parameters for link using the keys from configfile.ini

user = userinfo["login"]
password = userinfo["password"]
key = userinfo["key"]

host = userinfo["host"]
dbUser = userinfo["dbUser"]
dbPassword = userinfo["dbPassword"]
dataBase = userinfo["database"]




