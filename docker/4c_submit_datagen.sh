#!/bin/bash

HEADER="Content-Type: application/json"

DATA=$( cat << EOF
{
    "name": "iiot-simulated",
    "config": {
      "connector.class": "io.confluent.kafka.connect.datagen.DatagenConnector",
      "producer.interceptor.classes": "io.confluent.monitoring.clients.interceptor.MonitoringProducerInterceptor",
      "tasks.max": "3",
      "key.converter": "org.apache.kafka.connect.storage.StringConverter",
      "value.converter": "org.apache.kafka.connect.json.JsonConverter",
      "kafka.topic": "iiot.simulated",
      "max.interval": "5000",
      "iterations": "10000",
      "schema.string": "{   \"namespace\": \"iiot\",   \"name\": \"IIoT CRM Data\",   \"doc\": \"Defines a hypothetical IIoT CRM Data\",   \"type\": \"record\",   \"fields\": [     {       \"name\": \"crm_sensor_id\",       \"doc\": \"Sensor ID in CRM\",       \"type\": {         \"type\": \"string\",         \"arg.properties\": {\"regex\": \"Sensor[1-9]{0,1}\"}       }     },     {       \"name\": \"crm_sensor_model\",       \"doc\": \"\",       \"type\": {         \"type\": \"int\",         \"arg.properties\": {\"regex\": \"MODEL[1-9]{0,1}\"}       }     },     {       \"name\": \"crm_sensor_make\",       \"doc\": \"Sensor Make\",       \"type\": {         \"type\": \"string\",         \"arg.properties\": {           \"options\": [ \"MAKE_A\", \"MAKE_B\", \"MAKE_C\", \"MAKE_D\"]         }       }     },     {       \"name\": \"crm_sensor_yom\",       \"doc\": \"Sensor Year of Manufacturing\",       \"type\": {         \"type\": \"int\",         \"arg.properties\": {           \"range\": {             \"min\": 2015,             \"max\": 2022           }         }       }     },     {       \"name\": \"crm_sensor_supplier\",       \"doc\": \"Sensor Supplier\",       \"type\": {         \"type\": \"string\",         \"arg.properties\": {           \"options\": [ \"SUPPLIER_A\", \"SUPPLIER_B\", \"SUPPLIER_C\" ]         }       }     }",
      "schema.keyfield": "iiot_id",
      "value.converter.schema.registry.url": "http://schema-registry:8081",
      "key.converter.schema.registry.url": "http://schema-registry:8081"
  }
}
EOF
)

docker-compose exec connect curl -X POST -H "${HEADER}" --data "${DATA}" http://localhost:8083/connectors