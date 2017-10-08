#Simple MQTT Client publishing example for Google Cloud Platform
import datetime
import os
import time
import paho.mqtt.client as mqtt
import jwt

project_id = 'pro-adapter-182205'
cloud_region = 'us-central1'
registry_id = 'cradlepoint-iot'
device_id = 'Cradlepoint-IOT'
algorithm = 'RS256'
mqtt_hostname = 'mqtt.googleapis.com'
mqtt_port = 8883
ca_certs_name = 'roots.pem'
private_key_file = '/Users/plea/mqtt/rsa_private.pem'

#Google requires certificate based authentication using JSON Web Tokens (JWT) per device.
#This limits surface area of attacks
def create_jwt(project_id, private_key_file, algorithm): 
    token = {
            # The time that the token was issued
            'iat': datetime.datetime.utcnow(),
            # The time the token expires.
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            # Audience field = project_id
            'aud': project_id
    }

    # Read the private key file.
    with open(private_key_file, 'r') as f:
        private_key = f.read()
    return jwt.encode(token, private_key, algorithm=algorithm)


#Typical MQTT callbacks
def error_str(rc):
    return '{}: {}'.format(rc, mqtt.error_string(rc))

def on_connect(unused_client, unused_userdata, unused_flags, rc):
    print('on_connect', error_str(rc))

def on_disconnect(unused_client, unused_userdata, rc):
    print('on_disconnect', error_str(rc))

def on_publish(unused_client, unused_userdata, unused_mid):
    print('on_publish')


def main():
    client = mqtt.Client(
            client_id=('projects/{}/locations/{}/registries/{}/devices/{}'
                       .format(
                               project_id,
                               cloud_region,
                               registry_id,
                               device_id)))   #Google requires this format explicitly

    client.username_pw_set(
            username='unused',  	#Google ignores the user name.
            password=create_jwt( 	#Google needs the JWT for authorization
                    project_id, private_key_file, algorithm))

    # Enable SSL/TLS support.
    client.tls_set(ca_certs=ca_certs_name)
    
    #callback unused in this example:
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect

    # Connect to the Google pub/sub
    client.connect(mqtt_hostname, mqtt_port)

    # Loop
    client.loop_start()

    # Publish to the events or state topic based on the flag.
    sub_topic = 'events'
    mqtt_topic = '/devices/{}/{}'.format(device_id, sub_topic)

    # Publish num_messages mesages to the MQTT bridge once per second.
    
    for i in range(1,10):
        payload = 'Hello World!: {}'.format(i)
        print('Publishing message\'{}\''.format(payload))
        client.publish(mqtt_topic, payload, qos=1)   
      
        time.sleep(1)
        

if __name__ == '__main__':
    main()