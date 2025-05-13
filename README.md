# simpleDemandResponse

Simple Demand Response is a framework for implementing basic DR functionality across a heterogenous aggregation through MQTT.

A simple MQTT based implementation of a demand response system composed of behind-the-meter (BTM) batteries and smart switches.

There are 2 database files:
* Participants
* Data

This project defines the requirements for Simple Demand Response

Upcoming event info is distributed via MQTT
* Easy enrollment

Participant data is shared via an API
* Security
* User Choice

## Demand Response (DR) and Virtual Power Plants (VPP)

### DR Event Actions

#### Automated Curtailment

#### Automated Replacement

#### Automated Shifting

Automated shifting is not currenty available with this project, but it can be easily extended.

#### Manual Performance

### Enrollment

## Hardware

This system relies on a power station, auto transfer switch, smart outlets or smart relays, and power measuring. If a solar panel is connected to the power station, an addition DC power meter is also necessary.

### Battery/ Power Station

Bluetti power stations

### Smart Relays

Shelly

### Additional Sensors

INA219

## Software

### Installation

### Functions


### Optimization
Charging

Discharging

# Prediction

Weather

Baselines

### Communication and Interfaces



### To do

things to handle: events, alerts (fire, hurricane, etc.)
